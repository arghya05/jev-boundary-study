"""Scoring (gold joined only here) and analysis outputs."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from . import router, stats
from .canonical import Task, read_jsonl

FRONTIERS = ("astra-high", "fable-high")
JEV = "jev9b-s1"


def load_frame(task_files, gold_files, result_files, include_latency: bool = False) -> pd.DataFrame:
    tasks = {d["task_id"]: Task.from_json(d) for f in task_files for d in read_jsonl(f)}
    gold = {d["task_id"]: d for f in gold_files for d in read_jsonl(f)}
    latest = {}
    for f in result_files:
        for r in read_jsonl(f):
            if r.get("mode") == "sync-latency" and not include_latency:
                continue
            latest[(r["system"], r["task_id"], r.get("mode", "sync"))] = r  # last write wins (re-collection)
    rows = []
    for (system, tid, mode), r in latest.items():
        if tid not in tasks:
            continue
        t, g = tasks[tid], gold[tid]
        rows.append({
            "system": system, "mode": mode, "task_id": tid, "family": t.family, "split": t.split,
            "cluster": t.cluster_id, "status": r["status"], "answer": r["answer_id"], "gold": g["answer_id"],
            "gold_label": g["answer_label"],
            "correct": int(r["status"] == "ok" and r["answer_id"] == g["answer_id"]),  # failures stay in denominator
            "cost_usd": r.get("cost_usd", 0.0), "latency_s": r.get("latency_s"), "cache_hit": r.get("cache_hit", False),
            "input_tokens": (r.get("usage") or {}).get("input_tokens", 0),
            "output_tokens": (r.get("usage") or {}).get("output_tokens", 0),
            "reasoning_tokens": (r.get("usage") or {}).get("reasoning_tokens"),
            "conf": max(r["distribution"].values()) if r.get("distribution") else None,
            "resolved_model": r.get("resolved_model"),
            **{f"m_{k}": v for k, v in t.meta.items()},
        })
    return pd.DataFrame(rows)


def accuracy_table(df: pd.DataFrame, by=("split", "family", "system")) -> pd.DataFrame:
    out = []
    for key, g in df.groupby(list(by)):
        k, n = int(g.correct.sum()), len(g)
        lo, hi = stats.wilson(k, n)
        out.append({**dict(zip(by, key)), "n": n, "accuracy": k / n, "ci_lo": lo, "ci_hi": hi,
                    "failures": int((g.status != "ok").sum()),
                    "usd_per_1k": 1000 * g.cost_usd.mean(),
                    "mean_out_tokens": g.output_tokens.mean(),
                    "p50_latency_s": g.latency_s.median(), "p95_latency_s": g.latency_s.quantile(0.95)})
    return pd.DataFrame(out)


def paired_comparisons(df: pd.DataFrame, panels: list[tuple[str, str]], alpha=0.05, mode_jev="local") -> list[dict]:
    """Primary comparisons: JEV-9B vs each frontier on each (split, family) panel, Bonferroni-adjusted."""
    m = len(panels) * len(FRONTIERS)
    a = stats.bonferroni_alpha(alpha, m)
    out = []
    for split, fam in panels:
        sub = df[(df.split == split) & (df.family == fam)]
        j = sub[sub.system == JEV].set_index("task_id")
        for fr in FRONTIERS:
            f = sub[sub.system == fr].set_index("task_id")
            ids = sorted(set(j.index) | set(f.index))
            rows = [{"cluster": (j.cluster.get(i) if i in j.index else f.cluster.get(i)),
                     "x": int(j.correct.get(i, 0)), "y": int(f.correct.get(i, 0))} for i in ids]
            if not rows:
                continue
            res = stats.paired_delta(rows, alpha=a)
            cj, cf = j.cost_usd.sum(), f.cost_usd.sum()
            res.update({"split": split, "family": fam, "frontier": fr, "adjusted_alpha": a, "m": m,
                        "jev_cost_usd": cj, "frontier_cost_usd": cf,
                        "conclusion": stats.classify(res, jev_cheaper=cj < cf)})
            out.append(res)
    return out


def controlled_effects(df: pd.DataFrame, split="controlled_final", alpha=0.05) -> dict:
    base = df[(df.split == split) & (df.get("m_condition") == "base")]
    out = {}
    systems = sorted(base.system.unique())
    for fr in [s for s in systems if s != JEV]:
        x = base[base.system == JEV].set_index("task_id")
        y = base[base.system == fr].set_index("task_id")
        ids = sorted(set(x.index) & set(y.index))
        rows = [{"cluster": x.cluster[i], "depth": x.m_depth[i], "irrelevant": x.m_irrelevant[i],
                 "x": int(x.correct[i]), "y": int(y.correct[i])} for i in ids]
        if not rows:
            continue
        out[fr] = {
            "depth5_vs_1": stats.interaction(rows, "depth", 5, 1, alpha),
            "depth3_vs_1": stats.interaction(rows, "depth", 3, 1, alpha),
            "irrelevant8_vs_0": stats.interaction(rows, "irrelevant", 8, 0, alpha),
        }
    # cell accuracies per system
    cells = base.groupby(["system", "m_depth", "m_irrelevant"]).correct.agg(["mean", "count"]).reset_index()
    out["cells"] = cells.to_dict("records")
    # by gold label (Unknown items test absence of a derivation)
    out["by_label"] = base.groupby(["system", "m_depth", "gold_label"]).correct.mean().reset_index().to_dict("records")
    # paired controls
    ctl = df[(df.split == split) & (df.get("m_condition").isin(["decision_changing", "decision_preserving"]))]
    ref = df[(df.split == split) & (df.get("m_condition") == "base") & (df.m_depth == 3) & (df.m_irrelevant == 8)]
    ctrl = {}
    for s in sorted(ctl.system.unique()):
        r0 = ref[ref.system == s].set_index("cluster")
        c = ctl[ctl.system == s]
        ch = c[c.m_condition == "decision_changing"].set_index("cluster")
        pr = c[c.m_condition == "decision_preserving"].set_index("cluster")
        ks = sorted(set(r0.index) & set(ch.index) & set(pr.index))
        ctrl[s] = {
            "changing_accuracy": float(np.mean([ch.correct[k] for k in ks])) if ks else None,
            "changing_follows_change": float(np.mean([ch.answer[k] != r0.answer[k] for k in ks])) if ks else None,
            "both_correct_change": float(np.mean([ch.correct[k] and r0.correct[k] for k in ks])) if ks else None,
            "preserving_accuracy": float(np.mean([pr.correct[k] for k in ks])) if ks else None,
            "preserving_invariant": float(np.mean([pr.answer[k] == r0.answer[k] for k in ks])) if ks else None,
            "n": len(ks)}
    out["controls"] = ctrl
    return out


def router_evaluation(df: pd.DataFrame, tasks: dict, splits: list[str]) -> dict:
    """Leave-one-family-out (public panels + controlled) and unseen-template evaluation."""
    out = {}
    for fr in FRONTIERS:
        rows = []
        sub = df[df.split.isin(splits)]
        j = sub[sub.system == JEV].set_index("task_id")
        f = sub[sub.system == fr].set_index("task_id")
        for tid in sorted(set(j.index) & set(f.index)):
            t = tasks[tid]
            rows.append({"task_id": tid, "f": router.features(t), "family": t.family,
                         "template": t.meta.get("template"), "conf": float(j.conf[tid] or 0.0),
                         "jev": int(j.correct[tid]), "front": int(f.correct[tid]),
                         "cost_jev": float(j.cost_usd[tid]), "cost_front": float(f.cost_usd[tid])})
        if not rows:
            continue
        fams = sorted({r["family"] for r in rows})
        lofo = {}
        for fam in fams:
            tr = [r for r in rows if r["family"] != fam]
            te = [r for r in rows if r["family"] == fam]
            if tr and te:
                lofo[fam] = router.evaluate_policies(tr, te)
        tpl = None
        tr = [r for r in rows if r["template"] != "T2"]
        te = [r for r in rows if r["template"] == "T2"]
        if tr and te:
            tpl = router.evaluate_policies(tr, te)
        out[fr] = {"leave_one_family_out": lofo, "unseen_template_T2": tpl, "n": len(rows)}
    return out


def write_json(obj, path):
    Path(path).write_text(json.dumps(obj, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
