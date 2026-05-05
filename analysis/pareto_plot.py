"""Pareto frontier visualization — Accuracy vs Normalized Cost.

Usage:
    python analysis/pareto_plot.py --results results/ --output figures/
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="results/")
    parser.add_argument("--output", default="figures/")
    args = parser.parse_args()

    Path(args.output).mkdir(parents=True, exist_ok=True)

    try:
        import matplotlib.pyplot as plt  # type: ignore
        import matplotlib.patches as mpatches  # type: ignore
    except ImportError:
        print("matplotlib not installed — skipping plot. Run: pip install matplotlib")
        return

    from evaluation.statistics import ParetoPoint, pareto_frontier

    points: list[ParetoPoint] = []
    for path in Path(args.results).glob("*.json"):
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        setup = data.get("config", {}).get("architecture", path.stem)
        metrics = data.get("metrics", {})
        acc = metrics.get("accuracy", 0.0)
        cost = metrics.get("normalized_cost", 1.0)
        points.append(ParetoPoint(label=setup, accuracy=acc, normalized_cost=cost))

    if not points:
        print("No result files found.")
        return

    pareto_frontier(points)

    fig, ax = plt.subplots(figsize=(8, 6))
    colors = plt.cm.tab10.colors  # type: ignore

    for i, pt in enumerate(points):
        color = colors[i % len(colors)]
        marker = "*" if pt.is_pareto else "o"
        size = 200 if pt.is_pareto else 80
        ax.scatter(pt.normalized_cost, pt.accuracy, c=[color], marker=marker, s=size, zorder=3)
        ax.annotate(pt.label, (pt.normalized_cost, pt.accuracy), textcoords="offset points", xytext=(6, 4), fontsize=9)

    pareto_pts = sorted([p for p in points if p.is_pareto], key=lambda p: p.normalized_cost)
    if len(pareto_pts) >= 2:
        xs = [p.normalized_cost for p in pareto_pts]
        ys = [p.accuracy for p in pareto_pts]
        ax.step(xs, ys, where="post", color="black", linewidth=1.5, linestyle="--", label="Pareto frontier")

    ax.set_xlabel("Normalized Cost (lower is better)")
    ax.set_ylabel("Accuracy (higher is better)")
    ax.set_title("Pareto Frontier: Accuracy vs Cost")
    ax.legend()
    ax.grid(alpha=0.3)

    out = Path(args.output) / "pareto_frontier.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
