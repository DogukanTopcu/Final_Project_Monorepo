from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import mlflow
from mlflow.entities import RunStatus


class MLflowTracker:
    def __init__(
        self,
        experiment_name: str,
        tracking_uri: str | None = None,
    ) -> None:
        self._tracking_uri = tracking_uri or os.getenv(
            "MLFLOW_TRACKING_URI", "http://localhost:5000"
        )
        mlflow.set_tracking_uri(self._tracking_uri)
        mlflow.set_experiment(experiment_name)
        self._run: mlflow.ActiveRun | None = None
        self._sample_idx: int = 0

    @property
    def run_id(self) -> str | None:
        if self._run is None:
            return None
        return self._run.info.run_id

    def start_run(self, run_name: str, config: dict[str, Any]) -> str:
        self._run = mlflow.start_run(run_name=run_name)
        flat = self._flatten(config)
        for key, value in flat.items():
            mlflow.log_param(key, value)
        self._sample_idx = 0
        return self._run.info.run_id

    def log_sample(
        self,
        sample_id: str,
        prediction: str,
        correct: bool,
        response: Any,
    ) -> None:
        mlflow.log_metric("sample_correct", int(correct), step=self._sample_idx)
        if hasattr(response, "latency"):
            mlflow.log_metric("sample_latency", response.latency, step=self._sample_idx)
        if hasattr(response, "cost"):
            mlflow.log_metric("sample_cost", response.cost, step=self._sample_idx)
        self._sample_idx += 1

    def log_final_metrics(self, metrics: dict[str, float]) -> None:
        for name, value in metrics.items():
            mlflow.log_metric(name, value)

    def log_artifacts(self, results_dir: Path) -> None:
        mlflow.log_artifacts(str(results_dir))

    def end_run(self, status: str = "FINISHED") -> None:
        status_map = {
            "FINISHED": RunStatus.to_string(RunStatus.FINISHED),
            "FAILED": RunStatus.to_string(RunStatus.FAILED),
            "KILLED": RunStatus.to_string(RunStatus.KILLED),
        }
        mlflow.end_run(status=status_map.get(status, status))
        self._run = None

    @staticmethod
    def _flatten(d: dict, parent_key: str = "", sep: str = ".") -> dict[str, str]:
        items: list[tuple[str, str]] = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(MLflowTracker._flatten(v, new_key, sep).items())
            else:
                items.append((new_key, str(v)))
        return dict(items)
