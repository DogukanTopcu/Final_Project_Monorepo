from __future__ import annotations

import json
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
from datetime import UTC, datetime
from pathlib import Path
from threading import Event
from typing import Any

from core.model_catalog import get_model_spec
from core.models import get_model_runtime_status
from core.types import ExperimentConfig
from evaluation.metrics import compute_metrics
from experiments.runner import (
    ExperimentCancelledError,
    ExperimentRunner,
    resolve_recommended_baseline,
)
from mlops.callbacks import RunnerCallbacks
from web.backend.dependencies import Settings, get_settings
from web.backend.schemas import (
    Architecture,
    Benchmark,
    ExperimentCreate,
    ExperimentResponse,
    ExperimentStatus,
)
from web.backend.services.model_host_service import reserve_llm_host

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
        ensemble_slms_raw = config.get("ensemble_slms") or []
        if isinstance(ensemble_slms_raw, list):
            ensemble_slms = [str(x) for x in ensemble_slms_raw]
        else:
            ensemble_slms = []
        return ExperimentResponse(
            experiment_id=experiment_id,
            status=ExperimentStatus.COMPLETED,
            architecture=Architecture(architecture),
            benchmark=Benchmark(benchmark),
            n_samples=int(config.get("n_samples", 0)),
            slm=str(config.get("slm") or "") or None,
            secondary_slm=str(config.get("secondary_slm") or "") or None,
            llm=str(config.get("llm") or "") or None,
            ensemble_slms=ensemble_slms,
            config_overrides=config,
            created_at=datetime.fromisoformat(
                data.get("created_at", datetime.now(UTC).isoformat())
            ),
            completed_at=datetime.fromisoformat(
                data.get("created_at", datetime.now(UTC).isoformat())
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
        "max_oracle_calls",
        "n_models",
        "voting",
        "llm_tiebreak",
        "seed",
        "slm_temperature",
        "llm_temperature",
        "slm_max_tokens",
        "llm_max_tokens",
        "speculative_acceptance_threshold",
        "cost_weight",
        "bid_threshold",
        "ttl_ms",
        "slm_url",
        "max_subtasks",
        "allow_nested_subtasks",
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

    ensemble_slms = list(params.ensemble_slms or [])
    # Default n_models to the explicit ensemble count when a list is provided.
    default_n_models = len(ensemble_slms) if ensemble_slms else 3
    n_models = int(overrides.get("n_models", default_n_models))

    return ExperimentConfig(
        architecture=params.architecture.value,
        benchmark=params.benchmark.value,
        n_samples=params.n_samples,
        slm=params.slm,
        secondary_slm=params.secondary_slm,
        llm=params.llm,
        ensemble_slms=ensemble_slms,
        slm_temperature=slm_temperature,
        llm_temperature=llm_temperature,
        slm_max_tokens=slm_max_tokens,
        llm_max_tokens=llm_max_tokens,
        slm_only=bool(overrides.get("slm_only", False)),
        confidence_threshold=float(overrides.get("confidence_threshold", 0.7)),
        arbitrator=str(overrides.get("arbitrator", "llm")),
        n_debate_rounds=int(overrides.get("n_debate_rounds", 1)),
        max_oracle_calls=int(overrides.get("max_oracle_calls", 3)),
        n_models=n_models,
        voting=str(overrides.get("voting", "majority")),
        llm_tiebreak=bool(overrides.get("llm_tiebreak", False)),
        slm_url=str(overrides.get("slm_url", "auto")),
        speculative_acceptance_threshold=float(
            overrides.get("speculative_acceptance_threshold", 0.7)
        ),
        cost_weight=float(overrides.get("cost_weight", 0.15)),
        bid_threshold=float(overrides.get("bid_threshold", 0.65)),
        ttl_ms=int(overrides.get("ttl_ms", 1500)),
        max_subtasks=int(overrides.get("max_subtasks", 2)),
        allow_nested_subtasks=bool(overrides.get("allow_nested_subtasks", False)),
        dry_run=bool(overrides.get("dry_run", False)),
        seed=int(overrides.get("seed", 42)),
        output_dir=settings.results_dir,
        mlflow_tracking_uri=settings.mlflow_tracking_uri,
    )


def _sync_runtime_provider_env(settings: Settings) -> None:
    """Expose provider keys/base URLs to runtime code that reads os.environ."""
    env_map = {
        "THESIS_OPENAI_API_KEY": settings.openai_api_key,
        "OPENAI_API_KEY": settings.openai_api_key,
        "THESIS_GEMINI_API_KEY": settings.gemini_api_key,
        "GEMINI_API_KEY": settings.gemini_api_key,
        "THESIS_TOGETHER_API_KEY": settings.together_api_key,
        "TOGETHER_API_KEY": settings.together_api_key,
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
        # Identify the single shared-host model this experiment needs (if any).
        # Only one model on a shared host is allowed per run; we pick the LLM
        # for monolithic/hybrid and the heaviest SLM/tiebreaker for ensemble.
        primary_shared_model = None
        if not config.dry_run:
            candidates: list[str] = []
            if params.architecture.value == "ensemble":
                if params.llm and (params.config_overrides or {}).get("llm_tiebreak"):
                    candidates.append(params.llm)
                candidates.extend(params.ensemble_slms or [])
                if params.slm and not params.ensemble_slms:
                    candidates.append(params.slm)
            elif params.architecture.value in {"blackboard", "entropy_blackboard", "pure_swarm"}:
                if params.llm:
                    candidates.append(params.llm)
                if params.slm:
                    candidates.append(params.slm)
                if params.secondary_slm:
                    candidates.append(params.secondary_slm)
            else:
                if params.llm:
                    candidates.append(params.llm)
                if params.slm:
                    candidates.append(params.slm)
            from core.hosts import get_host_for_model
            for mid in candidates:
                host = get_host_for_model(mid)
                if host and host.shared:
                    primary_shared_model = mid
                    break

        reservation = (
            reserve_llm_host(
                primary_shared_model,
                settings,
                on_status=lambda message, status: _push_event(
                    experiment_id,
                    {"type": "status", "status": status, "message": message},
                ),
            )
            if primary_shared_model
            else nullcontext()
        )
        with reservation:
            runner = ExperimentRunner(config, callbacks=callbacks)
            runner.experiment_id = experiment_id
            result = runner.run()
            baseline_metrics = resolve_recommended_baseline(config.benchmark)
            metrics = compute_metrics(
                result,
                full_llm_cost_usd=baseline_metrics.get("total_cost_usd"),
                full_llm_avg_algorithmic_latency_ms=baseline_metrics.get("avg_algorithmic_latency_ms"),
                full_llm_energy_kwh=baseline_metrics.get("total_energy_kwh"),
            )

        exp.status = ExperimentStatus.COMPLETED
        exp.metrics = metrics
        exp.completed_at = datetime.now(UTC)
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
        exp.completed_at = datetime.now(UTC)
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
        exp.completed_at = datetime.now(UTC)
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


def _validate_architecture_models(params: ExperimentCreate, *, require_runtime: bool) -> None:
    arch = params.architecture.value
    if arch == "monolithic":
        if not params.llm:
            raise ValueError("Monolithic architecture requires an LLM selection.")
        _validate_model_selection(params.llm, "llm", require_runtime=require_runtime)
        return

    if arch == "ensemble":
        ids = params.ensemble_slms or ([params.slm] if params.slm else [])
        if not ids:
            raise ValueError("Ensemble requires at least one SLM.")
        for sid in ids:
            _validate_model_selection(sid, "slm", require_runtime=require_runtime)
        # Tiebreak LLM is optional
        if params.llm and (params.config_overrides or {}).get("llm_tiebreak"):
            _validate_model_selection(params.llm, "llm", require_runtime=require_runtime)
        return

    if arch == "blackboard":
        if not params.slm:
            raise ValueError("Blackboard requires a Primary SLM selection.")
        if not params.secondary_slm:
            raise ValueError("Blackboard requires a Secondary SLM selection.")
        if not params.llm:
            raise ValueError("Blackboard requires an LLM sweeper selection.")
        _validate_model_selection(params.slm, "slm", require_runtime=require_runtime)
        _validate_model_selection(params.secondary_slm, "slm", require_runtime=require_runtime)
        _validate_model_selection(params.llm, "llm", require_runtime=require_runtime)
        return

    if arch == "entropy_blackboard":
        if not params.slm:
            raise ValueError("Entropy Blackboard requires a Primary SLM selection.")
        if not params.secondary_slm:
            raise ValueError("Entropy Blackboard requires a Secondary SLM selection.")
        if not params.llm:
            raise ValueError("Entropy Blackboard requires an LLM sweeper selection.")
        _validate_model_selection(params.slm, "slm", require_runtime=require_runtime)
        _validate_model_selection(params.secondary_slm, "slm", require_runtime=require_runtime)
        _validate_model_selection(params.llm, "llm", require_runtime=require_runtime)
        return

    if arch == "pure_swarm":
        if not params.slm:
            raise ValueError("Pure Swarm requires a Primary SLM selection.")
        if not params.secondary_slm:
            raise ValueError("Pure Swarm requires a Secondary SLM selection.")
        _validate_model_selection(params.slm, "slm", require_runtime=require_runtime)
        _validate_model_selection(params.secondary_slm, "slm", require_runtime=require_runtime)
        return

    # routing / multi_agent / multi_agent_crew / speculative — need both
    if not params.slm or not params.llm:
        raise ValueError(f"{arch} requires both an SLM and an LLM selection.")
    _validate_model_selection(params.slm, "slm", require_runtime=require_runtime)
    _validate_model_selection(params.llm, "llm", require_runtime=require_runtime)


def launch_experiment(params: ExperimentCreate, settings: Settings) -> ExperimentResponse:
    config = _build_config(params, settings)
    _validate_architecture_models(params, require_runtime=not config.dry_run)

    experiment_id = f"exp_{uuid.uuid4().hex[:8]}"
    now = datetime.now(UTC)

    exp = ExperimentResponse(
        experiment_id=experiment_id,
        status=ExperimentStatus.QUEUED,
        architecture=params.architecture,
        benchmark=params.benchmark,
        n_samples=params.n_samples,
        slm=params.slm,
        secondary_slm=params.secondary_slm,
        llm=params.llm,
        ensemble_slms=list(params.ensemble_slms or []),
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
