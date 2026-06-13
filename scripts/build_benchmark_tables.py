"""
Build per-benchmark comparison JSON tables from experiment results.
Filters out experiments created on or before 2026-05-27.
Groups by (architecture, model_key) and averages metrics across multiple runs.
"""

import json
import glob
import os
from datetime import datetime, timezone
from collections import defaultdict

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
OUTPUT_DIR = os.path.join(RESULTS_DIR, "benchmark_tables")
CUTOFF = datetime.fromisoformat("2026-05-27T23:59:59+00:00")
MIN_TOTAL_SAMPLES = 100

# The five benchmarks in scope for the study. Result files for benchmarks
# outside this set (e.g. the dropped livecodebench/humaneval_plus runs) are
# ignored so no stray tables are produced.
STUDY_BENCHMARKS = {"mmlu", "arc", "gsm8k", "hellaswag", "truthfulqa"}

# Principal operating point for the blackboard family. Exploratory runs
# (the MMLU bid-threshold sweep, 20-sample pilots, and legacy
# pre-claim-policy runs at bid 0.65 / TTL 1500 ms) are excluded so each
# reported row is a single matched run; they are discussed in the report
# prose instead of the tables.
BLACKBOARD_BID_THRESHOLD = 0.75
BLACKBOARD_TTL_MS = 3500

METRICS_TO_AVG = [
    "accuracy",
    "llm_call_ratio",
    "avg_latency_ms",
    "latency_p50_ms",
    "latency_p95_ms",
    "avg_slm_confidence",
    "escalation_rate",
]
METRICS_TO_NORMALIZE = [
    ("total_cost_usd", "avg_cost_per_sample_usd"),
    ("total_api_cost_usd", "avg_api_cost_per_sample_usd"),
    ("total_infra_cost_usd", "avg_infra_cost_per_sample_usd"),
    ("total_energy_kwh", "avg_energy_per_sample_kwh"),
    ("total_co2_g", "avg_co2_per_sample_g"),
]


def get_model_key(config: dict) -> str:
    arch = config["architecture"]
    slm = config.get("slm")
    llm = config.get("llm")
    ensemble_slms = config.get("ensemble_slms") or []

    if arch == "monolithic":
        return slm or llm or "unknown"
    elif arch == "ensemble":
        return "+".join(sorted(ensemble_slms)) if ensemble_slms else (slm or "unknown")
    elif arch in ("routing", "speculative", "active_oracle", "blackboard", "entropy_blackboard"):
        parts = [p for p in [slm, llm] if p]
        key = " → ".join(parts) if parts else "unknown"
        if arch in ("blackboard", "entropy_blackboard"):
            # Split by claim policy. claim_policy was introduced in 5f48199
            # (2026-06-07); runs without the field used the legacy
            # first-to-threshold claiming behaviour.
            key += f" [{config.get('claim_policy') or 'first_threshold'}]"
        return key
    elif arch == "pure_swarm":
        return slm or "unknown"
    elif arch == "multi_agent":
        # Split debate (POA) by arbitrator type: SLM-only vs LLM-arbitrated
        if config.get("arbitrator") == "llm" and llm:
            return f"{slm} → {llm}"
        return slm or "unknown"
    return slm or llm or "unknown"


def load_valid_experiments():
    files = glob.glob(os.path.join(RESULTS_DIR, "exp_*.json"))
    experiments = []
    skipped = 0

    for path in files:
        with open(path) as f:
            data = json.load(f)

        created = datetime.fromisoformat(data["created_at"])
        if created <= CUTOFF:
            skipped += 1
            continue

        config = data["config"]
        metrics = data["metrics"]

        if config["benchmark"] not in STUDY_BENCHMARKS:
            skipped += 1
            continue
        n_total = metrics.get("n_total", config.get("n_samples", 1)) or 1

        if config["architecture"] in ("blackboard", "entropy_blackboard"):
            if (
                config.get("claim_policy") is None
                or config.get("bid_threshold") != BLACKBOARD_BID_THRESHOLD
                or config.get("ttl_ms") != BLACKBOARD_TTL_MS
            ):
                skipped += 1
                continue

        entry = {
            "experiment_id": data["experiment_id"],
            "created_at": data["created_at"],
            "benchmark": config["benchmark"],
            "architecture": config["architecture"],
            "model_key": get_model_key(config),
            "slm": config.get("slm"),
            "llm": config.get("llm"),
            "ensemble_slms": config.get("ensemble_slms"),
            "n_samples": n_total,
            "confidence_threshold": config.get("confidence_threshold"),
            "n_models": config.get("n_models"),
            # raw metrics for averaging
            "accuracy": metrics.get("accuracy"),
            "llm_call_ratio": metrics.get("llm_call_ratio"),
            "avg_latency_ms": metrics.get("avg_latency_ms"),
            "latency_p50_ms": metrics.get("latency_p50_ms"),
            "latency_p95_ms": metrics.get("latency_p95_ms"),
            "avg_slm_confidence": metrics.get("avg_slm_confidence"),
            "escalation_rate": metrics.get("escalation_rate"),
            # normalized (per-sample)
            "avg_cost_per_sample_usd": metrics.get("total_cost_usd", 0) / n_total,
            "avg_api_cost_per_sample_usd": metrics.get("total_api_cost_usd", 0) / n_total,
            "avg_infra_cost_per_sample_usd": metrics.get("total_infra_cost_usd", 0) / n_total,
            "avg_energy_per_sample_kwh": metrics.get("total_energy_kwh", 0) / n_total,
            "avg_co2_per_sample_g": metrics.get("total_co2_g", 0) / n_total,
        }
        experiments.append(entry)

    print(f"Loaded {len(experiments)} valid experiments, skipped {skipped} (≤2026-05-27 or off the blackboard principal operating point)")
    return experiments


def aggregate_group(exps: list) -> dict:
    """Average numeric metrics across experiments in a group."""
    avg_metrics = [
        "accuracy", "llm_call_ratio", "avg_latency_ms",
        "latency_p50_ms", "latency_p95_ms", "avg_slm_confidence",
        "escalation_rate", "avg_cost_per_sample_usd", "avg_api_cost_per_sample_usd",
        "avg_infra_cost_per_sample_usd", "avg_energy_per_sample_kwh",
        "avg_co2_per_sample_g",
    ]

    rep = exps[0]
    result = {
        "architecture": rep["architecture"],
        "model_key": rep["model_key"],
        "slm": rep["slm"],
        "llm": rep["llm"],
        "ensemble_slms": rep["ensemble_slms"],
        "n_experiments": len(exps),
        "experiment_ids": [e["experiment_id"] for e in exps],
        "total_samples_evaluated": int(sum(e["n_samples"] for e in exps)),
    }

    for metric in avg_metrics:
        vals = [e[metric] for e in exps if e.get(metric) is not None]
        if vals:
            result[metric] = round(sum(vals) / len(vals), 6)
        else:
            result[metric] = None

    return result


def compute_eats(
    accuracy: float,
    normalized_cost: float = 1.0,
    normalized_latency: float = 1.0,
    normalized_energy: float = 1.0,
    w_cost: float = 0.5,
    w_latency: float = 0.3,
    w_energy: float = 0.2,
) -> float:
    acc = max(accuracy, 0.0)
    penalty = (
        w_cost * max(normalized_cost, 0.0)
        + w_latency * max(normalized_latency, 0.0)
        + w_energy * max(normalized_energy, 0.0)
    )
    denom = acc + penalty
    return round(acc / denom, 6) if denom > 0 else 0.0


def add_eats(entries: list) -> None:
    """Compute EATS in-place. Reference = mean of monolithic entries per benchmark."""
    mono = [e for e in entries if e["architecture"] == "monolithic"]
    if not mono:
        for e in entries:
            e["eats"] = None
        return

    def _mean(field):
        vals = [e[field] for e in mono if e.get(field) is not None]
        return sum(vals) / len(vals) if vals else None

    ref_cost = _mean("avg_cost_per_sample_usd")
    ref_latency = _mean("avg_latency_ms")
    ref_energy = _mean("avg_energy_per_sample_kwh")

    for e in entries:
        acc = e.get("accuracy")
        cost = e.get("avg_cost_per_sample_usd")
        latency = e.get("avg_latency_ms")
        energy = e.get("avg_energy_per_sample_kwh")

        if any(v is None for v in [acc, cost, latency, energy, ref_cost, ref_latency, ref_energy]):
            e["eats"] = None
            continue

        e["eats"] = compute_eats(
            accuracy=acc,
            normalized_cost=cost / ref_cost if ref_cost else 1.0,
            normalized_latency=latency / ref_latency if ref_latency else 1.0,
            normalized_energy=energy / ref_energy if ref_energy else 1.0,
        )


def build_tables(experiments: list):
    # Group: benchmark → (architecture, model_key) → [experiments]
    by_bench = defaultdict(lambda: defaultdict(list))
    for exp in experiments:
        key = (exp["architecture"], exp["model_key"])
        by_bench[exp["benchmark"]][key].append(exp)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    summary = {}
    for benchmark, groups in sorted(by_bench.items()):
        entries = []
        skipped_configs = []
        for (arch, model_key), exps in sorted(groups.items()):
            aggregated = aggregate_group(exps)
            if aggregated["total_samples_evaluated"] < MIN_TOTAL_SAMPLES:
                skipped_configs.append(
                    {
                        "architecture": arch,
                        "model_key": model_key,
                        "total_samples_evaluated": aggregated["total_samples_evaluated"],
                        "experiment_ids": aggregated["experiment_ids"],
                    }
                )
                continue
            entries.append(aggregated)

        # Sort: by architecture then model_key
        entries.sort(key=lambda x: (x["architecture"], x["model_key"]))
        add_eats(entries)

        table = {
            "benchmark": benchmark,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "min_total_samples_required": MIN_TOTAL_SAMPLES,
            "n_unique_configs": len(entries),
            "skipped_configs_below_min_samples": skipped_configs,
            "entries": entries,
        }

        out_path = os.path.join(OUTPUT_DIR, f"benchmark_{benchmark}.json")
        with open(out_path, "w") as f:
            json.dump(table, f, indent=2)

        summary[benchmark] = {
            "n_configs": len(entries),
            "architectures": sorted(set(e["architecture"] for e in entries)),
            "min_total_samples_required": MIN_TOTAL_SAMPLES,
            "n_skipped_configs_below_min_samples": len(skipped_configs),
            "output": out_path,
        }
        print(
            f"  [{benchmark}] {len(entries)} configs "
            f"(skipped {len(skipped_configs)} below N={MIN_TOTAL_SAMPLES}) → {out_path}"
        )

    # Write summary
    summary_path = os.path.join(OUTPUT_DIR, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "cutoff": CUTOFF.isoformat(),
                "min_total_samples_required": MIN_TOTAL_SAMPLES,
                "benchmarks": summary,
            },
            f,
            indent=2,
        )
    print(f"\nSummary → {summary_path}")


if __name__ == "__main__":
    experiments = load_valid_experiments()
    build_tables(experiments)
