"""
Evaluation metrics.

EATS — Efficiency-Accuracy Trade-off Score
==========================================
Defined to fill the gap identified in SLR RQ2:
  "cost and energy remain far less reported than accuracy"

Formula:
    efficiency_penalty = (
        0.65 × normalized_cost +
        0.20 × normalized_algorithmic_latency +
        0.15 × normalized_energy
    )
    quality_penalty = 0.60 × (1 − accuracy)
    EATS = accuracy / (accuracy + 0.40 × efficiency_penalty + quality_penalty)

Where:
    - accuracy        : fraction of correct answers
    - normalized_cost : total_cost_usd / cost_usd_full_llm_baseline
                        (1.0 = same cost as running all samples on LLM)
    - normalized_algorithmic_latency :
                        avg_algorithmic_latency_ms / full_llm_avg_algorithmic_latency_ms
    - normalized_energy  : total_energy_kwh / total_energy_kwh_full_llm_baseline

Weights (sum to 1): cost 65%, latency 20%, energy 15%.
The additive form avoids multiplicative collapse when any single dimension
is unmeasured (e.g. energy ≈ 0 for API-only architectures): those missing
dimensions simply contribute zero to the penalty rather than zeroing out all
other penalties.

The form accuracy / (accuracy + λ × penalty + β × error) is structurally
analogous to an F-score-like trade-off, but with an explicit accuracy-deficit
term so low-accuracy systems cannot score near 1.0 simply by being cheap.
This revision uses λ = 0.40 and β = 0.60. Score is bounded in [0, 1].

Interpretation: Higher EATS is better. A system with 0.75 accuracy that only
uses low cost, low algorithmic latency, and low energy will score higher than
one with similar accuracy but heavier resource usage.
"""
from __future__ import annotations

import math

from core.types import ExperimentResult

EATS_W_COST = 0.65
EATS_W_LATENCY = 0.20
EATS_W_ENERGY = 0.15
EATS_PENALTY_SCALE = 0.40
EATS_QUALITY_DEFICIT_SCALE = 0.60


def compute_efficiency_penalty(
    normalized_cost: float = 1.0,
    normalized_algorithmic_latency: float = 1.0,
    normalized_energy: float = 1.0,
    w_cost: float = EATS_W_COST,
    w_latency: float = EATS_W_LATENCY,
    w_energy: float = EATS_W_ENERGY,
) -> float:
    return (
        w_cost * max(normalized_cost, 0.0) +
        w_latency * max(normalized_algorithmic_latency, 0.0) +
        w_energy * max(normalized_energy, 0.0)
    )


def compute_accuracy_deficit_penalty(
    accuracy: float,
    quality_deficit_scale: float = EATS_QUALITY_DEFICIT_SCALE,
) -> float:
    acc = min(max(accuracy, 0.0), 1.0)
    return quality_deficit_scale * (1.0 - acc)


def aggregate_runs(runs: list[dict[str, float]]) -> dict[str, float]:
    """Compute mean and std across repeated runs of the same config.

    Given N metrics dicts (one per run), returns a flat dict where every
    numeric key appears twice:
      - ``<key>_mean`` — arithmetic mean across runs
      - ``<key>_std``  — sample standard deviation (ddof=1, or 0.0 for N=1)

    Non-numeric values are dropped. Intended for thesis-grade reporting where
    CLAUDE.md §9 requires mean ± std over ≥ 3 independent runs.
    """
    if not runs:
        return {}
    keys = [k for k, v in runs[0].items() if isinstance(v, (int, float))]
    out: dict[str, float] = {"n_runs": float(len(runs))}
    for key in keys:
        vals = [float(r[key]) for r in runs if key in r]
        if not vals:
            continue
        mean = sum(vals) / len(vals)
        if len(vals) > 1:
            variance = sum((v - mean) ** 2 for v in vals) / (len(vals) - 1)
            std = math.sqrt(variance)
        else:
            std = 0.0
        out[f"{key}_mean"] = mean
        out[f"{key}_std"] = std
    return out


def compute_subject_accuracy(result: ExperimentResult) -> dict[str, dict[str, float]]:
    """Disaggregate accuracy by query metadata group.

    Returns a dict keyed by group field name, each containing a
    {group_value: accuracy} mapping. Currently extracts:
      - "subject"    — MMLU 57-subject breakdown
      - "difficulty" — custom_stratified easy/medium/hard breakdown

    Returns an empty dict when no groupable metadata is present.
    """
    from collections import defaultdict

    group_fields = ["subject", "difficulty"]
    result_map: dict[str, dict[str, float]] = {}

    for field in group_fields:
        buckets: dict[str, list[bool]] = defaultdict(list)
        for s in result.samples:
            val = s.query.metadata.get(field)
            if val:
                buckets[str(val)].append(s.correct)
        if buckets:
            result_map[field] = {
                k: sum(v) / len(v) for k, v in sorted(buckets.items())
            }

    return result_map


def _normalize_metric(value: float, baseline: float | None) -> float:
    if baseline and baseline > 0:
        return value / baseline
    return 1.0


def wilson_ci(n_correct: int, n_total: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a proportion at the given z (default 95%)."""
    if n_total == 0:
        return 0.0, 0.0
    p = n_correct / n_total
    denom = 1 + z * z / n_total
    center = (p + z * z / (2 * n_total)) / denom
    margin = z * math.sqrt(p * (1 - p) / n_total + z * z / (4 * n_total * n_total)) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def compute_ece(
    confidences: list[float],
    correctness: list[bool],
    n_bins: int = 10,
) -> float:
    """Expected Calibration Error (Guo et al. 2017), equal-width bins.

    ECE = Σ_b (|B_b| / n) × |acc(B_b) − conf(B_b)|

    A perfectly calibrated model scores 0.0. Only meaningful when confidence
    scores actually vary (e.g. routing SLM); returns 0.0 on empty input.
    """
    if not confidences or len(confidences) != len(correctness):
        return 0.0
    n = len(confidences)
    bin_width = 1.0 / n_bins
    ece = 0.0
    for b in range(n_bins):
        lo = b * bin_width
        hi = lo + bin_width
        # include the right edge only in the last bucket
        in_bin = [
            i for i, c in enumerate(confidences)
            if lo <= c < hi or (b == n_bins - 1 and c == 1.0)
        ]
        if not in_bin:
            continue
        bucket_n = len(in_bin)
        avg_conf = sum(confidences[i] for i in in_bin) / bucket_n
        avg_acc = sum(1 for i in in_bin if correctness[i]) / bucket_n
        ece += (bucket_n / n) * abs(avg_acc - avg_conf)
    return ece


def compute_eats(
    accuracy: float,
    normalized_cost: float = 1.0,
    normalized_algorithmic_latency: float = 1.0,
    normalized_energy: float = 1.0,
    w_cost: float = EATS_W_COST,
    w_latency: float = EATS_W_LATENCY,
    w_energy: float = EATS_W_ENERGY,
    penalty_scale: float = EATS_PENALTY_SCALE,
    quality_deficit_scale: float = EATS_QUALITY_DEFICIT_SCALE,
) -> float:
    acc = min(max(accuracy, 0.0), 1.0)
    penalty = compute_efficiency_penalty(
        normalized_cost=normalized_cost,
        normalized_algorithmic_latency=normalized_algorithmic_latency,
        normalized_energy=normalized_energy,
        w_cost=w_cost,
        w_latency=w_latency,
        w_energy=w_energy,
    )
    quality_penalty = compute_accuracy_deficit_penalty(
        accuracy=acc,
        quality_deficit_scale=quality_deficit_scale,
    )
    denom = acc + penalty_scale * penalty + quality_penalty
    return (acc / denom) if denom > 0 else 0.0


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
    efficiency_penalty = compute_efficiency_penalty(
        normalized_cost=normalized_cost,
        normalized_algorithmic_latency=normalized_algorithmic_latency,
        normalized_energy=normalized_energy,
    )
    accuracy_deficit_penalty = compute_accuracy_deficit_penalty(base["accuracy"])

    eats = compute_eats(
        accuracy=base["accuracy"],
        normalized_cost=normalized_cost,
        normalized_algorithmic_latency=normalized_algorithmic_latency,
        normalized_energy=normalized_energy,
    )

    # Per-sample averages
    latencies = [
        ExperimentResult._algorithmic_latency_of(s.response)
        for s in result.samples
    ]
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
    n_correct = int(base["n_correct"])
    escalation_rate = n_escalated / n_total if n_total else 0.0

    acc_ci_low, acc_ci_high = wilson_ci(n_correct, n_total)

    cost_slm_path_usd = sum(
        s.response.cost_usd for s in non_escalated_samples
    )
    cost_escalated_path_usd = sum(
        s.response.cost_usd for s in escalated_samples
    )
    total_cost = base["total_cost_usd"]
    cost_slm_path_fraction = (
        cost_slm_path_usd / total_cost if total_cost > 0 else 0.0
    )

    # Joules per output token — §8 primary energy comparison unit
    total_output_tokens = sum(s.response.output_tokens for s in result.samples)
    joules_per_output_token = (
        (base["total_energy_kwh"] * 3_600_000) / total_output_tokens
        if total_output_tokens > 0 else 0.0
    )

    # Per-architecture accuracy breakdowns
    # non_escalated = SLM-handled (routing) or majority-vote succeeded (ensemble)
    # escalated     = LLM-fallback (routing) or LLM tiebreak (ensemble)
    n_non_esc_correct = sum(1 for s in non_escalated_samples if s.correct)
    n_esc_correct = sum(1 for s in escalated_samples if s.correct)
    accuracy_slm_handled = (
        n_non_esc_correct / len(non_escalated_samples) if non_escalated_samples else 0.0
    )
    accuracy_llm_handled = (
        n_esc_correct / len(escalated_samples) if escalated_samples else 0.0
    )
    # ECE — calibration of confidence scores used for routing decisions
    # Uses SLM confidence when available, falls back to response.confidence.
    ece_confs = [
        float(s.response.metadata.get("slm_confidence") or s.response.confidence or 0.0)
        for s in result.samples
    ]
    ece_correct = [s.correct for s in result.samples]
    ece = compute_ece(ece_confs, ece_correct)

    # oracle_query_rate: fraction of queries that made at least one oracle call
    n_oracle_queries = sum(
        1 for s in result.samples
        if any(
            isinstance(step, dict) and "oracle" in str(step.get("role", "")).lower()
            for step in (s.response.metadata.get("inference_steps") or [])
        )
    )
    oracle_query_rate = n_oracle_queries / n_total if n_total else 0.0

    # Per-model-tier API cost derived from inference_steps, so it works for
    # every architecture (routing, ensemble, multi-agent, speculative, etc.).
    # Steps whose model_id matches the config's SLM pool are SLM-tier;
    # steps whose model_id matches the LLM are LLM-tier.
    slm_ids: set[str] = set()
    if result.config.slm:
        slm_ids.add(result.config.slm)
    slm_ids.update(result.config.ensemble_slms or [])
    llm_id = result.config.llm or ""

    total_slm_api_cost_usd = 0.0
    total_llm_api_cost_usd = 0.0
    for s in result.samples:
        steps = s.response.metadata.get("inference_steps") or []
        for step in steps:
            if not isinstance(step, dict):
                continue
            mid = str(step.get("model_id") or "")
            step_cost = float(step.get("api_cost_usd") or 0.0)
            if mid in slm_ids:
                total_slm_api_cost_usd += step_cost
            elif llm_id and mid == llm_id:
                total_llm_api_cost_usd += step_cost
            else:
                # Fallback: monolithic has no SLM, so all cost is LLM-tier
                if not slm_ids:
                    total_llm_api_cost_usd += step_cost

    accepted_draft_ratios: list[float] = []
    rewrite_flags: list[bool] = []
    draft_completion_tokens: list[float] = []
    verifier_request_counts: list[float] = []
    verifier_completion_counts: list[float] = []
    if result.config.architecture == "speculative":
        accepted_draft_ratios = [
            float(s.response.metadata.get("accepted_draft_ratio"))
            for s in result.samples
            if isinstance(s.response.metadata.get("accepted_draft_ratio"), (int, float))
        ]
        rewrite_flags = [
            bool(s.response.metadata.get("rewrite_triggered"))
            for s in result.samples
            if "rewrite_triggered" in s.response.metadata
        ]
        draft_completion_tokens = [
            float(s.response.metadata.get("slm_output_tokens"))
            for s in result.samples
            if isinstance(s.response.metadata.get("slm_output_tokens"), (int, float))
        ]
        verifier_request_counts = [
            float(s.response.metadata.get("verifier_requests"))
            for s in result.samples
            if isinstance(s.response.metadata.get("verifier_requests"), (int, float))
        ]
        verifier_completion_counts = [
            float(s.response.metadata.get("verifier_completion_tokens"))
            for s in result.samples
            if isinstance(s.response.metadata.get("verifier_completion_tokens"), (int, float))
        ]

    metrics = {
        **base,
        "accuracy_ci_low_95": acc_ci_low,
        "accuracy_ci_high_95": acc_ci_high,
        "eats_score": eats,
        "normalized_cost": normalized_cost,
        "normalized_algorithmic_latency": normalized_algorithmic_latency,
        "normalized_energy": normalized_energy,
        "normalized_efficiency_penalty": efficiency_penalty,
        "accuracy_deficit_penalty": accuracy_deficit_penalty,
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
        "cost_slm_path_usd": cost_slm_path_usd,
        "cost_escalated_path_usd": cost_escalated_path_usd,
        "cost_slm_path_fraction": cost_slm_path_fraction,
        "total_slm_api_cost_usd": total_slm_api_cost_usd,
        "total_llm_api_cost_usd": total_llm_api_cost_usd,
        # Throughput and per-query cost — standard comparison units
        "throughput_tokens_per_sec": (
            total_output_tokens / (base["avg_latency_ms"] / 1000.0)
            if base["avg_latency_ms"] > 0 else 0.0
        ),
        "cost_per_query_usd": (
            base["total_cost_usd"] / n_total if n_total else 0.0
        ),
        # Energy — primary comparison unit per §8
        "joules_per_output_token": joules_per_output_token,
        "ece": ece,
        # Per-architecture accuracy breakdowns
        "accuracy_slm_handled": accuracy_slm_handled,   # routing: SLM-only path
        "accuracy_llm_handled": accuracy_llm_handled,   # routing: LLM fallback path
        "accuracy_majority_vote": accuracy_slm_handled, # ensemble alias (same split)
        "llm_tiebreak_rate": escalation_rate,           # ensemble: tiebreak fraction
        "oracle_query_rate": oracle_query_rate,         # active_oracle only
        "baseline_cost_usd": full_llm_cost_usd if full_llm_cost_usd is not None else 0.0,
        "baseline_algorithmic_latency_ms": full_llm_avg_algorithmic_latency_ms if full_llm_avg_algorithmic_latency_ms is not None else 0.0,
        "baseline_energy_kwh": full_llm_energy_kwh if full_llm_energy_kwh is not None else 0.0,
    }
    if rewrite_flags:
        metrics["rewrite_rate"] = (
            sum(1 for flag in rewrite_flags if flag) / len(rewrite_flags)
        )
    if accepted_draft_ratios:
        metrics["avg_accepted_draft_ratio"] = (
            sum(accepted_draft_ratios) / len(accepted_draft_ratios)
        )
    if draft_completion_tokens:
        metrics["avg_draft_completion_tokens"] = (
            sum(draft_completion_tokens) / len(draft_completion_tokens)
        )
        metrics["max_draft_completion_tokens"] = max(draft_completion_tokens)
    if verifier_request_counts:
        metrics["avg_verifier_requests"] = (
            sum(verifier_request_counts) / len(verifier_request_counts)
        )
    if verifier_completion_counts:
        metrics["avg_verifier_completion_tokens"] = (
            sum(verifier_completion_counts) / len(verifier_completion_counts)
        )
    return metrics
