from __future__ import annotations

import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Event
from typing import Any

from core.types import ExperimentConfig
from evaluation.metrics import compute_metrics
from experiments.runner import ExperimentCancelledError, ExperimentRunner
from mlops.callbacks import RunnerCallbacks
from web.backend.dependencies import Settings
from web.backend.schemas import (
    Architecture,
    ExperimentCreate,
    ExperimentResponse,
    ExperimentStatus,
)

_executor = ThreadPoolExecutor(max_workers=4)

_experiments: dict[str, ExperimentResponse] = {}
_cancel_flags: dict[str, Event] = {}
_sse_queues: dict[str, list[dict[str, Any]]] = {}


def _push_event(experiment_id: str, event: dict[str, Any]) -> None:
    if experiment_id not in _sse_queues:
        _sse_queues[experiment_id] = []
    _sse_queues[experiment_id].append(event)


def get_events(experiment_id: str) -> list[dict[str, Any]]:
    return _sse_queues.get(experiment_id, [])


def _build_config(params: ExperimentCreate, settings: Settings) -> ExperimentConfig:
    overrides = params.config_overrides or {}
    allowed_override_keys = {"confidence_threshold", "dry_run"}
    unexpected = sorted(set(overrides) - allowed_override_keys)
    if unexpected:
        raise ValueError(
            f"Unsupported config overrides for web routing: {', '.join(unexpected)}"
        )

    return ExperimentConfig(
        architecture=params.architecture.value,
        benchmark=params.benchmark.value,
        n_samples=params.n_samples,
        slm=params.slm,
        llm=params.llm,
        confidence_threshold=float(overrides.get("confidence_threshold", 0.7)),
        dry_run=bool(overrides.get("dry_run", False)),
        output_dir=settings.results_dir,
        mlflow_tracking_uri=settings.mlflow_tracking_uri,
    )


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
        config = _build_config(params, settings)
        exp.total = config.n_samples
        runner = ExperimentRunner(config, callbacks=callbacks)
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


def _llm_provider_is_configured(llm_model_id: str, settings: Settings) -> bool:
    if llm_model_id.startswith("gpt-"):
        return bool(settings.openai_api_key)
    if llm_model_id.startswith("gemini-"):
        return bool(settings.gemini_api_key)
    if llm_model_id in {"llama-3.1-70b", "llama3-70b"}:
        return bool(settings.together_api_key)
    return False


def launch_experiment(params: ExperimentCreate, settings: Settings) -> ExperimentResponse:
    config = _build_config(params, settings)
    if params.architecture is not Architecture.ROUTING:
        raise ValueError("Web launch currently supports routing only.")
    if not config.dry_run and not _llm_provider_is_configured(params.llm, settings):
        raise ValueError(
            f"The selected fallback model `{params.llm}` is not configured. "
            "Set the matching API key in `.env`."
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
    return _experiments.get(experiment_id)


def list_experiments() -> list[ExperimentResponse]:
    return sorted(
        _experiments.values(),
        key=lambda e: e.created_at,
        reverse=True,
    )


def cancel_experiment(experiment_id: str) -> bool:
    flag = _cancel_flags.get(experiment_id)
    if flag is None:
        return False
    flag.set()
    return True
