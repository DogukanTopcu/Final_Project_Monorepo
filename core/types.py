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
    confidence: float = 1.0             # 0-1, used by routing arch
    model_id: str = ""
    latency_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0               # estimated API cost
    llm_calls: int = 0                  # 1 if LLM was invoked, else 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentConfig:
    architecture: str              # "routing" | "multi_agent" | "ensemble"
    benchmark: str                 # "mmlu" | "arc" | "hellaswag" | "gsm8k" | "truthfulqa"
    n_samples: int = 100
    slm: str = "phi3-mini"
    llm: str = "gpt-4o-mini"
    # Arch A params
    confidence_threshold: float = 0.7
    # Arch B params
    n_debate_rounds: int = 1
    arbitrator: str = "llm"        # "llm" | "slm"
    # Arch C params
    n_models: int = 3
    voting: str = "majority"       # "majority" | "weighted"
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
        return sum(s.response.latency_ms for s in self.samples) / self.n_total if self.n_total else 0.0

    @property
    def total_cost_usd(self) -> float:
        return sum(s.response.cost_usd for s in self.samples)

    def to_metrics(self) -> dict[str, float]:
        return {
            "accuracy": self.accuracy,
            "llm_call_ratio": self.llm_call_ratio,
            "avg_latency_ms": self.avg_latency_ms,
            "total_cost_usd": self.total_cost_usd,
            "n_total": float(self.n_total),
            "n_correct": float(self.n_correct),
        }
