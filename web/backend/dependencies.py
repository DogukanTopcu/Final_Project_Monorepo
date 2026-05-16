from __future__ import annotations

from functools import lru_cache

from google.cloud import bigquery, compute_v1, storage
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project: str = "thesis"
    gcp_project_id: str = "thesis-gcp"
    gcp_region: str = "europe-west4"
    gcp_zone: str = "europe-west4-a"
    gcs_results_bucket: str = "thesis-results-dev"
    gcs_artifacts_bucket: str = "thesis-artifacts-dev"
    firestore_collection: str = "thesis-experiments"
    billing_export_table: str = ""
    mlflow_tracking_uri: str = "http://localhost:5000"
    ollama_base_url: str = "http://localhost:11434"
    environment: str = "dev"
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_prefix": "THESIS_", "env_file": ".env"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_storage_client() -> storage.Client:
    return storage.Client(project=get_settings().gcp_project_id)


def get_instances_client() -> compute_v1.InstancesClient:
    return compute_v1.InstancesClient()


def get_bigquery_client() -> bigquery.Client:
    return bigquery.Client(project=get_settings().gcp_project_id)
