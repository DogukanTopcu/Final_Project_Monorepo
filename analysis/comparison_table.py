"""
Reads experiment result JSONs and prints a 4-metric comparison table.

Usage:
    python -m analysis.comparison_table results/
    python -m analysis.comparison_table results/ --format markdown
    python -m analysis.comparison_table results/ --benchmark mmlu --format csv
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load_results(results_dir: Path, benchmark_filter: str | None) -> list[dict]:
    rows = []
    for json_path in sorted(results_dir.glob("*.json")):
        try:
            data = json.loads(json_path.read_text())
        except Exception:
            continue
        cfg = data.get("config", {})
        m = data.get("metrics", {})
        if not cfg or not m:
            continue
        if benchmark_filter and cfg.get("benchmark") != benchmark_filter:
            continue
        rows.append({
            "experiment_id": data.get("experiment_id", json_path.stem),
            "architecture": cfg.get("architecture", "?"),
            "benchmark": cfg.get("benchmark", "?"),
            "n_samples": cfg.get("n_samples", 0),
            "slm": cfg.get("slm") or "—",
            "llm": cfg.get("llm") or "—",
            # Accuracy
            "accuracy": m.get("accuracy", 0.0),
            "ci_low": m.get("accuracy_ci_low_95", 0.0),
            "ci_high": m.get("accuracy_ci_high_95", 0.0),
            # Latency
            "latency_avg_ms": m.get("avg_latency_ms", 0.0),
            "latency_algo_ms": m.get("avg_algorithmic_latency_ms", 0.0),
            "latency_p95_ms": m.get("latency_p95_ms", 0.0),
            "throughput_tok_s": m.get("throughput_tokens_per_sec", 0.0),
            # Cost
            "cost_per_query_usd": m.get("cost_per_query_usd", 0.0),
            "cost_total_usd": m.get("total_cost_usd", 0.0),
            "cost_slm_api_usd": m.get("total_slm_api_cost_usd", 0.0),
            "cost_llm_api_usd": m.get("total_llm_api_cost_usd", 0.0),
            "cost_slm_path_usd": m.get("cost_slm_path_usd", 0.0),
            "cost_escalated_path_usd": m.get("cost_escalated_path_usd", 0.0),
            "cost_normalized": m.get("normalized_cost", 1.0),
            # Energy
            "energy_kwh": m.get("total_energy_kwh", 0.0),
            "joules_per_output_token": m.get("joules_per_output_token", 0.0),
            "co2_g": m.get("total_co2_g", 0.0),
            "energy_normalized": m.get("normalized_energy", 1.0),
            # Summary
            "eats_score": m.get("eats_score", 0.0),
            "escalation_rate": m.get("escalation_rate", 0.0),
        })
    return rows


def _fmt_pct(v: float) -> str:
    return f"{v:.1%}"


def _fmt_ci(row: dict) -> str:
    return f"[{row['ci_low']:.1%}, {row['ci_high']:.1%}]"


def _markdown_table(rows: list[dict]) -> str:
    if not rows:
        return "_No results found._"

    header = (
        "| Architecture | Benchmark | N | "
        "Accuracy | 95% CI | "
        "Latency p95 (ms) | Throughput (tok/s) | "
        "Cost/query ($) | % of monolithic | SLM API ($) | LLM API ($) | "
        "J/output token | CO₂ (g) | "
        "EATS |"
    )
    sep = "|---|" * 14 + "|"
    lines = [header, sep]
    for r in rows:
        cost_pct = f"{r['cost_normalized'] * 100:.1f}%"
        lines.append(
            f"| {r['architecture']} | {r['benchmark']} | {r['n_samples']} | "
            f"{_fmt_pct(r['accuracy'])} | {_fmt_ci(r)} | "
            f"{r['latency_p95_ms']:.0f} | {r['throughput_tok_s']:.1f} | "
            f"${r['cost_per_query_usd']:.6f} | {cost_pct} | ${r['cost_slm_api_usd']:.4f} | ${r['cost_llm_api_usd']:.4f} | "
            f"{r['joules_per_output_token']:.4f} | {r['co2_g']:.3f} | "
            f"{r['eats_score']:.4f} |"
        )
    return "\n".join(lines)


def _csv_table(rows: list[dict]) -> str:
    if not rows:
        return ""
    cols = [
        "experiment_id", "architecture", "benchmark", "n_samples",
        "accuracy", "ci_low", "ci_high",
        "latency_avg_ms", "latency_p95_ms", "latency_algo_ms", "throughput_tok_s",
        "cost_per_query_usd", "cost_total_usd", "cost_slm_api_usd", "cost_llm_api_usd",
        "cost_slm_path_usd", "cost_escalated_path_usd", "cost_normalized",
        "energy_kwh", "joules_per_output_token", "co2_g", "energy_normalized",
        "eats_score", "escalation_rate",
    ]
    lines = [",".join(cols)]
    for r in rows:
        lines.append(",".join(str(r.get(c, "")) for c in cols))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Print 4-metric comparison table from result JSONs.")
    parser.add_argument("results_dir", type=Path, help="Directory containing experiment JSON files")
    parser.add_argument("--benchmark", default=None, help="Filter to a specific benchmark name")
    parser.add_argument("--format", choices=["markdown", "csv"], default="markdown")
    args = parser.parse_args()

    if not args.results_dir.is_dir():
        print(f"Error: {args.results_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    rows = _load_results(args.results_dir, args.benchmark)
    if not rows:
        print("No matching experiment results found.", file=sys.stderr)
        sys.exit(1)

    if args.format == "csv":
        print(_csv_table(rows))
    else:
        print(_markdown_table(rows))


if __name__ == "__main__":
    main()
