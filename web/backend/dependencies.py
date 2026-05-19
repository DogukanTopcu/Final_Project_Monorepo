from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import boto3
from pydantic_settings import BaseSettings


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_repo_env(path: str | Path | None = None) -> None:
    env_path = Path(path) if path is not None else REPO_ROOT / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_repo_env()


class Settings(BaseSettings):
    aws_region: str = "eu-central-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    s3_results_bucket: str = "thesis-results-dev"
    s3_artifacts_bucket: str = "thesis-artifacts-dev"
    dynamodb_table: str = "thesis-experiments"
    mlflow_tracking_uri: str = "http://localhost:5000"
    openai_api_key: str = ""
    gemini_api_key: str = ""
    together_api_key: str = ""
    hf_token: str = ""
    rtx6000_autoswitch_enabled: bool = True
    rtx6000_instance_name: str = "dogukan-topcu-rtx6000-spot"
    rtx6000_project: str = "hubx-ml-playground"
    rtx6000_zone: str = "europe-west2-c"
    rtx6000_switch_script: str = "~/run-mid-llm.sh"
    rtx6000_switch_command_timeout_s: int = 180
    rtx6000_switch_poll_timeout_s: int = 1800
    rtx6000_lock_timeout_s: int = 21600
    rtx6000_poll_interval_s: int = 5
    results_dir: str = str(REPO_ROOT / "results")
    environment: str = "dev"
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_prefix": "THESIS_", "env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    results_path = Path(settings.results_dir)
    if not results_path.is_absolute():
        settings.results_dir = str((REPO_ROOT / results_path).resolve())
    return settings


def get_s3_client():
    settings = get_settings()
    kwargs = {"region_name": settings.aws_region}
    if settings.aws_access_key_id:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
    return boto3.client("s3", **kwargs)


def get_ec2_client():
    settings = get_settings()
    kwargs = {"region_name": settings.aws_region}
    if settings.aws_access_key_id:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
    return boto3.client("ec2", **kwargs)


def get_dynamodb_resource():
    settings = get_settings()
    kwargs = {"region_name": settings.aws_region}
    if settings.aws_access_key_id:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
    return boto3.resource("dynamodb", **kwargs)


def get_ce_client():
    settings = get_settings()
    kwargs = {"region_name": "us-east-1"}
    if settings.aws_access_key_id:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
    return boto3.client("ce", **kwargs)
