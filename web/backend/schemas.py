from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Architecture(str, Enum):
    ROUTING = "routing"
    MULTI_AGENT = "multi_agent"
    ENSEMBLE = "ensemble"


class Benchmark(str, Enum):
    MMLU = "mmlu"
    ARC = "arc"
    HELLASWAG = "hellaswag"
    GSM8K = "gsm8k"
    TRUTHFULQA = "truthfulqa"


class ExperimentStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExperimentCreate(BaseModel):
    architecture: Architecture
    benchmark: Benchmark
    n_samples: int = Field(default=100, ge=1, le=10000)
    slm: str = "phi3-mini"
    llm: str = "gpt-4o-mini"
    config_overrides: dict[str, Any] = Field(default_factory=dict)


class ExperimentResponse(BaseModel):
    experiment_id: str
    status: ExperimentStatus
    architecture: Architecture
    benchmark: Benchmark
    n_samples: int
    slm: str
    llm: str
    config_overrides: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    completed_at: datetime | None = None
    metrics: dict[str, float] | None = None
    progress: int = 0
    total: int = 0
    error: str | None = None


class ExperimentLaunchResponse(BaseModel):
    experiment_id: str
    status: ExperimentStatus = ExperimentStatus.QUEUED


class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    type: str  # "slm" or "llm"
    status: str = "unknown"


class ModelListResponse(BaseModel):
    slm: list[ModelInfo]
    llm: list[ModelInfo]
    ollama_reachable: bool = False
    openai_configured: bool = False
    gemini_configured: bool = False
    warnings: list[str] = Field(default_factory=list)


class ModelPingResponse(BaseModel):
    model_id: str
    reachable: bool
    latency_ms: float | None = None


class ResultSummary(BaseModel):
    id: str
    experiment_id: str
    architecture: str
    benchmark: str
    slm: str
    llm: str
    accuracy: float
    avg_latency_ms: float | None = None
    eats_score: float | None = None
    llm_call_ratio: float | None = None
    total_cost_usd: float | None = None
    created_at: datetime


class ResultDetail(BaseModel):
    id: str
    experiment_id: str
    architecture: str
    benchmark: str
    metrics: dict[str, float]
    samples: list[dict[str, Any]] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ComparisonResponse(BaseModel):
    ids: list[str]
    metrics: dict[str, dict[str, float]]


class InstanceInfo(BaseModel):
    instance_id: str
    name: str
    instance_type: str
    state: str
    public_ip: str | None = None
    private_ip: str | None = None
    launch_time: datetime | None = None
    tags: dict[str, str] = Field(default_factory=dict)


class CostEstimate(BaseModel):
    total_monthly: float
    breakdown: dict[str, float]
    currency: str = "USD"


class SSEEvent(BaseModel):
    type: str
    completed: int | None = None
    total: int | None = None
    current_query: str | None = None
    name: str | None = None
    value: float | None = None
    experiment_id: str | None = None
    metrics: dict[str, float] | None = None
    message: str | None = None
    status: str | None = None
