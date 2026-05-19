from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import boto3
from pydantic_settings import BaseSettings


def _load_repo_env(path: str | Path = ".env") -> None:
    env_path = Path(path)
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
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: str = ""
    gemini_api_key: str = ""
    together_api_key: str = ""
    force_vllm: bool = False
    hf_token: str = ""
    results_dir: str = "results"
    environment: str = "dev"
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_prefix": "THESIS_", "env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


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
