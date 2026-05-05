from __future__ import annotations

import mlflow
from mlflow.tracking import MlflowClient


def register_model(run_id: str, model_name: str, artifact_path: str = "model") -> str:
    client = MlflowClient()
    model_uri = f"runs:/{run_id}/{artifact_path}"
    result = mlflow.register_model(model_uri, model_name)
    return result.version


def promote_model(model_name: str, version: str, stage: str = "Production") -> None:
    client = MlflowClient()
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage=stage,
    )


def get_latest_version(model_name: str, stage: str = "Production") -> str | None:
    client = MlflowClient()
    versions = client.get_latest_versions(model_name, stages=[stage])
    if versions:
        return versions[0].version
    return None
