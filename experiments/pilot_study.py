"""Pilot study — 100 stratified queries to calibrate confidence thresholds.

Runs Setup A (routing) and Setup C (speculative decoding) across thresholds
[0.70, 0.75, 0.80] and reports EATS score + accuracy for each.

The optimal threshold is written back to the YAML config files.

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
    slm_id: str = "llama3-8b",
    llm_id: str = "llama3-70b",
) -> dict:
    if thresholds is None:
        thresholds = [0.70, 0.75, 0.80]

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    benchmark = CustomStratifiedBenchmark(seed=42)
    queries = benchmark.load()[:n_queries]

    slm = get_model(slm_id)
    llm = get_model(llm_id)

    results: dict[str, dict[float, dict]] = {"routing": {}, "speculative": {}}

    for threshold in thresholds:
        print(f"\n--- Threshold {threshold} ---")

        # Setup A: Routing
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
        a_eats = compute_eats(a_acc, a_ratio)
        results["routing"][threshold] = {"accuracy": a_acc, "llm_ratio": a_ratio, "eats": a_eats}
        print(f"  Routing    acc={a_acc:.3f}  llm_ratio={a_ratio:.3f}  EATS={a_eats:.3f}")

        # Setup C: Speculative Decoding
        from architectures.speculative_decoding import SpeculativeDecodingArchitecture
        arch_c = SpeculativeDecodingArchitecture(confidence_threshold=threshold)
        c_correct = 0
        c_llm_calls = 0
        for q in queries:
            resp = arch_c.run(q)
            gt = q.answer.strip().upper() if q.choices else q.answer.strip()
            pred = (resp.predicted_answer or "").strip()
            correct = (gt == pred.upper()) if q.choices else _approx_equal(gt, pred)
            if correct:
                c_correct += 1
            c_llm_calls += resp.llm_calls
        c_acc = c_correct / n_queries
        c_ratio = c_llm_calls / n_queries
        c_eats = compute_eats(c_acc, c_ratio)
        results["speculative"][threshold] = {"accuracy": c_acc, "llm_ratio": c_ratio, "eats": c_eats}
        print(f"  Speculative acc={c_acc:.3f}  llm_ratio={c_ratio:.3f}  EATS={c_eats:.3f}")

    # Select best threshold per architecture
    best_a = max(results["routing"], key=lambda t: results["routing"][t]["eats"])
    best_c = max(results["speculative"], key=lambda t: results["speculative"][t]["eats"])
    print(f"\nBest threshold for Routing: {best_a}")
    print(f"Best threshold for Speculative: {best_c}")

    summary = {
        "n_queries": n_queries,
        "thresholds_tested": thresholds,
        "results": {k: {str(t): v for t, v in inner.items()} for k, inner in results.items()},
        "best_threshold_routing": best_a,
        "best_threshold_speculative": best_c,
    }

    out_path = Path(output_dir) / "pilot_summary.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nPilot results written to {out_path}")

    _update_configs(best_a, best_c)
    return summary


def _approx_equal(a: str, b: str, tol: float = 1e-4) -> bool:
    try:
        return abs(float(a) - float(b)) < tol
    except ValueError:
        return a.strip().lower() == b.strip().lower()


def _update_configs(routing_threshold: float, speculative_threshold: float) -> None:
    import yaml  # type: ignore
    for path, key, value in [
        ("experiments/configs/arch_a.yaml", "confidence_threshold", routing_threshold),
        ("experiments/configs/arch_c.yaml", "confidence_threshold", speculative_threshold),
    ]:
        if os.path.exists(path):
            with open(path) as f:
                cfg = yaml.safe_load(f) or {}
            cfg[key] = value
            with open(path, "w") as f:
                yaml.dump(cfg, f)
            print(f"Updated {path}: {key}={value}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-queries", type=int, default=100)
    parser.add_argument("--thresholds", nargs="+", type=float, default=[0.70, 0.75, 0.80])
    parser.add_argument("--output", default="pilot_results")
    parser.add_argument("--slm", default="llama3-8b")
    parser.add_argument("--llm", default="llama3-70b")
    args = parser.parse_args()

    run_pilot(
        n_queries=args.n_queries,
        thresholds=args.thresholds,
        output_dir=args.output,
        slm_id=args.slm,
        llm_id=args.llm,
    )
