from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

from evaluation.baselines import LATENCY_SOURCE_ALGORITHMIC, save_baseline

BENCHMARKS = ("mmlu", "arc", "hellaswag", "gsm8k", "truthfulqa")


def load_manifest(path: str | Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(Path(path).read_text())
    if not isinstance(data, dict) or not isinstance(data.get("runs"), list):
        raise ValueError("Manifest must be a mapping with a 'runs' list")
    runs = data["runs"]
    validate_manifest(runs)
    return runs


def validate_manifest(runs: list[dict[str, Any]]) -> None:
    if len(runs) != 35:
        raise ValueError(f"Expected 35 runs in monolithic sweep manifest, found {len(runs)}")
    seen = set()
    valid_models = {
        "gpt-oss-120b",
        "llama3.3-70b",
        "qwen3.5-27b",
        "gpt-oss-20b",
        "gemma4-31b",
        "gemma4-26b-a4b",
        "qwen3.5-35b-a3b",
    }
    for run in runs:
        run_id = str(run.get("run_id", "")).strip()
        if not run_id or run_id in seen:
            raise ValueError(f"Duplicate or missing run_id: {run_id!r}")
        seen.add(run_id)
        if run.get("architecture") != "monolithic":
            raise ValueError(f"Run {run_id} must use architecture=monolithic")
        benchmark = str(run.get("benchmark"))
        if benchmark not in BENCHMARKS:
            raise ValueError(f"Run {run_id} has unsupported benchmark: {benchmark}")
        llm = str(run.get("llm"))
        if llm not in valid_models:
            raise ValueError(f"Run {run_id} has unsupported llm alias: {llm}")


def _load_result(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text())
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def result_matches_run(result_data: dict[str, Any], run: dict[str, Any]) -> bool:
    config = result_data.get("config", {})
    return (
        config.get("architecture") == "monolithic"
        and config.get("benchmark") == run["benchmark"]
        and config.get("llm") == run["llm"]
        and int(config.get("n_samples", -1)) == int(run["n_samples"])
        and int(config.get("seed", -1)) == int(run["seed"])
        and float(config.get("llm_temperature", -1.0)) == float(run["llm_temperature"])
        and int(config.get("llm_max_tokens", -1)) == int(run["llm_max_tokens"])
    )


def find_matching_results(run: dict[str, Any], results_dir: str | Path) -> list[Path]:
    matches: list[Path] = []
    for path in sorted(Path(results_dir).glob("*.json")):
        result_data = _load_result(path)
        if result_data and result_matches_run(result_data, run):
            matches.append(path)
    return matches


def extract_summary_row(run: dict[str, Any], result_path: Path) -> dict[str, Any]:
    data = _load_result(result_path)
    if data is None:
        raise ValueError(f"Failed to parse result file: {result_path}")
    metrics = data.get("metrics", {})
    return {
        "run_id": run["run_id"],
        "experiment_id": data.get("experiment_id", result_path.stem),
        "architecture": "monolithic",
        "benchmark": run["benchmark"],
        "llm": run["llm"],
        "model_family": run["model_family"],
        "model_class": run["model_class"],
        "n_samples": int(run["n_samples"]),
        "seed": int(run["seed"]),
        "llm_temperature": float(run["llm_temperature"]),
        "llm_max_tokens": int(run["llm_max_tokens"]),
        "latency_source": LATENCY_SOURCE_ALGORITHMIC,
        "accuracy": float(metrics.get("accuracy", 0.0)),
        "avg_algorithmic_latency_ms": float(metrics.get("avg_algorithmic_latency_ms", 0.0)),
        "avg_latency_ms": float(metrics.get("avg_latency_ms", 0.0)),
        "total_cost_usd": float(metrics.get("total_cost_usd", 0.0)),
        "total_energy_kwh": float(metrics.get("total_energy_kwh", 0.0)),
        "total_co2_g": float(metrics.get("total_co2_g", 0.0)),
        "created_at": data.get("created_at"),
        "result_path": str(result_path),
        "query_set_hash": data.get("config", {}).get("query_set_hash"),
    }


def write_baseline_registry(
    rows: list[dict[str, Any]],
    index_path: str | Path,
) -> list[dict[str, Any]]:
    saved: list[dict[str, Any]] = []
    for row in rows:
        saved.append(save_baseline(index_path, row))
    return saved


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0 or numerator < 0:
        return 1.0
    return numerator / denominator


def _accuracy_norm(values: list[float], value: float) -> float:
    lo = min(values)
    hi = max(values)
    if hi == lo:
        return 1.0
    return (value - lo) / (hi - lo)


def compute_llm_benchmark_scores(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["benchmark"])].append(dict(row))

    scored_rows: list[dict[str, Any]] = []
    for benchmark, items in grouped.items():
        accuracies = [float(item["accuracy"]) for item in items]
        min_cost = min(float(item["total_cost_usd"]) for item in items if float(item["total_cost_usd"]) > 0)
        min_latency = min(
            float(item["avg_algorithmic_latency_ms"])
            for item in items
            if float(item["avg_algorithmic_latency_ms"]) > 0
        )
        min_energy = min(float(item["total_energy_kwh"]) for item in items if float(item["total_energy_kwh"]) > 0)

        ranked_items: list[dict[str, Any]] = []
        for item in items:
            accuracy_norm = _accuracy_norm(accuracies, float(item["accuracy"]))
            cost_eff = _safe_ratio(min_cost, float(item["total_cost_usd"]))
            latency_eff = _safe_ratio(min_latency, float(item["avg_algorithmic_latency_ms"]))
            energy_eff = _safe_ratio(min_energy, float(item["total_energy_kwh"]))
            score = (
                0.35 * accuracy_norm
                + 0.25 * cost_eff
                + 0.20 * latency_eff
                + 0.20 * energy_eff
            )
            scored = dict(item)
            scored["accuracy_norm"] = accuracy_norm
            scored["cost_eff"] = cost_eff
            scored["latency_eff"] = latency_eff
            scored["energy_eff"] = energy_eff
            scored["llm_benchmark_score"] = score
            ranked_items.append(scored)

        ranked_items.sort(key=lambda item: (-float(item["llm_benchmark_score"]), item["llm"]))
        for idx, item in enumerate(ranked_items, start=1):
            item["benchmark_rank"] = idx
            scored_rows.append(item)
    return scored_rows


def select_recommended_dense_references(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["model_class"] == "dense_llm":
            grouped[str(row["benchmark"])].append(row)

    selected: dict[str, dict[str, Any]] = {}
    for benchmark, items in grouped.items():
        ordered = sorted(
            items,
            key=lambda item: (
                -float(item["accuracy"]),
                float(item["avg_algorithmic_latency_ms"]),
                float(item["total_cost_usd"]),
                str(item["llm"]),
            ),
        )
        selected[benchmark] = ordered[0]
    return selected


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(path: Path, rows: list[dict[str, Any]], title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", ""]
    if not rows:
        lines.append("No rows.")
        path.write_text("\n".join(lines))
        return
    headers = list(rows[0].keys())
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows:
        values = [str(row.get(header, "")) for header in headers]
        lines.append("| " + " | ".join(values) + " |")
    path.write_text("\n".join(lines))


def build_dense_vs_moe_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["benchmark"])].append(row)
    summary: list[dict[str, Any]] = []
    for benchmark, items in grouped.items():
        dense = [item for item in items if item["model_class"] == "dense_llm"]
        moe = [item for item in items if item["model_class"] == "moe"]
        best_dense = max(dense, key=lambda item: float(item["llm_benchmark_score"]))
        best_moe = max(moe, key=lambda item: float(item["llm_benchmark_score"]))
        summary.append(
            {
                "benchmark": benchmark,
                "best_dense_llm": best_dense["llm"],
                "best_dense_score": round(float(best_dense["llm_benchmark_score"]), 6),
                "best_moe": best_moe["llm"],
                "best_moe_score": round(float(best_moe["llm_benchmark_score"]), 6),
                "score_gap_moe_minus_dense": round(
                    float(best_moe["llm_benchmark_score"]) - float(best_dense["llm_benchmark_score"]),
                    6,
                ),
            }
        )
    return summary


def build_overall_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["llm"])].append(row)
    summary: list[dict[str, Any]] = []
    for llm, items in grouped.items():
        mean_rank = sum(float(item["benchmark_rank"]) for item in items) / len(items)
        mean_score = sum(float(item["llm_benchmark_score"]) for item in items) / len(items)
        summary.append(
            {
                "llm": llm,
                "model_class": items[0]["model_class"],
                "mean_rank": round(mean_rank, 6),
                "mean_llm_benchmark_score": round(mean_score, 6),
            }
        )
    summary.sort(key=lambda item: (float(item["mean_rank"]), -float(item["mean_llm_benchmark_score"])))
    return summary


def write_analysis_outputs(
    scored_rows: list[dict[str, Any]],
    recommended_refs: dict[str, dict[str, Any]],
    baseline_root: str | Path,
    output_dir: str | Path,
) -> None:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    baseline_root = Path(baseline_root)
    baseline_root.mkdir(parents=True, exist_ok=True)

    dense_vs_moe = build_dense_vs_moe_summary(scored_rows)
    overall = build_overall_summary(scored_rows)

    (out_dir / "leaderboard.json").write_text(json.dumps(scored_rows, indent=2))
    _write_csv(out_dir / "leaderboard.csv", scored_rows)
    _write_markdown(out_dir / "leaderboard.md", scored_rows, "Monolithic LLM Sweep Leaderboard")

    (out_dir / "dense_vs_moe_by_benchmark.json").write_text(json.dumps(dense_vs_moe, indent=2))
    _write_csv(out_dir / "dense_vs_moe_by_benchmark.csv", dense_vs_moe)
    _write_markdown(out_dir / "dense_vs_moe_by_benchmark.md", dense_vs_moe, "Dense vs MoE by Benchmark")

    (out_dir / "overall_summary.json").write_text(json.dumps(overall, indent=2))
    _write_csv(out_dir / "overall_summary.csv", overall)
    _write_markdown(out_dir / "overall_summary.md", overall, "Monolithic LLM Sweep Overall Summary")

    (baseline_root / "recommended_references.json").write_text(json.dumps(recommended_refs, indent=2))


def run_sweep_analysis(
    manifest_path: str | Path,
    results_dir: str | Path,
    baseline_index_path: str | Path,
    output_dir: str | Path,
) -> dict[str, Any]:
    runs = load_manifest(manifest_path)
    summary_rows: list[dict[str, Any]] = []
    for run in runs:
        matches = find_matching_results(run, results_dir)
        if not matches:
            continue
        summary_rows.append(extract_summary_row(run, matches[-1]))

    saved_baselines = write_baseline_registry(summary_rows, baseline_index_path)
    scored_rows = compute_llm_benchmark_scores(saved_baselines)
    recommended_refs = select_recommended_dense_references(scored_rows)
    write_analysis_outputs(
        scored_rows=scored_rows,
        recommended_refs=recommended_refs,
        baseline_root=Path(baseline_index_path).parent,
        output_dir=output_dir,
    )
    return {
        "rows": scored_rows,
        "recommended_references": recommended_refs,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analyze monolithic LLM/MoE sweep results")
    parser.add_argument(
        "--manifest",
        default="experiments/manifests/monolithic_llm_sweep.yaml",
    )
    parser.add_argument("--results-dir", default="results")
    parser.add_argument("--baseline-index", default="artifacts/baselines/index.json")
    parser.add_argument("--output-dir", default="analysis/outputs/monolithic_llm_sweep")
    args = parser.parse_args()

    run_sweep_analysis(
        manifest_path=args.manifest,
        results_dir=args.results_dir,
        baseline_index_path=args.baseline_index,
        output_dir=args.output_dir,
    )
