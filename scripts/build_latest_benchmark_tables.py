"""
Build poster-oriented benchmark tables from the latest qualified experiment runs.

Selection rule:
- For each benchmark x architecture, keep the most recently created experiment
  whose evaluated sample count is at least 100.

Scoring rule:
- Reuse the experiment's canonical EATS score when it is present.
- Preserve the accompanying cost / latency / energy / normalized metrics so the
  poster tables stay aligned with the web UI and runner outputs.

Outputs are written under results/benchmark_tables as:
- latest_benchmark_<benchmark>.json
- latest_summary.json
- latest_panels.json
"""

from __future__ import annotations

import glob
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.model_catalog import get_model_spec
from evaluation.metrics import _normalize_metric, compute_eats, compute_efficiency_penalty
from experiments.runner import resolve_recommended_baseline

RESULTS_DIR = REPO_ROOT / "results"
OUTPUT_DIR = RESULTS_DIR / "benchmark_tables"
MIN_TOTAL_SAMPLES = 100
STUDY_BENCHMARKS = ("mmlu", "arc", "gsm8k", "hellaswag", "truthfulqa")
NOVEL_ARCHITECTURES = {
    "active_oracle",
    "blackboard",
    "entropy_blackboard",
    "multi_agent",
    "pure_swarm",
}
ARCHITECTURE_LABELS = {
    "active_oracle": "Active Oracle",
    "blackboard": "Blackboard",
    "ensemble": "Ensemble",
    "entropy_blackboard": "Entropy BB",
    "multi_agent": "Debate",
    "pure_swarm": "Pure Swarm",
    "routing": "Routing",
    "speculative": "Speculative",
}
BENCHMARK_DISPLAY_NAMES = {
    "mmlu": "MMLU",
    "arc": "ARC",
    "gsm8k": "GSM8K",
    "hellaswag": "HellaSwag",
    "truthfulqa": "TruthfulQA",
}


def _safe_div(numerator: float | int | None, denominator: float | int | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return float(numerator) / float(denominator)


def _round_or_none(value: float | int | None, digits: int = 6) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def get_model_key(config: dict) -> str:
    arch = config["architecture"]
    slm = config.get("slm")
    llm = config.get("llm")
    ensemble_slms = config.get("ensemble_slms") or []

    if arch == "monolithic":
        return slm or llm or "unknown"
    if arch == "ensemble":
        return "+".join(sorted(ensemble_slms)) if ensemble_slms else (slm or "unknown")
    if arch in ("routing", "speculative", "active_oracle", "blackboard", "entropy_blackboard"):
        parts = [part for part in (slm, llm) if part]
        return " → ".join(parts) if parts else "unknown"
    if arch == "pure_swarm":
        return slm or "unknown"
    if arch == "multi_agent":
        if config.get("arbitrator") == "llm" and llm:
            return f"{slm} → {llm}"
        return slm or "unknown"
    return slm or llm or "unknown"


def get_poster_label(config: dict, model_key: str) -> str:
    arch = config["architecture"]
    if arch == "monolithic":
        model_id = config.get("llm") or config.get("slm") or model_key
        spec = get_model_spec(model_id)
        if spec and spec.tier == "moe":
            return model_id
        return model_id
    if arch == "multi_agent" and config.get("arbitrator") == "llm" and config.get("llm"):
        return "LLM-arb. Debate"
    return ARCHITECTURE_LABELS.get(arch, arch)


def get_canonical_eats(metrics: dict) -> float | None:
    eats = metrics.get("eats_score")
    if eats is None:
        return None
    return round(float(eats), 6)


def harmonize_metrics_with_web_rule(config: dict, metrics: dict) -> dict:
    """Mirror the web layer's baseline backfill + EATS recomputation logic."""
    harmonized = dict(metrics)
    llm = config.get("llm")

    baseline_cost = harmonized.get("baseline_cost_usd", 0.0) or 0.0
    baseline_latency = harmonized.get("baseline_algorithmic_latency_ms", 0.0) or 0.0
    baseline_energy = harmonized.get("baseline_energy_kwh", 0.0) or 0.0

    if harmonized.get("baseline_accuracy") is None or baseline_cost == 0.0:
        baseline = resolve_recommended_baseline(
            config.get("benchmark", "mmlu"),
            llm,
            n_samples=int(config.get("n_samples", 500)),
        )
        if baseline:
            harmonized["baseline_cost_usd"] = baseline.get("total_cost_usd", 0.0) or 0.0
            harmonized["baseline_algorithmic_latency_ms"] = (
                baseline.get("avg_algorithmic_latency_ms", 0.0) or 0.0
            )
            harmonized["baseline_energy_kwh"] = baseline.get("total_energy_kwh", 0.0) or 0.0
            if baseline.get("accuracy") is not None:
                harmonized["baseline_accuracy"] = baseline.get("accuracy")
            if baseline.get("eats_score") is not None:
                harmonized["baseline_eats_score"] = baseline.get("eats_score")
            if baseline.get("ece") is not None:
                harmonized["baseline_ece"] = baseline.get("ece")

    baseline_cost = harmonized.get("baseline_cost_usd", 0.0) or 0.0
    baseline_latency = harmonized.get("baseline_algorithmic_latency_ms", 0.0) or 0.0
    baseline_energy = harmonized.get("baseline_energy_kwh", 0.0) or 0.0

    if baseline_cost > 0.0 and baseline_latency > 0.0 and baseline_energy > 0.0:
        harmonized["normalized_cost"] = _normalize_metric(
            harmonized.get("total_cost_usd", 0.0) or 0.0,
            baseline_cost,
        )
        harmonized["normalized_algorithmic_latency"] = _normalize_metric(
            harmonized.get("avg_algorithmic_latency_ms", harmonized.get("avg_latency_ms", 0.0)) or 0.0,
            baseline_latency,
        )
        harmonized["normalized_energy"] = _normalize_metric(
            harmonized.get("total_energy_kwh", 0.0) or 0.0,
            baseline_energy,
        )
        harmonized["normalized_efficiency_penalty"] = compute_efficiency_penalty(
            normalized_cost=harmonized["normalized_cost"],
            normalized_algorithmic_latency=harmonized["normalized_algorithmic_latency"],
            normalized_energy=harmonized["normalized_energy"],
        )
        harmonized["eats_score"] = compute_eats(
            accuracy=harmonized.get("accuracy", 0.0) or 0.0,
            normalized_cost=harmonized["normalized_cost"],
            normalized_algorithmic_latency=harmonized["normalized_algorithmic_latency"],
            normalized_energy=harmonized["normalized_energy"],
        )

    return harmonized


def load_latest_qualified_runs() -> tuple[dict[str, list[dict]], list[dict]]:
    latest_by_key: dict[tuple[str, str], dict] = {}
    skipped: list[dict] = []

    for path_str in glob.glob(str(RESULTS_DIR / "exp_*.json")):
        path = Path(path_str)
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)

        config = data.get("config", {})
        metrics = harmonize_metrics_with_web_rule(config, data.get("metrics", {}))
        benchmark = config.get("benchmark")
        architecture = config.get("architecture")
        created_at = data.get("created_at")

        if benchmark not in STUDY_BENCHMARKS or not architecture or not created_at:
            continue

        n_total = metrics.get("n_total", config.get("n_samples", 0)) or 0
        if n_total < MIN_TOTAL_SAMPLES:
            skipped.append(
                {
                    "experiment_id": data.get("experiment_id"),
                    "benchmark": benchmark,
                    "architecture": architecture,
                    "created_at": created_at,
                    "n_total": n_total,
                    "reason": f"n_total < {MIN_TOTAL_SAMPLES}",
                }
            )
            continue

        model_key = get_model_key(config)
        entry = {
            "experiment_id": data["experiment_id"],
            "source_file": path.name,
            "created_at": created_at,
            "completed_at": data.get("completed_at"),
            "benchmark": benchmark,
            "architecture": architecture,
            "poster_label": get_poster_label(config, model_key),
            "model_key": model_key,
            "slm": config.get("slm"),
            "secondary_slm": config.get("secondary_slm"),
            "llm": config.get("llm"),
            "ensemble_slms": config.get("ensemble_slms") or [],
            "arbitrator": config.get("arbitrator"),
            "claim_policy": config.get("claim_policy"),
            "bid_threshold": config.get("bid_threshold"),
            "ttl_ms": config.get("ttl_ms"),
            "n_models": config.get("n_models"),
            "n_samples": int(n_total),
            "accuracy": _round_or_none(metrics.get("accuracy")),
            "eats_score": get_canonical_eats(metrics),
            "llm_call_ratio": _round_or_none(metrics.get("llm_call_ratio")),
            "avg_latency_ms": _round_or_none(metrics.get("avg_latency_ms")),
            "avg_algorithmic_latency_ms": _round_or_none(
                metrics.get("avg_algorithmic_latency_ms", metrics.get("avg_latency_ms"))
            ),
            "latency_p50_ms": _round_or_none(metrics.get("latency_p50_ms")),
            "latency_p95_ms": _round_or_none(metrics.get("latency_p95_ms")),
            "avg_slm_confidence": _round_or_none(metrics.get("avg_slm_confidence")),
            "escalation_rate": _round_or_none(metrics.get("escalation_rate")),
            "total_cost_usd": _round_or_none(metrics.get("total_cost_usd", 0.0)),
            "total_api_cost_usd": _round_or_none(metrics.get("total_api_cost_usd", 0.0)),
            "total_infra_cost_usd": _round_or_none(metrics.get("total_infra_cost_usd", 0.0)),
            "total_energy_kwh": _round_or_none(metrics.get("total_energy_kwh", 0.0)),
            "total_co2_g": _round_or_none(metrics.get("total_co2_g", 0.0)),
            "cost_per_query_usd": _round_or_none(
                metrics.get("cost_per_query_usd"),
            ),
            "avg_cost_per_sample_usd": _round_or_none(
                metrics.get("cost_per_query_usd", _safe_div(metrics.get("total_cost_usd", 0), n_total))
            ),
            "avg_api_cost_per_sample_usd": _round_or_none(
                _safe_div(metrics.get("total_api_cost_usd", 0), n_total)
            ),
            "avg_infra_cost_per_sample_usd": _round_or_none(
                _safe_div(metrics.get("total_infra_cost_usd", 0), n_total)
            ),
            "avg_energy_per_sample_kwh": _round_or_none(
                metrics.get("avg_energy_per_sample_kwh", _safe_div(metrics.get("total_energy_kwh", 0), n_total))
            ),
            "avg_co2_per_sample_g": _round_or_none(
                metrics.get("avg_co2_per_sample_g", _safe_div(metrics.get("total_co2_g", 0), n_total))
            ),
            "normalized_cost": _round_or_none(metrics.get("normalized_cost")),
            "normalized_algorithmic_latency": _round_or_none(
                metrics.get("normalized_algorithmic_latency")
            ),
            "normalized_energy": _round_or_none(metrics.get("normalized_energy")),
            "normalized_efficiency_penalty": _round_or_none(
                metrics.get("normalized_efficiency_penalty")
            ),
            "baseline_cost_usd": _round_or_none(metrics.get("baseline_cost_usd")),
            "baseline_algorithmic_latency_ms": _round_or_none(
                metrics.get("baseline_algorithmic_latency_ms")
            ),
            "baseline_energy_kwh": _round_or_none(metrics.get("baseline_energy_kwh")),
            "baseline_accuracy": _round_or_none(metrics.get("baseline_accuracy")),
            "baseline_eats_score": _round_or_none(metrics.get("baseline_eats_score")),
        }

        key = (benchmark, architecture)
        current = latest_by_key.get(key)
        if current is None or datetime.fromisoformat(created_at) > datetime.fromisoformat(current["created_at"]):
            latest_by_key[key] = entry

    by_benchmark: dict[str, list[dict]] = defaultdict(list)
    for (_, _), entry in latest_by_key.items():
        by_benchmark[entry["benchmark"]].append(entry)

    for benchmark in by_benchmark:
        by_benchmark[benchmark].sort(key=lambda item: (item["architecture"], item["poster_label"]))

    return by_benchmark, skipped


def build_panel_summary(benchmark: str, entries: list[dict]) -> dict:
    eligible_eats = [entry for entry in entries if entry.get("eats_score") is not None]
    eligible_accuracy = [entry for entry in entries if entry.get("accuracy") is not None]
    thesis_entries = [entry for entry in entries if entry["architecture"] in NOVEL_ARCHITECTURES]

    eats_leader = max(
        eligible_eats,
        key=lambda entry: (entry["eats_score"], entry.get("accuracy") or 0.0),
    )
    accuracy_leader = max(
        eligible_accuracy,
        key=lambda entry: ((entry.get("accuracy") or 0.0), (entry.get("eats_score") or 0.0)),
    )
    novel_leader = max(
        thesis_entries,
        key=lambda entry: ((entry.get("accuracy") or 0.0), (entry.get("eats_score") or 0.0)),
    )

    def compact(entry: dict) -> dict:
        return {
            "architecture": entry["architecture"],
            "label": entry["poster_label"],
            "experiment_id": entry["experiment_id"],
            "accuracy": round((entry.get("accuracy") or 0.0) * 100, 1),
            "eats": round(entry.get("eats_score") or 0.0, 3),
            "n_samples": entry["n_samples"],
            "created_at": entry["created_at"],
            "cost_per_query_usd": round(entry.get("avg_cost_per_sample_usd") or 0.0, 6),
            "latency_ms": round(
                entry.get("avg_algorithmic_latency_ms")
                or entry.get("avg_latency_ms")
                or 0.0,
                1,
            ),
            "energy_kwh_per_sample": round(entry.get("avg_energy_per_sample_kwh") or 0.0, 6),
            "llm_call_ratio": round(entry.get("llm_call_ratio") or 0.0, 3),
        }

    return {
        "benchmark": BENCHMARK_DISPLAY_NAMES.get(benchmark, benchmark),
        "benchmark_key": benchmark,
        "eats_leader": compact(eats_leader),
        "accuracy_leader": compact(accuracy_leader),
        "novel_leader": compact(novel_leader),
    }


def write_outputs(by_benchmark: dict[str, list[dict]], skipped: list[dict]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_benchmarks: dict[str, dict] = {}
    panels: list[dict] = []

    for benchmark in STUDY_BENCHMARKS:
        entries = by_benchmark.get(benchmark, [])

        table = {
            "benchmark": benchmark,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "selection_rule": "latest run per benchmark x architecture with n_total >= 100",
            "scoring_rule": "canonical runner/web EATS from experiment metrics (cost + latency + energy normalized to the run baseline)",
            "min_total_samples_required": MIN_TOTAL_SAMPLES,
            "n_architectures": len(entries),
            "entries": entries,
        }
        out_path = OUTPUT_DIR / f"latest_benchmark_{benchmark}.json"
        out_path.write_text(json.dumps(table, indent=2), encoding="utf-8")

        summary_benchmarks[benchmark] = {
            "benchmark_display_name": BENCHMARK_DISPLAY_NAMES.get(benchmark, benchmark),
            "n_architectures": len(entries),
            "output": str(out_path),
        }
        print(f"[{benchmark}] wrote {len(entries)} latest entries -> {out_path}")

        if entries:
            panels.append(build_panel_summary(benchmark, entries))

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "selection_rule": "latest run per benchmark x architecture with n_total >= 100",
        "scoring_rule": "canonical runner/web EATS from experiment metrics",
        "min_total_samples_required": MIN_TOTAL_SAMPLES,
        "benchmarks": summary_benchmarks,
        "n_skipped_below_min_samples": len(skipped),
        "skipped_below_min_samples_preview": skipped[:20],
    }
    summary_path = OUTPUT_DIR / "latest_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Summary -> {summary_path}")

    panels_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "selection_rule": "latest run per benchmark x architecture with n_total >= 100",
        "scoring_rule": "canonical runner/web EATS from experiment metrics",
        "panels": panels,
    }
    panels_path = OUTPUT_DIR / "latest_panels.json"
    panels_path.write_text(json.dumps(panels_payload, indent=2), encoding="utf-8")
    print(f"Panels -> {panels_path}")


def main() -> None:
    by_benchmark, skipped = load_latest_qualified_runs()
    write_outputs(by_benchmark, skipped)


if __name__ == "__main__":
    main()
