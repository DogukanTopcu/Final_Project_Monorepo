"""Statistical analysis for experiment results.

Implements:
  - One-way ANOVA across setups
  - Tukey HSD post-hoc test
  - Cohen's d effect size
  - Shapiro-Wilk normality check (fallback to Kruskal-Wallis)
  - Pareto frontier computation (accuracy vs normalized cost)
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence


@dataclass
class ANOVAResult:
    f_statistic: float
    p_value: float
    significant: bool  # p < 0.05


@dataclass
class TukeyResult:
    group_a: str
    group_b: str
    mean_diff: float
    p_value: float
    significant: bool


@dataclass
class EffectSize:
    group_a: str
    group_b: str
    cohens_d: float
    interpretation: str  # "small", "medium", "large"


@dataclass
class ParetoPoint:
    label: str
    accuracy: float
    normalized_cost: float
    is_pareto: bool = False


# ------------------------------------------------------------------
# ANOVA
# ------------------------------------------------------------------

def one_way_anova(*groups: Sequence[float]) -> ANOVAResult:
    """One-way ANOVA. Requires scipy."""
    from scipy import stats  # type: ignore
    f, p = stats.f_oneway(*groups)
    return ANOVAResult(f_statistic=float(f), p_value=float(p), significant=p < 0.05)


def kruskal_wallis(*groups: Sequence[float]) -> ANOVAResult:
    from scipy import stats  # type: ignore
    h, p = stats.kruskal(*groups)
    return ANOVAResult(f_statistic=float(h), p_value=float(p), significant=p < 0.05)


def shapiro_wilk(data: Sequence[float]) -> tuple[float, float]:
    from scipy import stats  # type: ignore
    stat, p = stats.shapiro(data)
    return float(stat), float(p)


# ------------------------------------------------------------------
# Tukey HSD
# ------------------------------------------------------------------

def tukey_hsd(groups: dict[str, Sequence[float]]) -> list[TukeyResult]:
    """Pairwise Tukey HSD. Returns all pairwise comparisons."""
    from itertools import combinations
    from scipy.stats import studentized_range  # type: ignore
    import numpy as np

    names = list(groups.keys())
    arrays = [np.array(groups[n]) for n in names]
    grand_mean = np.concatenate(arrays).mean()
    k = len(arrays)
    n_total = sum(len(a) for a in arrays)
    ms_within = sum(((a - a.mean()) ** 2).sum() for a in arrays) / (n_total - k)
    results: list[TukeyResult] = []

    for a_name, b_name in combinations(names, 2):
        a = np.array(groups[a_name])
        b = np.array(groups[b_name])
        mean_diff = float(a.mean() - b.mean())
        se = math.sqrt(ms_within * (1 / len(a) + 1 / len(b)) / 2)
        if se == 0:
            q = 0.0
        else:
            q = abs(mean_diff) / se
        # p-value via studentized range distribution
        p = float(1 - studentized_range.cdf(q, k, n_total - k))
        results.append(TukeyResult(
            group_a=a_name,
            group_b=b_name,
            mean_diff=mean_diff,
            p_value=p,
            significant=p < 0.05,
        ))

    return results


# ------------------------------------------------------------------
# Cohen's d
# ------------------------------------------------------------------

def cohens_d(a: Sequence[float], b: Sequence[float]) -> float:
    import numpy as np
    a_arr = np.array(a)
    b_arr = np.array(b)
    pooled_std = math.sqrt(
        ((len(a_arr) - 1) * a_arr.std(ddof=1) ** 2 + (len(b_arr) - 1) * b_arr.std(ddof=1) ** 2)
        / (len(a_arr) + len(b_arr) - 2)
    )
    if pooled_std == 0:
        return 0.0
    return float((a_arr.mean() - b_arr.mean()) / pooled_std)


def interpret_cohens_d(d: float) -> str:
    d = abs(d)
    if d < 0.2:
        return "negligible"
    if d < 0.5:
        return "small"
    if d < 0.8:
        return "medium"
    return "large"


def effect_sizes(groups: dict[str, Sequence[float]]) -> list[EffectSize]:
    from itertools import combinations
    results: list[EffectSize] = []
    for a_name, b_name in combinations(groups.keys(), 2):
        d = cohens_d(groups[a_name], groups[b_name])
        results.append(EffectSize(
            group_a=a_name,
            group_b=b_name,
            cohens_d=d,
            interpretation=interpret_cohens_d(d),
        ))
    return results


# ------------------------------------------------------------------
# Pareto Frontier
# ------------------------------------------------------------------

def pareto_frontier(points: list[ParetoPoint]) -> list[ParetoPoint]:
    """Mark Pareto-optimal points: maximize accuracy, minimize normalized cost."""
    sorted_pts = sorted(points, key=lambda p: (-p.accuracy, p.normalized_cost))
    pareto: list[ParetoPoint] = []
    min_cost = math.inf
    for pt in sorted_pts:
        if pt.normalized_cost <= min_cost:
            pt.is_pareto = True
            min_cost = pt.normalized_cost
            pareto.append(pt)
    return sorted_pts


# ------------------------------------------------------------------
# Cost-Effectiveness Ratio
# ------------------------------------------------------------------

def cost_effectiveness_ratio(accuracy: float, normalized_cost: float) -> float:
    """CER = accuracy / normalized_cost. Higher is better."""
    if normalized_cost <= 0:
        return float("inf")
    return accuracy / normalized_cost


# ------------------------------------------------------------------
# Full analysis pipeline
# ------------------------------------------------------------------

def run_analysis(
    group_accuracies: dict[str, list[float]],
    group_costs: dict[str, float],
) -> dict:
    """Run full statistical pipeline. Returns serialisable dict."""
    # Normality check
    normality: dict[str, bool] = {}
    for name, vals in group_accuracies.items():
        if len(vals) >= 3:
            _, p = shapiro_wilk(vals)
            normality[name] = p >= 0.05
        else:
            normality[name] = True

    all_normal = all(normality.values())

    # ANOVA or Kruskal-Wallis
    arrays = list(group_accuracies.values())
    if all_normal:
        anova = one_way_anova(*arrays)
        test_used = "one_way_anova"
    else:
        anova = kruskal_wallis(*arrays)
        test_used = "kruskal_wallis"

    # Post-hoc
    tukey = tukey_hsd(group_accuracies) if all_normal else []
    effects = effect_sizes(group_accuracies)

    # Pareto
    pareto_pts = [
        ParetoPoint(label=name, accuracy=sum(vals) / len(vals), normalized_cost=group_costs.get(name, 1.0))
        for name, vals in group_accuracies.items()
        if vals
    ]
    pareto_frontier(pareto_pts)

    return {
        "normality": normality,
        "test_used": test_used,
        "anova": {"f": anova.f_statistic, "p": anova.p_value, "significant": anova.significant},
        "tukey": [{"a": t.group_a, "b": t.group_b, "diff": t.mean_diff, "p": t.p_value, "sig": t.significant} for t in tukey],
        "effect_sizes": [{"a": e.group_a, "b": e.group_b, "d": e.cohens_d, "interp": e.interpretation} for e in effects],
        "pareto": [{"label": pt.label, "accuracy": pt.accuracy, "cost": pt.normalized_cost, "pareto": pt.is_pareto} for pt in pareto_pts],
    }
