"""
EATS weight sensitivity and validity analysis (Route A).

The EATS efficiency weights (w_C, w_L, w_E) and the outer scale lambda are
preference parameters, not fitted quantities: they encode a cost-primary
deployment prior. Rather than calibrate them against the architecture outputs
(which would be circular), this script validates the resulting metric against
objective desiderata and reports how robust the architecture ranking is to the
weight choice.

It reads the aggregate benchmark tables in results/benchmark_tables/ (the same
inputs that feed the Chapter 4 result tables) and reports, per benchmark:

  1. Dominance consistency  -- for every Pareto-dominating pair (A >= acc and
     A <= cost, latency, energy, with at least one strict), EATS(A) > EATS(B)
     must hold. A valid composite metric never reverses a dominance.
  2. Discrimination          -- spread of EATS values and the count of near-ties
     (|dEATS| < 0.01), i.e. whether the metric actually separates configs.
  3. Sensitivity             -- over a grid of weights within +/-0.10 of the
     default (step 0.05, simplex-constrained) and lambda in {0.30..0.50}, how
     often the top-1 and top-3 EATS configurations are unchanged, and the mean
     Kendall tau-b between each grid ranking and the default ranking.

Normalisation matches scripts/build_benchmark_tables.py (aggregate mode: each
metric is divided by the mean of the monolithic standalone runs on that
benchmark).
"""

from __future__ import annotations

import json
import os
from itertools import product

try:
    from scipy.stats import kendalltau
except Exception:  # pragma: no cover - scipy is available in the project venv
    kendalltau = None

TABLES_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "benchmark_tables")
BENCHMARKS = ["mmlu", "arc", "gsm8k", "hellaswag", "truthfulqa"]

# Canonical default operating point (Chapter 3 / evaluation.metrics).
DEFAULT_WC, DEFAULT_WL, DEFAULT_WE = 0.65, 0.20, 0.15
DEFAULT_LAMBDA = 0.40

NEIGHBOURHOOD = 0.10  # +/- range for the sensitivity sweep
STEP = 0.05


def eats(acc, nc, nl, ne, wc, wl, we, lam):
    beta = 1.0 - lam
    p_eff = wc * max(nc, 0.0) + wl * max(nl, 0.0) + we * max(ne, 0.0)
    denom = acc + lam * p_eff + beta * (1.0 - acc)
    return acc / denom if denom > 0 else 0.0


def load_benchmark(bench):
    path = os.path.join(TABLES_DIR, f"benchmark_{bench}.json")
    with open(path, encoding="utf-8") as f:
        table = json.load(f)
    rows = []
    for e in table["entries"]:
        if None in (
            e.get("accuracy"),
            e.get("avg_cost_per_sample_usd"),
            e.get("avg_latency_ms"),
            e.get("avg_energy_per_sample_kwh"),
        ):
            continue
        rows.append(
            {
                "key": f"{e['architecture']}|{e['model_key']}",
                "arch": e["architecture"],
                "acc": e["accuracy"],
                "cost": e["avg_cost_per_sample_usd"],
                "lat": e["avg_latency_ms"],
                "energy": e["avg_energy_per_sample_kwh"],
            }
        )
    mono = [r for r in rows if r["arch"] == "monolithic"]
    ref_cost = sum(r["cost"] for r in mono) / len(mono)
    ref_lat = sum(r["lat"] for r in mono) / len(mono)
    ref_energy = sum(r["energy"] for r in mono) / len(mono)
    for r in rows:
        r["nc"] = r["cost"] / ref_cost
        r["nl"] = r["lat"] / ref_lat
        r["ne"] = r["energy"] / ref_energy
    return rows


def score_all(rows, wc, wl, we, lam):
    for r in rows:
        r_eats = eats(r["acc"], r["nc"], r["nl"], r["ne"], wc, wl, we, lam)
        r["eats"] = r_eats
    return sorted(rows, key=lambda r: -r["eats"])


def dominance_violations(rows):
    viol = 0
    pairs = 0
    for a in rows:
        for b in rows:
            if a is b:
                continue
            ge_acc = a["acc"] >= b["acc"]
            le_res = a["cost"] <= b["cost"] and a["lat"] <= b["lat"] and a["energy"] <= b["energy"]
            strict = (
                a["acc"] > b["acc"]
                or a["cost"] < b["cost"]
                or a["lat"] < b["lat"]
                or a["energy"] < b["energy"]
            )
            if ge_acc and le_res and strict:
                pairs += 1
                if not (a["eats"] > b["eats"]):
                    viol += 1
    return viol, pairs


def near_ties(rows, eps=0.01):
    vals = sorted(r["eats"] for r in rows)
    return sum(1 for i in range(1, len(vals)) if abs(vals[i] - vals[i - 1]) < eps)


def grid_points():
    lo = round(0.05, 2)
    vals = [round(x, 2) for x in frange(lo, 0.95, STEP)]
    pts = []
    for wc, wl in product(vals, vals):
        we = round(1.0 - wc - wl, 2)
        if we < lo or we > 0.95:
            continue
        if (
            abs(wc - DEFAULT_WC) <= NEIGHBOURHOOD + 1e-9
            and abs(wl - DEFAULT_WL) <= NEIGHBOURHOOD + 1e-9
            and abs(we - DEFAULT_WE) <= NEIGHBOURHOOD + 1e-9
        ):
            pts.append((wc, wl, we))
    lambdas = [round(DEFAULT_LAMBDA + d, 2) for d in (-0.10, -0.05, 0.0, 0.05, 0.10)]
    return [(wc, wl, we, lam) for (wc, wl, we) in pts for lam in lambdas]


def frange(start, stop, step):
    x = start
    while x <= stop + 1e-9:
        yield x
        x += step


def main():
    grid = grid_points()
    print(f"Sensitivity grid: {len(grid)} weight settings within +/-{NEIGHBOURHOOD} of default\n")

    overall = {"top1_stable": 0, "top3_stable": 0, "tau_sum": 0.0, "tau_n": 0, "dom_viol": 0, "dom_pairs": 0}

    for bench in BENCHMARKS:
        rows = load_benchmark(bench)
        default_ranking = score_all(rows, DEFAULT_WC, DEFAULT_WL, DEFAULT_WE, DEFAULT_LAMBDA)
        default_keys = [r["key"] for r in default_ranking]
        default_top1 = default_keys[0]
        default_top3 = set(default_keys[:3])
        # Snapshot default EATS before the grid loop mutates the row dicts.
        default_eats = {r["key"]: r["eats"] for r in default_ranking}

        dv, dp = dominance_violations(rows)
        nt = near_ties(rows)
        spread = default_eats[default_keys[0]] - default_eats[default_keys[-1]]

        top1_stable = top3_stable = 0
        taus = []
        for (wc, wl, we, lam) in grid:
            ranking = score_all(rows, wc, wl, we, lam)
            keys = [r["key"] for r in ranking]
            if keys[0] == default_top1:
                top1_stable += 1
            if set(keys[:3]) == default_top3:
                top3_stable += 1
            if kendalltau is not None:
                rank_default = {k: i for i, k in enumerate(default_keys)}
                tau, _ = kendalltau(
                    [rank_default[k] for k in default_keys],
                    [rank_default[k] for k in keys],
                )
                if tau is not None and tau == tau:  # not NaN
                    taus.append(tau)

        n = len(grid)
        mean_tau = sum(taus) / len(taus) if taus else float("nan")
        print(f"=== {bench.upper()} ({len(rows)} configs) ===")
        print(f"  default top-1: {default_top1}  (EATS {default_eats[default_top1]:.3f})")
        print(f"  dominance: {dp - dv}/{dp} pairs respected ({dv} violations)")
        print(f"  discrimination: EATS spread {spread:.3f}, near-ties(<0.01) {nt}")
        print(f"  top-1 unchanged across grid: {top1_stable}/{n} ({100*top1_stable/n:.0f}%)")
        print(f"  top-3 set unchanged across grid: {top3_stable}/{n} ({100*top3_stable/n:.0f}%)")
        print(f"  mean Kendall tau-b vs default ranking: {mean_tau:.3f}\n")

        overall["top1_stable"] += top1_stable
        overall["top3_stable"] += top3_stable
        overall["tau_sum"] += sum(taus)
        overall["tau_n"] += len(taus)
        overall["dom_viol"] += dv
        overall["dom_pairs"] += dp

    n_total = len(grid) * len(BENCHMARKS)
    print("=== OVERALL ===")
    print(f"  dominance: {overall['dom_pairs'] - overall['dom_viol']}/{overall['dom_pairs']} pairs respected ({overall['dom_viol']} violations)")
    print(f"  top-1 unchanged: {overall['top1_stable']}/{n_total} ({100*overall['top1_stable']/n_total:.0f}%)")
    print(f"  top-3 set unchanged: {overall['top3_stable']}/{n_total} ({100*overall['top3_stable']/n_total:.0f}%)")
    print(f"  mean Kendall tau-b: {overall['tau_sum']/overall['tau_n']:.3f}")


if __name__ == "__main__":
    main()
