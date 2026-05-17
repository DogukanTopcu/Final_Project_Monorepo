"""
Evaluation metrics.

EATS — Efficiency-Accuracy Trade-off Score
==========================================
Defined to fill the gap identified in SLR RQ2:
  "cost and energy remain far less reported than accuracy"

Formula:
    EATS = accuracy / (llm_call_ratio * normalized_cost + epsilon)

Where:
    - accuracy        : fraction of correct answers
    - llm_call_ratio  : fraction of samples that triggered an LLM call
                        (0.0 = fully local, 1.0 = always LLM)
    - normalized_cost : total_cost_usd / cost_usd_full_llm_baseline
                        (1.0 = same cost as running all samples on LLM)
    - epsilon         : small constant to avoid division by zero (default 0.01)

Interpretation: Higher EATS is better. A system with 0.75 accuracy that only
calls the LLM 10% of the time scores much higher than one with 0.80 accuracy
that always uses the LLM.

Special case: if llm_call_ratio == 0 (pure SLM), EATS = accuracy / epsilon
so pure SLM is rewarded heavily for not using any LLM budget.
"""
from __future__ import annotations

from core.types import ExperimentResult


def compute_eats(
    accuracy: float,
    llm_call_ratio: float,
    normalized_cost: float = 1.0,
    epsilon: float = 0.01,
) -> float:
    denom = llm_call_ratio * normalized_cost + epsilon
    return accuracy / denom


def compute_metrics(
    result: ExperimentResult,
    full_llm_cost_usd: float | None = None,
) -> dict[str, float]:
    """
    Compute all metrics from an ExperimentResult.
    full_llm_cost_usd: cost of running the same n_samples entirely through LLM.
                       Used to normalize cost for EATS. If None, normalized_cost=1.
    """
    base = result.to_metrics()

    # Normalized cost
    if full_llm_cost_usd and full_llm_cost_usd > 0:
        normalized_cost = base["total_cost_usd"] / full_llm_cost_usd
    else:
        normalized_cost = 1.0

    eats = compute_eats(
        accuracy=base["accuracy"],
        llm_call_ratio=base["llm_call_ratio"],
        normalized_cost=normalized_cost,
    )

    # Per-sample averages
    latencies = [s.response.latency_ms for s in result.samples]
    p50 = sorted(latencies)[len(latencies) // 2] if latencies else 0.0
    p95_idx = int(len(latencies) * 0.95)
    p95 = sorted(latencies)[min(p95_idx, len(latencies) - 1)] if latencies else 0.0
    confidences = [
        float(s.response.metadata.get("slm_confidence", s.response.confidence))
        for s in result.samples
    ]
    escalated_samples = [
        s for s in result.samples if bool(s.response.metadata.get("escalated", s.response.llm_calls))
    ]
    non_escalated_samples = [
        s for s in result.samples if not bool(s.response.metadata.get("escalated", s.response.llm_calls))
    ]
    escalated_confidences = [
        float(s.response.metadata.get("slm_confidence", s.response.confidence))
        for s in escalated_samples
    ]
    non_escalated_confidences = [
        float(s.response.metadata.get("slm_confidence", s.response.confidence))
        for s in non_escalated_samples
    ]
    n_escalated = len(escalated_samples)
    n_total = int(base["n_total"])
    escalation_rate = n_escalated / n_total if n_total else 0.0

    return {
        **base,
        "eats_score": eats,
        "normalized_cost": normalized_cost,
        "latency_p50_ms": p50,
        "latency_p95_ms": p95,
        "total_tokens": base["n_total"] and sum(
            s.response.input_tokens + s.response.output_tokens for s in result.samples
        ),
        "n_escalated": float(n_escalated),
        "escalation_rate": escalation_rate,
        "n_slm_only": float(n_total - n_escalated),
        "n_llm_final": float(n_escalated),
        "avg_slm_confidence": (
            sum(confidences) / len(confidences) if confidences else 0.0
        ),
        "avg_confidence_escalated": (
            sum(escalated_confidences) / len(escalated_confidences)
            if escalated_confidences
            else 0.0
        ),
        "avg_confidence_non_escalated": (
            sum(non_escalated_confidences) / len(non_escalated_confidences)
            if non_escalated_confidences
            else 0.0
        ),
    }
