"""Paired accuracy statistics, decision rules, and coverage simulation.

delta = accuracy(JEV-9B) - accuracy(frontier). Operational failures count as
incorrect. Uncertainty is computed over independent clusters.
"""
from __future__ import annotations

import math
from collections import defaultdict

import numpy as np
from scipy.stats import norm

MARGIN = 0.02  # frozen noninferiority margin (accuracy points)


def wilson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    z = norm.ppf(1 - alpha / 2)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def newcombe_paired(a: int, b: int, c: int, d: int, alpha: float = 0.05) -> tuple[float, float, float]:
    """Newcombe (1998) method 10 hybrid score interval for a paired difference p1 - p2.

    a: both correct, b: system1 only, c: system2 only, d: neither.
    """
    n = a + b + c + d
    p1, p2 = (a + b) / n, (a + c) / n
    l1, u1 = wilson(a + b, n, alpha)
    l2, u2 = wilson(a + c, n, alpha)
    den = math.sqrt((a + b) * (c + d) * (a + c) * (b + d))
    # Newcombe's continuity-corrected phi: shrink |ad - bc| by n/2 (floored at zero)
    num = a * d - b * c
    num = max(num - n / 2, 0.0) if num > 0 else min(num + n / 2, 0.0)
    phi = 0.0 if den == 0 else num / den
    delta = p1 - p2
    lo = delta - math.sqrt(max(0.0, (p1 - l1) ** 2 - 2 * phi * (p1 - l1) * (u2 - p2) + (u2 - p2) ** 2))
    hi = delta + math.sqrt(max(0.0, (u1 - p1) ** 2 - 2 * phi * (u1 - p1) * (p2 - l2) + (p2 - l2) ** 2))
    return delta, max(-1.0, lo), min(1.0, hi)


def cluster_bootstrap(diffs_by_cluster: dict, alpha: float = 0.05, B: int = 10000, seed: int = 0):
    """Percentile bootstrap over clusters for mean item-level difference.

    diffs_by_cluster: cluster -> list of per-item values (e.g. jev_correct - frontier_correct).
    """
    keys = sorted(diffs_by_cluster)
    sums = np.array([sum(diffs_by_cluster[k]) for k in keys], dtype=float)
    cnts = np.array([len(diffs_by_cluster[k]) for k in keys], dtype=float)
    est = sums.sum() / cnts.sum()
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(keys), size=(B, len(keys)))
    boots = sums[idx].sum(1) / cnts[idx].sum(1)
    lo, hi = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    return float(est), float(lo), float(hi)


def paired_delta(rows: list[dict], alpha: float = 0.05, B: int = 10000) -> dict:
    """rows: [{'cluster':..., 'x': 0/1 (JEV correct), 'y': 0/1 (frontier correct)}]."""
    n = len(rows)
    a = sum(r["x"] and r["y"] for r in rows)
    b = sum(r["x"] and not r["y"] for r in rows)
    c = sum((not r["x"]) and r["y"] for r in rows)
    d = n - a - b - c
    clusters = defaultdict(list)
    for r in rows:
        clusters[r["cluster"]].append(r["x"] - r["y"])
    if all(len(v) == 1 for v in clusters.values()):
        est, lo, hi = newcombe_paired(a, b, c, d, alpha)
        method = "newcombe-paired-score"
    else:
        est, lo, hi = cluster_bootstrap(clusters, alpha, B)
        method = f"cluster-bootstrap(B={B})"
    return {"n": n, "clusters": len(clusters), "both": a, "jev_only": b, "frontier_only": c, "neither": d,
            "acc_jev": (a + b) / n if n else None, "acc_frontier": (a + c) / n if n else None,
            "delta": est, "lo": lo, "hi": hi, "alpha": alpha, "method": method}


def classify(res: dict, jev_cheaper: bool, margin: float = MARGIN, min_clusters: int = 20) -> str:
    """Four-way conclusion from an adjusted interval (frozen rule)."""
    if res["clusters"] < min_clusters:
        return "inconclusive (too few independent clusters)"
    if res["lo"] > 0:
        return "JEV-9B more accurate"
    if res["hi"] < -margin:
        return "frontier materially more accurate"
    if res["lo"] > -margin:
        return "comparable (noninferior) and cheaper" if jev_cheaper else "comparable (noninferior), not cheaper"
    return "inconclusive"


def bonferroni_alpha(alpha: float, m: int) -> float:
    return alpha / max(1, m)


# ---------------------------------------------------------------- controlled panel contrasts
def interaction(rows: list[dict], factor: str, hi_level, lo_level, alpha: float = 0.05, B: int = 10000, seed: int = 0):
    """Difference-in-differences, clustered by graph seed.

    rows: [{'cluster', factor: level, 'x': jev correct, 'y': frontier correct}]
    Returns [(acc_x(hi)-acc_x(lo)) - (acc_y(hi)-acc_y(lo))] with a cluster bootstrap CI.
    Negative => JEV-9B loses more accuracy than the frontier when moving lo -> hi.
    """
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r[factor] in (hi_level, lo_level):
            by[r["cluster"]][r[factor]].append(r)
    keys = sorted(k for k, v in by.items() if hi_level in v and lo_level in v)

    def stat(ks):
        def acc(level, field):
            vals = [r[field] for k in ks for r in by[k][level]]
            return sum(vals) / len(vals)
        return (acc(hi_level, "x") - acc(lo_level, "x")) - (acc(hi_level, "y") - acc(lo_level, "y")), \
               acc(hi_level, "x") - acc(lo_level, "x"), acc(hi_level, "y") - acc(lo_level, "y")

    est, dx, dy = stat(keys)
    rng = np.random.default_rng(seed)
    boots = [stat([keys[i] for i in rng.integers(0, len(keys), len(keys))])[0] for _ in range(B)]
    lo, hi = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    return {"did": est, "lo": float(lo), "hi": float(hi), "jev_change": dx, "frontier_change": dy, "clusters": len(keys)}


# ---------------------------------------------------------------- simulation check of interval coverage
def simulate_coverage(p_x=0.8, p_y=0.85, rho=0.3, n_clusters=60, cluster_size=1, reps=500, alpha=0.05, seed=0, B=1000):
    """Coverage of the interval procedure used by paired_delta, under a latent-normal paired model."""
    rng = np.random.default_rng(seed)
    tx, ty = norm.ppf(p_x), norm.ppf(p_y)
    hits, widths = 0, []
    for _ in range(reps):
        rows = []
        for c in range(n_clusters):
            u = rng.normal(size=1) * math.sqrt(0.3)  # shared cluster effect
            for _ in range(cluster_size):
                z = rng.multivariate_normal([0, 0], [[1, rho], [rho, 1]])
                rows.append({"cluster": c, "x": int(z[0] + u[0] < tx), "y": int(z[1] + u[0] < ty)})
        r = paired_delta(rows, alpha, B)
        # true delta under the cluster mixture, by Monte Carlo
        hits += r["lo"] <= true_delta(p_x, p_y) <= r["hi"]
        widths.append(r["hi"] - r["lo"])
    return {"coverage": hits / reps, "mean_width": float(np.mean(widths)), "n_clusters": n_clusters,
            "cluster_size": cluster_size, "reps": reps, "nominal": 1 - alpha}


def true_delta(p_x, p_y, sd_u=math.sqrt(0.3)):
    tx, ty = norm.ppf(p_x), norm.ppf(p_y)
    s = math.sqrt(1 + sd_u ** 2)
    return norm.cdf(tx / s) - norm.cdf(ty / s)
