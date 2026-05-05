"""Energy and Green AI report generator.

Reads experiment results and emissions.csv from CodeCarbon, produces a
Markdown summary with: total kWh, CO2 equivalent, AP/T, Tokens/kWh.

Usage:
    python analysis/energy_report.py --results results/ --output reports/energy_report.md
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="results/")
    parser.add_argument("--emissions-csv", default="emissions.csv")
    parser.add_argument("--output", default="reports/energy_report.md")
    args = parser.parse_args()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    for path in sorted(Path(args.results).glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        setup = data.get("config", {}).get("architecture", path.stem)
        benchmark = data.get("config", {}).get("benchmark", "unknown")
        metrics = data.get("metrics", {})
        rows.append({
            "setup": setup,
            "benchmark": benchmark,
            "accuracy": metrics.get("accuracy", 0.0),
            "energy_kwh": metrics.get("energy_kwh", 0.0),
            "co2_g": metrics.get("co2_g", 0.0),
            "tokens_per_kwh": metrics.get("tokens_per_kwh", 0.0),
            "total_tokens": metrics.get("total_tokens", 0),
        })

    lines: list[str] = ["# Energy & Green AI Report\n"]

    if rows:
        lines.append("## Per-Experiment Summary\n")
        lines.append("| Setup | Benchmark | Accuracy | Energy (kWh) | CO₂ (g) | Tokens/kWh |")
        lines.append("|-------|-----------|----------|-------------|---------|------------|")
        for r in rows:
            lines.append(
                f"| {r['setup']} | {r['benchmark']} | {r['accuracy']:.3f} "
                f"| {r['energy_kwh']:.4f} | {r['co2_g']:.2f} | {r['tokens_per_kwh']:.0f} |"
            )
        lines.append("")

    # Aggregate by setup
    from collections import defaultdict
    agg: dict[str, dict] = defaultdict(lambda: {"energy_kwh": 0.0, "co2_g": 0.0, "tokens": 0})
    for r in rows:
        agg[r["setup"]]["energy_kwh"] += r["energy_kwh"]
        agg[r["setup"]]["co2_g"] += r["co2_g"]
        agg[r["setup"]]["tokens"] += r["total_tokens"]

    lines.append("## Total Energy by Setup\n")
    lines.append("| Setup | Total kWh | Total CO₂ (g) | Avg Tokens/kWh |")
    lines.append("|-------|-----------|--------------|----------------|")
    for setup, vals in agg.items():
        tpk = vals["tokens"] / vals["energy_kwh"] if vals["energy_kwh"] > 0 else 0.0
        lines.append(f"| {setup} | {vals['energy_kwh']:.4f} | {vals['co2_g']:.2f} | {tpk:.0f} |")
    lines.append("")

    # CodeCarbon emissions.csv summary if present
    if Path(args.emissions_csv).exists():
        lines.append("## CodeCarbon Emissions Summary\n")
        with open(args.emissions_csv) as f:
            reader = csv.DictReader(f)
            cc_rows = list(reader)
        if cc_rows:
            lines.append("| Project | Duration (s) | Emissions (kgCO₂) | Energy (kWh) |")
            lines.append("|---------|-------------|-------------------|-------------|")
            for row in cc_rows[-10:]:
                lines.append(
                    f"| {row.get('project_name', '')} "
                    f"| {row.get('duration', '')} "
                    f"| {row.get('emissions', '')} "
                    f"| {row.get('energy_consumed', '')} |"
                )
        lines.append("")

    Path(args.output).write_text("\n".join(lines))
    print(f"Energy report written to {args.output}")


if __name__ == "__main__":
    main()
