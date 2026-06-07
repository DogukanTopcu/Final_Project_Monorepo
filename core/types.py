from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Query:
    id: str
    text: str
    choices: list[str] | None = None   # for MCQ benchmarks
    answer: str | None = None           # ground truth label / text
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Response:
    query_id: str
    text: str                           # raw model output
    predicted_answer: str | None = None # parsed answer (A/B/C/D or text)
    confidence: float | None = 1.0      # 0-1, used by routing arch
    model_id: str = ""
    latency_ms: float = 0.0             # observed end-to-end latency
    algorithmic_latency_ms: float = 0.0 # intrinsic inference + orchestration latency
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0               # total estimated cost (API + infra)
    api_cost_usd: float = 0.0           # direct provider/API cost
    infra_cost_usd: float = 0.0         # self-hosted infra estimate
    energy_kwh: float = 0.0             # estimated or measured energy
    co2_g: float = 0.0                  # estimated or measured emissions
    gpu_power_w: float = 0.0            # average estimated/measured GPU power
    llm_calls: int = 0                  # 1 if LLM was invoked, else 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentConfig:
    architecture: str              # "monolithic" | "routing" | "multi_agent" | "ensemble" | "active_oracle" | "speculative" | "blackboard" | "entropy_blackboard" | "pure_swarm" | "dynamic_bidding"
    benchmark: str                 # "mmlu" | "arc" | "hellaswag" | "gsm8k" | "truthfulqa"
    n_samples: int = 100
    slm: str | None = "qwen3.5-4b"  # may be None for monolithic
    secondary_slm: str | None = None  # required for blackboard variants
    llm: str | None = "llama3.3-70b"  # may be None when not needed
    ensemble_slms: list[str] = field(default_factory=list)  # multi-SLM ensemble selections
    slm_temperature: float = 0.0
    llm_temperature: float = 0.0
    slm_max_tokens: int = 0
    llm_max_tokens: int = 0
    slm_only: bool = False
    # Arch A params
    confidence_threshold: float = 0.7
    margin_threshold: float | None = None
    long_input_token_threshold: int | None = None
    force_escalate: bool = False
    confidence_method: str = "existing_model_confidence"
    # Arch B params
    n_debate_rounds: int = 1
    arbitrator: str = "llm"        # "llm" | "slm"
    # Arch C params
    n_models: int = 3
    voting: str = "majority"       # "majority" | "weighted"
    llm_tiebreak: bool = False
    # Active oracle params
    max_oracle_calls: int = 3
    # Speculative params
    speculative_acceptance_threshold: float = 0.7
    speculative_max_draft_tokens: int = 64
    cost_weight: float = 0.15
    bid_threshold: float = 0.65
    initial_bid_threshold: float = 0.95
    min_bid_threshold: float = 0.0
    ttl_ms: int = 1500
    max_subtasks: int = 2
    allow_nested_subtasks: bool = False
    entropy_weight: float = 0.5  # entropy blackboard: bid penalty per unit normalized entropy
    entropy_top_k: int = 20  # entropy blackboard: top-k logprob distribution width
    # Runtime
    dry_run: bool = False
    seed: int = 42
    output_dir: str = "results"
    mlflow_tracking_uri: str = "http://localhost:5000"
    extra: dict = field(default_factory=dict)


@dataclass
class SampleResult:
    query: Query
    response: Response
    correct: bool


@dataclass
class ExperimentResult:
    experiment_id: str
    config: ExperimentConfig
    samples: list[SampleResult] = field(default_factory=list)

    @property
    def n_total(self) -> int:
        return len(self.samples)

    @property
    def n_correct(self) -> int:
        return sum(1 for s in self.samples if s.correct)

    @property
    def accuracy(self) -> float:
        return self.n_correct / self.n_total if self.n_total else 0.0

    @property
    def llm_call_ratio(self) -> float:
        calls = sum(s.response.llm_calls for s in self.samples)
        return calls / self.n_total if self.n_total else 0.0

    @property
    def avg_latency_ms(self) -> float:
        if not self.n_total:
            return 0.0
        return sum(self._algorithmic_latency_of(s.response) for s in self.samples) / self.n_total

    @property
    def avg_algorithmic_latency_ms(self) -> float:
        if not self.n_total:
            return 0.0
        return sum(self._algorithmic_latency_of(s.response) for s in self.samples) / self.n_total

    @property
    def total_cost_usd(self) -> float:
        return sum(s.response.cost_usd for s in self.samples)

    @property
    def total_api_cost_usd(self) -> float:
        return sum(s.response.api_cost_usd for s in self.samples)

    @property
    def total_infra_cost_usd(self) -> float:
        return sum(s.response.infra_cost_usd for s in self.samples)

    @property
    def total_energy_kwh(self) -> float:
        return sum(s.response.energy_kwh for s in self.samples)

    @property
    def total_co2_g(self) -> float:
        return sum(s.response.co2_g for s in self.samples)

    @staticmethod
    def _algorithmic_latency_of(response: Response) -> float:
        if response.algorithmic_latency_ms > 0:
            return response.algorithmic_latency_ms
        metadata_latency = response.metadata.get("algorithmic_latency_ms")
        if isinstance(metadata_latency, (int, float)) and metadata_latency > 0:
            return float(metadata_latency)
        model_latency = response.metadata.get("model_latency_ms")
        if isinstance(model_latency, (int, float)) and model_latency > 0:
            return float(model_latency)
        server_latency = response.metadata.get("latency_ms_server")
        if isinstance(server_latency, (int, float)) and server_latency > 0:
            return float(server_latency)
        steps = response.metadata.get("inference_steps")
        if isinstance(steps, list):
            total = 0.0
            found = False
            for step in steps:
                if isinstance(step, dict):
                    latency = step.get("latency_ms")
                    if isinstance(latency, (int, float)):
                        total += float(latency)
                        found = True
            if found:
                return total
        return response.latency_ms

    def to_metrics(self) -> dict[str, float]:
        return {
            "accuracy": self.accuracy,
            "llm_call_ratio": self.llm_call_ratio,
            "avg_latency_ms": self.avg_latency_ms,
            "avg_algorithmic_latency_ms": self.avg_algorithmic_latency_ms,
            "total_cost_usd": self.total_cost_usd,
            "total_api_cost_usd": self.total_api_cost_usd,
            "total_infra_cost_usd": self.total_infra_cost_usd,
            "total_energy_kwh": self.total_energy_kwh,
            "total_co2_g": self.total_co2_g,
            "n_total": float(self.n_total),
            "n_correct": float(self.n_correct),
        }
