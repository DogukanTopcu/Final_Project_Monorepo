"""Plot per-benchmark accuracy/cost trade-offs from aggregated result tables.

Usage:
    python -m analysis.architecture_cost_accuracy_plot
    python -m analysis.architecture_cost_accuracy_plot \
        --tables results/benchmark_tables \
        --output docs/term_report/sources/architecture_cost_accuracy.png
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

BENCHMARKS = [
    ("mmlu", "MMLU"),
    ("arc", "ARC-Challenge"),
    ("gsm8k", "GSM8K"),
    ("hellaswag", "HellaSwag"),
    ("truthfulqa", "TruthfulQA"),
]

ACCURACY_LIMIT_OVERRIDES = {
    # Two GPT-OSS parsing outliers at 59.4% and 67.8% would otherwise compress
    # the main GSM8K cluster, where the architecture comparison is concentrated.
    "GSM8K": (84, 100),
}

ARCHITECTURE_LABELS = {
    "active_oracle": "Active Oracle",
    "ensemble": "Ensemble",
    "monolithic": "Standalone",
    "multi_agent": "Debate",
    "pure_swarm": "Pure Swarm",
    "routing": "Routing",
    "speculative": "Speculative",
}

ARCHITECTURE_STYLES = {
    "active_oracle": ("#CC79A7", "P"),
    "ensemble": ("#E69F00", "s"),
    "monolithic": ("#7F7F7F", "o"),
    "multi_agent": ("#009E73", "X"),
    "pure_swarm": ("#D55E00", "D"),
    "routing": ("#0072B2", "^"),
    "speculative": ("#56B4E9", "v"),
}


def _load_entries(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    eligible = [
        entry
        for entry in data.get("entries", [])
        if entry.get("accuracy") is not None
        and entry.get("avg_cost_per_sample_usd") is not None
        and entry["avg_cost_per_sample_usd"] > 0
        and entry.get("total_samples_evaluated", 0) >= 100
    ]
    best_by_group: dict[tuple[str, str], dict] = {}
    for entry in eligible:
        architecture = entry["architecture"]
        group_key = (
            architecture,
            entry["model_key"] if architecture == "monolithic" else architecture,
        )
        current = best_by_group.get(group_key)
        if current is None or (
            entry["accuracy"],
            -entry["avg_cost_per_sample_usd"],
        ) > (
            current["accuracy"],
            -current["avg_cost_per_sample_usd"],
        ):
            best_by_group[group_key] = entry
    return list(best_by_group.values())


def _pareto_frontier(entries: list[dict]) -> list[dict]:
    """Return points not dominated on both lower cost and higher accuracy."""
    frontier = []
    for candidate in entries:
        dominated = any(
            other["avg_cost_per_sample_usd"] <= candidate["avg_cost_per_sample_usd"]
            and other["accuracy"] >= candidate["accuracy"]
            and (
                other["avg_cost_per_sample_usd"] < candidate["avg_cost_per_sample_usd"]
                or other["accuracy"] > candidate["accuracy"]
            )
            for other in entries
        )
        if not dominated:
            frontier.append(candidate)
    return sorted(frontier, key=lambda entry: entry["avg_cost_per_sample_usd"])


def _short_model_label(entry: dict) -> str:
    model = entry.get("model_key", "")
    if entry.get("architecture") == "monolithic":
        return model
    return ARCHITECTURE_LABELS.get(entry.get("architecture", ""), entry.get("architecture", ""))


def _accuracy_limits(entries: list[dict]) -> tuple[float, float]:
    """Choose readable 5-point bounds around the observed accuracy range."""
    accuracies = [entry["accuracy"] * 100 for entry in entries]
    lower = max(0, math.floor((min(accuracies) - 2) / 5) * 5)
    upper = min(100, math.ceil((max(accuracies) + 2) / 5) * 5)
    if upper - lower < 10:
        lower = max(0, upper - 10)
    return lower, upper


def _annotate_frontier(fig, ax, frontier: list[dict]) -> None:
    """Place Pareto labels using non-overlapping callout positions."""
    candidate_offsets = [
        (6, 8),
        (6, -14),
        (-6, 8),
        (-6, -14),
        (18, 18),
        (18, -24),
        (-18, 18),
        (-18, -24),
        (30, 6),
        (-30, 6),
    ]
    occupied = []

    # Place the most crowded high-accuracy points first.
    for entry in sorted(frontier, key=lambda item: item["accuracy"], reverse=True):
        point = (
            entry["avg_cost_per_sample_usd"],
            entry["accuracy"] * 100,
        )
        selected = None
        for x_offset, y_offset in candidate_offsets:
            annotation = ax.annotate(
                _short_model_label(entry),
                point,
                xytext=(x_offset, y_offset),
                textcoords="offset points",
                fontsize=7,
                color="#222222",
                ha="left" if x_offset >= 0 else "right",
                va="bottom" if y_offset >= 0 else "top",
                arrowprops={
                    "arrowstyle": "-",
                    "color": "#777777",
                    "linewidth": 0.5,
                    "shrinkA": 2,
                    "shrinkB": 3,
                },
                zorder=4,
            )
            fig.canvas.draw()
            bbox = annotation.get_window_extent(fig.canvas.get_renderer()).expanded(1.05, 1.15)
            inside_axes = ax.get_window_extent().contains(*bbox.get_points()[0]) and (
                ax.get_window_extent().contains(*bbox.get_points()[1])
            )
            if inside_axes and not any(bbox.overlaps(previous) for previous in occupied):
                selected = bbox
                break
            annotation.remove()

        if selected is not None:
            occupied.append(selected)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot accuracy against per-query cost for each benchmark."
    )
    parser.add_argument(
        "--tables",
        type=Path,
        default=REPO_ROOT / "results" / "benchmark_tables",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "docs" / "term_report" / "sources" / "architecture_cost_accuracy.png",
    )
    args = parser.parse_args()

    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    loaded = []
    architectures = set()
    for benchmark, title in BENCHMARKS:
        entries = _load_entries(args.tables / f"benchmark_{benchmark}.json")
        loaded.append((title, entries))
        architectures.update(entry["architecture"] for entry in entries)

    fig, axes = plt.subplots(2, 3, figsize=(14, 8.2), sharey=False)
    axes_flat = list(axes.flat)

    for ax, (title, entries) in zip(axes_flat, loaded):
        for entry in entries:
            architecture = entry["architecture"]
            color, marker = ARCHITECTURE_STYLES.get(architecture, ("#333333", "o"))
            ax.scatter(
                entry["avg_cost_per_sample_usd"],
                entry["accuracy"] * 100,
                color=color,
                marker=marker,
                s=65,
                edgecolor="white",
                linewidth=0.6,
                alpha=0.9,
                zorder=3,
            )

        frontier = _pareto_frontier(entries)
        if frontier:
            ax.plot(
                [entry["avg_cost_per_sample_usd"] for entry in frontier],
                [entry["accuracy"] * 100 for entry in frontier],
                color="#222222",
                linestyle="--",
                linewidth=1.2,
                alpha=0.75,
                zorder=2,
            )

        ax.set_xscale("log")
        accuracy_limits = ACCURACY_LIMIT_OVERRIDES.get(title, _accuracy_limits(entries))
        ax.set_ylim(*accuracy_limits)
        omitted = [
            entry
            for entry in entries
            if entry["accuracy"] * 100 < accuracy_limits[0]
            or entry["accuracy"] * 100 > accuracy_limits[1]
        ]
        if omitted:
            omitted_labels = ", ".join(
                f"{_short_model_label(entry)} ({entry['accuracy'] * 100:.1f}%)"
                for entry in omitted
            )
            ax.text(
                0.02,
                0.03,
                f"Outside y-range: {omitted_labels}",
                transform=ax.transAxes,
                fontsize=6.5,
                color="#555555",
                va="bottom",
            )
        ax.set_title(title, fontweight="bold")
        ax.set_xlabel("Cost per query (USD, log scale)")
        ax.grid(True, which="both", alpha=0.22)
        ax.set_axisbelow(True)
        _annotate_frontier(fig, ax, frontier)

    axes_flat[0].set_ylabel("Accuracy (%)")
    axes_flat[3].set_ylabel("Accuracy (%)")
    axes_flat[-1].axis("off")

    legend_handles = []
    for architecture in sorted(architectures, key=lambda item: ARCHITECTURE_LABELS.get(item, item)):
        color, marker = ARCHITECTURE_STYLES.get(architecture, ("#333333", "o"))
        legend_handles.append(
            Line2D(
                [0],
                [0],
                marker=marker,
                color="none",
                markerfacecolor=color,
                markeredgecolor="white",
                markersize=8,
                label=ARCHITECTURE_LABELS.get(architecture, architecture),
            )
        )
    legend_handles.append(
        Line2D([0], [0], color="#222222", linestyle="--", label="Pareto frontier")
    )
    axes_flat[-1].legend(handles=legend_handles, loc="center", frameon=False, fontsize=10)

    fig.suptitle(
        "Architecture Trade-off: Accuracy vs. Cost",
        fontsize=16,
        fontweight="bold",
        y=0.98,
    )
    fig.text(
        0.5,
        0.02,
        "Best N>=100 result per architecture; standalone is selected per model "
        "(accuracy first, then lower cost). "
        "Higher is better for accuracy; farther left is better for cost. "
        "Y-axis ranges are fitted per benchmark; labels identify Pareto-optimal configurations.",
        ha="center",
        fontsize=10,
    )
    fig.tight_layout(rect=(0.02, 0.05, 1, 0.95))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
