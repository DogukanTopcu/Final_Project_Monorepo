from __future__ import annotations

import os
from typing import Any

from mlflow.tracking import MlflowClient


def _get_client() -> MlflowClient:
    uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    return MlflowClient(tracking_uri=uri)


def list_experiments() -> list[dict[str, Any]]:
    client = _get_client()
    experiments = client.search_experiments()
    return [
        {
            "experiment_id": exp.experiment_id,
            "name": exp.name,
            "lifecycle_stage": exp.lifecycle_stage,
        }
        for exp in experiments
    ]


def list_runs(experiment_name: str | None = None) -> list[dict[str, Any]]:
    client = _get_client()

    if experiment_name:
        exp = client.get_experiment_by_name(experiment_name)
        if exp is None:
            return []
        filter_string = f"experiment_id = '{exp.experiment_id}'"
    else:
        filter_string = ""

    runs = client.search_runs(
        experiment_ids=[],
        filter_string=filter_string,
        order_by=["start_time DESC"],
        max_results=100,
    )
    return [
        {
            "run_id": run.info.run_id,
            "run_name": run.info.run_name,
            "status": run.info.status,
            "start_time": run.info.start_time,
            "end_time": run.info.end_time,
            "metrics": run.data.metrics,
            "params": run.data.params,
        }
        for run in runs
    ]


def get_run(run_id: str) -> dict[str, Any] | None:
    client = _get_client()
    try:
        run = client.get_run(run_id)
        return {
            "run_id": run.info.run_id,
            "run_name": run.info.run_name,
            "status": run.info.status,
            "start_time": run.info.start_time,
            "end_time": run.info.end_time,
            "metrics": run.data.metrics,
            "params": run.data.params,
            "tags": run.data.tags,
        }
    except Exception:
        return None
