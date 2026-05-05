"""Main statistical analysis runner.

Reads all experiment result JSONs from a results/ directory, runs ANOVA,
Tukey HSD, Cohen's d, Pareto frontier, and writes summary CSVs.

Usage:
    python analysis/statistical_analysis.py --results results/ --output analysis/output/
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from evaluation.statistics import run_analysis


def _load_results(results_dir: str) -> dict[str, list[float]]:
    """Load per-query accuracy values keyed by setup name."""
    groups: dict[str, list[float]] = {}
    for path in Path(results_dir).glob("*.json"):
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        setup = data.get("config", {}).get("architecture", path.stem)
        samples = data.get("samples", [])
        acc_vals = [1.0 if s.get("correct") else 0.0 for s in samples]
        if acc_vals:
            groups.setdefault(setup, []).extend(acc_vals)
    return groups


def _load_costs(results_dir: str) -> dict[str, float]:
    costs: dict[str, float] = {}
    for path in Path(results_dir).glob("*.json"):
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        setup = data.get("config", {}).get("architecture", path.stem)
        metrics = data.get("metrics", {})
        costs[setup] = metrics.get("normalized_cost", 1.0)
    return costs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="results/")
    parser.add_argument("--output", default="analysis/output/")
    args = parser.parse_args()

    Path(args.output).mkdir(parents=True, exist_ok=True)
    groups = _load_results(args.results)
    costs = _load_costs(args.results)

    if len(groups) < 2:
        print("Need at least 2 experiment result files. Aborting.")
        return

    analysis = run_analysis(groups, costs)

    # Write JSON
    out_json = Path(args.output) / "analysis_results.json"
    out_json.write_text(json.dumps(analysis, indent=2))
    print(f"Analysis written to {out_json}")

    # Write CSVs
    _write_csv(
        Path(args.output) / "anova_results.csv",
        ["test", "f_or_h", "p_value", "significant"],
        [[analysis["test_used"], analysis["anova"]["f"], analysis["anova"]["p"], analysis["anova"]["significant"]]],
    )
    _write_csv(
        Path(args.output) / "tukey_hsd.csv",
        ["group_a", "group_b", "mean_diff", "p_value", "significant"],
        [[r["a"], r["b"], r["diff"], r["p"], r["sig"]] for r in analysis["tukey"]],
    )
    _write_csv(
        Path(args.output) / "cohens_d.csv",
        ["group_a", "group_b", "cohens_d", "interpretation"],
        [[e["a"], e["b"], e["d"], e["interp"]] for e in analysis["effect_sizes"]],
    )
    _write_csv(
        Path(args.output) / "pareto_frontier.csv",
        ["label", "accuracy", "normalized_cost", "is_pareto"],
        [[p["label"], p["accuracy"], p["cost"], p["pareto"]] for p in analysis["pareto"]],
    )
    print("CSVs written.")


def _write_csv(path: Path, headers: list, rows: list) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


if __name__ == "__main__":
    main()
