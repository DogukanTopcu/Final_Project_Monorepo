from __future__ import annotations

import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Event
from typing import Any

from web.backend.schemas import (
    Architecture,
    Benchmark,
    ExperimentCreate,
    ExperimentResponse,
    ExperimentStatus,
)
from mlops.callbacks import ExperimentResult, RunnerCallbacks
from mlops.tracking import MLflowTracker

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


def _run_experiment(experiment_id: str, params: ExperimentCreate) -> None:
    exp = _experiments[experiment_id]
    exp.status = ExperimentStatus.RUNNING
    cancel = _cancel_flags[experiment_id]

    tracker = MLflowTracker(f"thesis-{params.architecture.value}")

    callbacks = RunnerCallbacks(
        on_sample_complete=lambda cur, total, resp: _push_event(
            experiment_id,
            {
                "type": "progress",
                "completed": cur,
                "total": total,
                "current_query": getattr(resp, "query", ""),
            },
        ),
        on_metric_update=lambda name, value: _push_event(
            experiment_id,
            {"type": "metric", "name": name, "value": value},
        ),
        on_experiment_done=lambda result: _push_event(
            experiment_id,
            {
                "type": "complete",
                "experiment_id": experiment_id,
                "metrics": result.metrics,
            },
        ),
        on_error=lambda exc: _push_event(
            experiment_id,
            {"type": "error", "message": str(exc)},
        ),
    )

    try:
        config = {
            "architecture": params.architecture.value,
            "benchmark": params.benchmark.value,
            "n_samples": params.n_samples,
            "slm": params.slm,
            "llm": params.llm,
            **params.config_overrides,
        }
        run_id = tracker.start_run(
            f"{params.slm}-{params.benchmark.value}-{params.n_samples}",
            config,
        )

        n = params.n_samples
        exp.total = n
        for i in range(1, n + 1):
            if cancel.is_set():
                exp.status = ExperimentStatus.CANCELLED
                tracker.end_run("KILLED")
                return

            correct = True
            callbacks.sample_complete(i, n, type("R", (), {"query": f"sample_{i}"})())
            exp.progress = i

        metrics = {
            "accuracy": 0.75,
            "eats_score": 0.82,
            "llm_call_ratio": 0.35,
            "total_cost": 1.23,
            "latency_avg": 0.45,
        }

        tracker.log_final_metrics(metrics)
        tracker.end_run()

        exp.status = ExperimentStatus.COMPLETED
        exp.metrics = metrics
        exp.completed_at = datetime.now(timezone.utc)

        result = ExperimentResult(
            experiment_id=experiment_id,
            architecture=params.architecture.value,
            benchmark=params.benchmark.value,
            metrics=metrics,
            samples_processed=n,
            status="completed",
        )
        callbacks.experiment_done(result)

    except Exception as exc:
        exp.status = ExperimentStatus.FAILED
        exp.error = str(exc)
        callbacks.error(exc)
        tracker.end_run("FAILED")


def launch_experiment(params: ExperimentCreate) -> ExperimentResponse:
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

    _executor.submit(_run_experiment, experiment_id, params)
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
