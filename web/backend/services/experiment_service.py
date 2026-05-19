from __future__ import annotations

import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
from datetime import datetime, timezone
import json
from pathlib import Path
from threading import Event
from typing import Any

from core.model_catalog import get_model_spec
from core.models import get_model_runtime_status
from core.types import ExperimentConfig
from evaluation.metrics import compute_metrics
from experiments.runner import ExperimentCancelledError, ExperimentRunner
from mlops.callbacks import RunnerCallbacks
from web.backend.dependencies import Settings, get_settings
from web.backend.services.model_host_service import reserve_llm_host
from web.backend.schemas import (
    Architecture,
    Benchmark,
    ExperimentCreate,
    ExperimentResponse,
    ExperimentStatus,
)

_executor = ThreadPoolExecutor(max_workers=4)

_experiments: dict[str, ExperimentResponse] = {}
_cancel_flags: dict[str, Event] = {}
_sse_queues: dict[str, list[dict[str, Any]]] = {}


def _build_persisted_experiment_response(path: Path) -> ExperimentResponse | None:
    try:
        data = json.loads(path.read_text())
    except Exception:
        return None

    config = data.get("config", {})
    experiment_id = str(data.get("experiment_id", path.stem))
    architecture = str(config.get("architecture", "routing"))
    benchmark = str(config.get("benchmark", "mmlu"))

    try:
        return ExperimentResponse(
            experiment_id=experiment_id,
            status=ExperimentStatus.COMPLETED,
            architecture=Architecture(architecture),
            benchmark=Benchmark(benchmark),
            n_samples=int(config.get("n_samples", 0)),
            slm=str(config.get("slm", "")),
            llm=str(config.get("llm", "")),
            config_overrides=config,
            created_at=datetime.fromisoformat(
                data.get("created_at", datetime.now(timezone.utc).isoformat())
            ),
            completed_at=datetime.fromisoformat(
                data.get("created_at", datetime.now(timezone.utc).isoformat())
            ),
            metrics=data.get("metrics", {}),
            progress=int(config.get("n_samples", 0)),
            total=int(config.get("n_samples", 0)),
        )
    except Exception:
        return None


def _load_persisted_experiments(settings: Settings) -> dict[str, ExperimentResponse]:
    results_dir = Path(settings.results_dir)
    if not results_dir.exists():
        return {}

    persisted: dict[str, ExperimentResponse] = {}
    for path in sorted(results_dir.glob("*.json")):
        exp = _build_persisted_experiment_response(path)
        if exp is not None:
            persisted[exp.experiment_id] = exp
    return persisted


def _push_event(experiment_id: str, event: dict[str, Any]) -> None:
    if experiment_id not in _sse_queues:
        _sse_queues[experiment_id] = []
    _sse_queues[experiment_id].append(event)


def get_events(experiment_id: str) -> list[dict[str, Any]]:
    return _sse_queues.get(experiment_id, [])


def _build_config(params: ExperimentCreate, settings: Settings) -> ExperimentConfig:
    overrides = params.config_overrides or {}
    allowed_override_keys = {
        "confidence_threshold",
        "dry_run",
        "arbitrator",
        "n_debate_rounds",
        "n_models",
        "voting",
        "llm_tiebreak",
        "seed",
        "slm_temperature",
        "llm_temperature",
        "slm_max_tokens",
        "llm_max_tokens",
        "slm_only",
    }
    unexpected = sorted(set(overrides) - allowed_override_keys)
    if unexpected:
        raise ValueError(f"Unsupported config overrides: {', '.join(unexpected)}")

    slm_temperature = float(overrides.get("slm_temperature", 0.0))
    llm_temperature = float(overrides.get("llm_temperature", 0.0))
    slm_max_tokens = int(overrides.get("slm_max_tokens", 0))
    llm_max_tokens = int(overrides.get("llm_max_tokens", 0))

    if not 0.0 <= slm_temperature <= 2.0:
        raise ValueError("slm_temperature must be between 0.0 and 2.0")
    if not 0.0 <= llm_temperature <= 2.0:
        raise ValueError("llm_temperature must be between 0.0 and 2.0")
    if slm_max_tokens < 0 or slm_max_tokens > 32768:
        raise ValueError("slm_max_tokens must be between 0 and 32768")
    if llm_max_tokens < 0 or llm_max_tokens > 32768:
        raise ValueError("llm_max_tokens must be between 0 and 32768")

    return ExperimentConfig(
        architecture=params.architecture.value,
        benchmark=params.benchmark.value,
        n_samples=params.n_samples,
        slm=params.slm,
        llm=params.llm,
        slm_temperature=slm_temperature,
        llm_temperature=llm_temperature,
        slm_max_tokens=slm_max_tokens,
        llm_max_tokens=llm_max_tokens,
        slm_only=bool(overrides.get("slm_only", False)),
        confidence_threshold=float(overrides.get("confidence_threshold", 0.7)),
        arbitrator=str(overrides.get("arbitrator", "llm")),
        n_debate_rounds=int(overrides.get("n_debate_rounds", 1)),
        n_models=int(overrides.get("n_models", 3)),
        voting=str(overrides.get("voting", "majority")),
        llm_tiebreak=bool(overrides.get("llm_tiebreak", False)),
        dry_run=bool(overrides.get("dry_run", False)),
        seed=int(overrides.get("seed", 42)),
        output_dir=settings.results_dir,
        mlflow_tracking_uri=settings.mlflow_tracking_uri,
    )


def _sync_runtime_provider_env(settings: Settings) -> None:
    """Expose provider keys/base URLs to runtime code that reads os.environ."""
    env_map = {
        "THESIS_OLLAMA_BASE_URL": settings.ollama_base_url,
        "OLLAMA_BASE_URL": settings.ollama_base_url,
        "THESIS_OPENAI_API_KEY": settings.openai_api_key,
        "OPENAI_API_KEY": settings.openai_api_key,
        "THESIS_GEMINI_API_KEY": settings.gemini_api_key,
        "GEMINI_API_KEY": settings.gemini_api_key,
        "THESIS_TOGETHER_API_KEY": settings.together_api_key,
        "TOGETHER_API_KEY": settings.together_api_key,
        "THESIS_FORCE_VLLM": "1" if settings.force_vllm else "",
    }
    for key, value in env_map.items():
        if value:
            os.environ[key] = value


def _run_experiment(
    experiment_id: str,
    params: ExperimentCreate,
    settings: Settings,
) -> None:
    exp = _experiments[experiment_id]
    exp.status = ExperimentStatus.RUNNING
    cancel = _cancel_flags[experiment_id]

    callbacks = RunnerCallbacks(
        on_sample_complete=lambda cur, total, resp: _handle_sample_complete(
            experiment_id, cur, total, resp
        ),
        on_metric_update=lambda name, value: _push_event(
            experiment_id,
            {"type": "metric", "name": name, "value": value},
        ),
        on_error=lambda exc: _push_event(
            experiment_id,
            {"type": "error", "message": str(exc)},
        ),
        should_cancel=cancel.is_set,
    )

    try:
        _sync_runtime_provider_env(settings)
        config = _build_config(params, settings)
        exp.total = config.n_samples
        reservation = (
            reserve_llm_host(
                params.llm,
                settings,
                on_status=lambda message, status: _push_event(
                    experiment_id,
                    {"type": "status", "status": status, "message": message},
                ),
            )
            if not config.dry_run
            else nullcontext()
        )
        with reservation:
            runner = ExperimentRunner(config, callbacks=callbacks)
            runner.experiment_id = experiment_id
            result = runner.run()
            metrics = compute_metrics(result)

        exp.status = ExperimentStatus.COMPLETED
        exp.metrics = metrics
        exp.completed_at = datetime.now(timezone.utc)
        exp.progress = exp.total

        _push_event(
            experiment_id,
            {
                "type": "complete",
                "experiment_id": experiment_id,
                "metrics": metrics,
                "status": ExperimentStatus.COMPLETED.value,
            },
        )
    except ExperimentCancelledError:
        exp.status = ExperimentStatus.CANCELLED
        exp.completed_at = datetime.now(timezone.utc)
        _push_event(
            experiment_id,
            {
                "type": "complete",
                "experiment_id": experiment_id,
                "status": ExperimentStatus.CANCELLED.value,
            },
        )
    except Exception as exc:
        exp.status = ExperimentStatus.FAILED
        exp.error = str(exc)
        exp.completed_at = datetime.now(timezone.utc)
        callbacks.error(exc)
        _push_event(
            experiment_id,
            {
                "type": "complete",
                "experiment_id": experiment_id,
                "status": ExperimentStatus.FAILED.value,
            },
        )


def _handle_sample_complete(
    experiment_id: str,
    current: int,
    total: int,
    response: Any,
) -> None:
    exp = _experiments[experiment_id]
    exp.progress = current
    exp.total = total
    _push_event(
        experiment_id,
        {
            "type": "progress",
            "completed": current,
            "total": total,
            "current_query": getattr(response, "query_id", ""),
        },
    )


def _validate_model_selection(model_id: str, expected_kind: str, *, require_runtime: bool) -> None:
    spec = get_model_spec(model_id)
    if spec is None:
        raise ValueError(f"Unknown model alias: {model_id}")
    if spec.kind != expected_kind:
        raise ValueError(f"{model_id} is not a valid {expected_kind.upper()} selection.")

    if not require_runtime:
        return

    status = get_model_runtime_status(model_id)
    if not bool(status.get("available")):
        raise ValueError(str(status.get("reason", f"{model_id} is unavailable.")))


def launch_experiment(params: ExperimentCreate, settings: Settings) -> ExperimentResponse:
    config = _build_config(params, settings)
    _validate_model_selection(params.slm, "slm", require_runtime=not config.dry_run)
    llm_required = not (config.architecture == "routing" and config.slm_only)
    _validate_model_selection(
        params.llm,
        "llm",
        require_runtime=(not config.dry_run and llm_required),
    )

    experiment_id = f"exp_{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc)

    exp = ExperimentResponse(
        experiment_id=experiment_id,
        status=ExperimentStatus.QUEUED,
        architecture=params.architecture,
        benchmark=params.benchmark,
        n_samples=params.n_samples,
        slm=params.slm,
        llm=params.llm,
        config_overrides=params.config_overrides,
        created_at=now,
        total=params.n_samples,
    )
    _experiments[experiment_id] = exp
    _cancel_flags[experiment_id] = Event()
    _sse_queues[experiment_id] = []

    _executor.submit(_run_experiment, experiment_id, params, settings)
    return exp


def get_experiment(experiment_id: str) -> ExperimentResponse | None:
    live = _experiments.get(experiment_id)
    if live is not None:
        return live

    settings = get_settings()
    persisted_path = Path(settings.results_dir) / f"{experiment_id}.json"
    if persisted_path.exists():
        return _build_persisted_experiment_response(persisted_path)
    return None


def list_experiments() -> list[ExperimentResponse]:
    settings = get_settings()
    experiments = _load_persisted_experiments(settings)
    experiments.update(_experiments)
    return sorted(
        experiments.values(),
        key=lambda e: e.created_at,
        reverse=True,
    )


def cancel_experiment(experiment_id: str) -> bool:
    flag = _cancel_flags.get(experiment_id)
    if flag is None:
        return False
    flag.set()
    return True
