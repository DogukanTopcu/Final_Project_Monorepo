from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ExperimentResult:
    experiment_id: str
    architecture: str
    benchmark: str
    metrics: dict[str, float]
    samples_processed: int
    status: str


@dataclass
class RunnerCallbacks:
    on_sample_complete: Callable[[int, int, Any], None] | None = None
    on_metric_update: Callable[[str, float], None] | None = None
    on_experiment_done: Callable[[ExperimentResult], None] | None = None
    on_error: Callable[[Exception], None] | None = None

    def sample_complete(self, current: int, total: int, response: Any) -> None:
        if self.on_sample_complete is not None:
            self.on_sample_complete(current, total, response)

    def metric_update(self, name: str, value: float) -> None:
        if self.on_metric_update is not None:
            self.on_metric_update(name, value)

    def experiment_done(self, result: ExperimentResult) -> None:
        if self.on_experiment_done is not None:
            self.on_experiment_done(result)

    def error(self, exc: Exception) -> None:
        if self.on_error is not None:
            self.on_error(exc)
