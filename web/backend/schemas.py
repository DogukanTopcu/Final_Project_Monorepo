from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Architecture(str, Enum):
    MONOLITHIC = "monolithic"
    ROUTING = "routing"
    MULTI_AGENT = "multi_agent"
    ENSEMBLE = "ensemble"
    MULTI_AGENT_CREW = "multi_agent_crew"
    SPECULATIVE = "speculative"
    BLACKBOARD = "blackboard"
    ENTROPY_BLACKBOARD = "entropy_blackboard"
    PURE_SWARM = "pure_swarm"


class ArchitectureMode(str, Enum):
    MONOLITHIC = "monolithic"
    HYBRID = "hybrid"
    ENSEMBLE = "ensemble"
    SWARM = "swarm"


class Benchmark(str, Enum):
    MMLU = "mmlu"
    ARC = "arc"
    HELLASWAG = "hellaswag"
    GSM8K = "gsm8k"
    TRUTHFULQA = "truthfulqa"
    CUSTOM_STRATIFIED = "custom_stratified"


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
    slm: str | None = None
    secondary_slm: str | None = None
    llm: str | None = None
    ensemble_slms: list[str] = Field(default_factory=list)
    config_overrides: dict[str, Any] = Field(default_factory=dict)


class ExperimentResponse(BaseModel):
    experiment_id: str
    status: ExperimentStatus
    architecture: Architecture
    benchmark: Benchmark
    n_samples: int
    slm: str | None = None
    secondary_slm: str | None = None
    llm: str | None = None
    ensemble_slms: list[str] = Field(default_factory=list)
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
    family: str
    tier: str
    provider: str
    runtime_provider: str
    type: str  # "slm" or "llm"
    configured: bool = False
    status: str = "unknown"
    base_url: str | None = None
    reason: str | None = None
    host_id: str | None = None
    host_label: str | None = None
    is_active_on_host: bool | None = None
    shared_host: bool = False


class ModelListResponse(BaseModel):
    slm: list[ModelInfo]
    llm: list[ModelInfo]
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
    slm: str | None = None
    llm: str | None = None
    ensemble_slms: list[str] = Field(default_factory=list)
    accuracy: float
    avg_latency_ms: float | None = None
    eats_score: float | None = None
    llm_call_ratio: float | None = None
    total_cost_usd: float | None = None
    total_energy_kwh: float | None = None
    total_infra_cost_usd: float | None = None
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


# ---------------------------------------------------------------------------
# New schemas: architectures, hosts, playground
# ---------------------------------------------------------------------------


class ArchitectureParamSpec(BaseModel):
    key: str
    label: str
    type: str  # "float" | "int" | "bool" | "enum" | "string"
    default: Any = None
    min: float | None = None
    max: float | None = None
    options: list[str] | None = None
    description: str | None = None


class ArchitectureSpec(BaseModel):
    id: Architecture
    name: str
    mode: ArchitectureMode
    description: str
    requires_slm: bool
    requires_llm: bool
    supports_multi_slm: bool = False
    requires_secondary_slm: bool = False
    experimental: bool = False
    params: list[ArchitectureParamSpec] = Field(default_factory=list)


class HostStatus(BaseModel):
    host_id: str
    label: str
    base_url: str | None = None
    shared: bool
    configured_models: list[str]
    active_model_id: str | None = None
    active_served_ids: list[str] = Field(default_factory=list)
    is_reachable: bool = False
    locked: bool = False
    lock_holder: str | None = None
    last_probe_latency_ms: float | None = None
    notes: str | None = None


class HostsResponse(BaseModel):
    hosts: list[HostStatus]
    autoswitch_enabled: bool = False


class PlaygroundChatRequest(BaseModel):
    model_id: str
    prompt: str
    system: str | None = None
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=512, ge=1, le=32768)


class PlaygroundChatResponse(BaseModel):
    model_id: str
    text: str
    latency_ms: float
    model_latency_ms: float | None = None
    completed_at: datetime | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    effective_max_tokens: int = 0
    cost_usd: float = 0.0
    energy_kwh: float = 0.0
    co2_g: float = 0.0
    gpu_power_w: float = 0.0
    infra_cost_usd: float = 0.0
    base_url: str | None = None
    finish_reason: str = "unknown"
