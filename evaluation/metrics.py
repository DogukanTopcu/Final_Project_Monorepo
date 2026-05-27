"""
Evaluation metrics.

EATS — Efficiency-Accuracy Trade-off Score
==========================================
Defined to fill the gap identified in SLR RQ2:
  "cost and energy remain far less reported than accuracy"

Formula:
    efficiency_penalty = (
        normalized_cost^0.5 *
        normalized_algorithmic_latency^0.3 *
        normalized_energy^0.2
    )
    EATS = accuracy^2 / (accuracy^2 + efficiency_penalty)

Where:
    - accuracy        : fraction of correct answers
    - normalized_cost : total_cost_usd / cost_usd_full_llm_baseline
                        (1.0 = same cost as running all samples on LLM)
    - normalized_algorithmic_latency :
                        avg_algorithmic_latency_ms / full_llm_avg_algorithmic_latency_ms
    - normalized_energy  : total_energy_kwh / total_energy_kwh_full_llm_baseline

Interpretation: Higher EATS is better. A system with 0.75 accuracy that only
uses low cost, low algorithmic latency, and low energy will score higher than
one with similar accuracy but heavier resource usage. The score is bounded in
[0, 1].
"""
from __future__ import annotations

from core.types import ExperimentResult


def _normalize_metric(value: float, baseline: float | None) -> float:
    if baseline and baseline > 0:
        return value / baseline
    return 1.0


def compute_eats(
    accuracy: float,
    normalized_cost: float = 1.0,
    normalized_algorithmic_latency: float = 1.0,
    normalized_energy: float = 1.0,
) -> float:
    accuracy_term = max(accuracy, 0.0) ** 2
    efficiency_penalty = (
        (max(normalized_cost, 0.0) ** 0.5) *
        (max(normalized_algorithmic_latency, 0.0) ** 0.3) *
        (max(normalized_energy, 0.0) ** 0.2)
    )
    denom = accuracy_term + efficiency_penalty
    return (accuracy_term / denom) if denom > 0 else 0.0


def compute_metrics(
    result: ExperimentResult,
    full_llm_cost_usd: float | None = None,
    full_llm_avg_algorithmic_latency_ms: float | None = None,
    full_llm_energy_kwh: float | None = None,
) -> dict[str, float]:
    """
    Compute all metrics from an ExperimentResult.
    full_llm_cost_usd: cost of running the same n_samples entirely through LLM.
                       Used to normalize cost for EATS. If None, normalized_cost=1.
    full_llm_avg_algorithmic_latency_ms: average algorithmic latency of
                             running the same n_samples entirely through LLM.
                             Used to normalize latency inside EATS.
    full_llm_energy_kwh: total energy of running the same n_samples entirely
                         through LLM. Used to normalize energy.
    """
    base = result.to_metrics()
    avg_algorithmic_latency_ms = base["avg_algorithmic_latency_ms"]

    normalized_cost = _normalize_metric(base["total_cost_usd"], full_llm_cost_usd)
    normalized_algorithmic_latency = _normalize_metric(
        avg_algorithmic_latency_ms,
        full_llm_avg_algorithmic_latency_ms,
    )
    normalized_energy = _normalize_metric(base["total_energy_kwh"], full_llm_energy_kwh)
    efficiency_penalty = (
        (normalized_cost ** 0.5) *
        (normalized_algorithmic_latency ** 0.3) *
        (normalized_energy ** 0.2)
    )

    eats = compute_eats(
        accuracy=base["accuracy"],
        normalized_cost=normalized_cost,
        normalized_algorithmic_latency=normalized_algorithmic_latency,
        normalized_energy=normalized_energy,
    )

    # Per-sample averages
    latencies = [s.response.latency_ms for s in result.samples]
    p50 = sorted(latencies)[len(latencies) // 2] if latencies else 0.0
    p95_idx = int(len(latencies) * 0.95)
    p95 = sorted(latencies)[min(p95_idx, len(latencies) - 1)] if latencies else 0.0
    confidences = [
        float(conf)
        for s in result.samples
        for conf in [s.response.metadata.get("slm_confidence", s.response.confidence)]
        if conf is not None
    ]
    escalated_samples = [
        s for s in result.samples if bool(s.response.metadata.get("escalated", s.response.llm_calls))
    ]
    non_escalated_samples = [
        s for s in result.samples if not bool(s.response.metadata.get("escalated", s.response.llm_calls))
    ]
    escalated_confidences = [
        float(conf)
        for s in escalated_samples
        for conf in [s.response.metadata.get("slm_confidence", s.response.confidence)]
        if conf is not None
    ]
    non_escalated_confidences = [
        float(conf)
        for s in non_escalated_samples
        for conf in [s.response.metadata.get("slm_confidence", s.response.confidence)]
        if conf is not None
    ]
    n_escalated = len(escalated_samples)
    n_total = int(base["n_total"])
    escalation_rate = n_escalated / n_total if n_total else 0.0

    return {
        **base,
        "eats_score": eats,
        "normalized_cost": normalized_cost,
        "normalized_algorithmic_latency": normalized_algorithmic_latency,
        "normalized_energy": normalized_energy,
        "normalized_efficiency_penalty": efficiency_penalty,
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
        "avg_energy_per_sample_kwh": (
            base["total_energy_kwh"] / base["n_total"] if base["n_total"] else 0.0
        ),
        "avg_co2_per_sample_g": (
            base["total_co2_g"] / base["n_total"] if base["n_total"] else 0.0
        ),
    }
