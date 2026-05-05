"""Cost metrics: Active Parameters per Token (AP/T) and Tokens/kWh."""
from __future__ import annotations

from dataclasses import dataclass

from evaluation.energy import _MODEL_PARAMS, active_parameters_per_token


@dataclass
class CostMetrics:
    ap_per_token: float     # Active Parameters per Token
    tokens_per_kwh: float   # Throughput efficiency
    cost_usd: float         # Total USD (API pricing or compute estimate)
    cer: float              # Cost-Effectiveness Ratio = accuracy / normalized_cost


def compute_cost_metrics(
    model_id: str,
    total_tokens: int,
    energy_kwh: float,
    cost_usd: float,
    accuracy: float,
) -> CostMetrics:
    ap_t = active_parameters_per_token(model_id, total_tokens)
    tpkwh = (total_tokens / energy_kwh) if energy_kwh > 0 else 0.0
    normalized_cost = cost_usd if cost_usd > 0 else (energy_kwh * 100)
    cer = (accuracy / normalized_cost) if normalized_cost > 0 else 0.0
    return CostMetrics(ap_per_token=ap_t, tokens_per_kwh=tpkwh, cost_usd=cost_usd, cer=cer)
