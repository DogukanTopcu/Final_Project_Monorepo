"""Pilot study for routing threshold calibration.

This script reflects the currently supported experiment surface. It calibrates
the `routing` architecture by sweeping confidence thresholds over the custom
stratified benchmark.

Usage:
    python experiments/pilot_study.py \
        --n-queries 100 \
        --thresholds 0.70 0.75 0.80 \
        --output pilot_results/
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from benchmarks.custom_stratified import CustomStratifiedBenchmark
from core.models import get_model
from evaluation.metrics import compute_eats


def run_pilot(
    n_queries: int = 100,
    thresholds: list[float] | None = None,
    output_dir: str = "pilot_results",
    slm_id: str = "qwen3.5-4b",
    llm_id: str = "llama3.3-70b",
) -> dict:
    if thresholds is None:
        thresholds = [0.70, 0.75, 0.80]

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    benchmark = CustomStratifiedBenchmark(seed=42)
    queries = benchmark.load()[:n_queries]

    slm = get_model(slm_id)
    llm = get_model(llm_id)

    results: dict[str, dict[float, dict]] = {"routing": {}}

    for threshold in thresholds:
        print(f"\n--- Threshold {threshold} ---")

        from architectures.routing import RoutingArchitecture
        arch_a = RoutingArchitecture(slm=slm, llm=llm, confidence_threshold=threshold)
        a_correct = 0
        a_llm_calls = 0
        for q in queries:
            resp = arch_a.run(q)
            gt = q.answer.strip().upper()
            pred = (resp.predicted_answer or "").strip().upper()
            if gt == pred:
                a_correct += 1
            a_llm_calls += resp.llm_calls
        a_acc = a_correct / n_queries
        a_ratio = a_llm_calls / n_queries
        a_eats = compute_eats(a_acc)
        results["routing"][threshold] = {"accuracy": a_acc, "llm_ratio": a_ratio, "eats": a_eats}
        print(f"  Routing    acc={a_acc:.3f}  llm_ratio={a_ratio:.3f}  EATS={a_eats:.3f}")

    best_a = max(results["routing"], key=lambda t: results["routing"][t]["eats"])
    print(f"\nBest threshold for Routing: {best_a}")

    summary = {
        "n_queries": n_queries,
        "thresholds_tested": thresholds,
        "results": {k: {str(t): v for t, v in inner.items()} for k, inner in results.items()},
        "best_threshold_routing": best_a,
    }

    out_path = Path(output_dir) / "pilot_summary.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nPilot results written to {out_path}")

    _update_configs(best_a)
    return summary


def _approx_equal(a: str, b: str, tol: float = 1e-4) -> bool:
    try:
        return abs(float(a) - float(b)) < tol
    except ValueError:
        return a.strip().lower() == b.strip().lower()


def _update_configs(routing_threshold: float) -> None:
    import yaml  # type: ignore
    path = "experiments/configs/arch_a.yaml"
    if os.path.exists(path):
        with open(path) as f:
            cfg = yaml.safe_load(f) or {}
        cfg["confidence_threshold"] = routing_threshold
        with open(path, "w") as f:
            yaml.dump(cfg, f)
        print(f"Updated {path}: confidence_threshold={routing_threshold}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-queries", type=int, default=100)
    parser.add_argument("--thresholds", nargs="+", type=float, default=[0.70, 0.75, 0.80])
    parser.add_argument("--output", default="pilot_results")
    parser.add_argument("--slm", default="qwen3.5-4b")
    parser.add_argument("--llm", default="llama3.3-70b")
    args = parser.parse_args()

    run_pilot(
        n_queries=args.n_queries,
        thresholds=args.thresholds,
        output_dir=args.output,
        slm_id=args.slm,
        llm_id=args.llm,
    )
