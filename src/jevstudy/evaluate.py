"""Reusable evaluation workflows built on the study's protocol.

`judge`  - use JEV-9B as an evaluator of model outputs (pass/fail, pairwise, 0-5 score), optionally
           escalating low-confidence items to a frontier model, and measuring agreement with human labels.
`custom` - run the fair-comparison protocol (JEV-9B vs frontier on identical tasks) on YOUR labelled
           tasks and get accuracy, cost, a replace/escalate verdict and a confidence-threshold table.

Input formats (JSON lines):

judge, pointwise:  {"id": "1", "question": "...", "response": "...", "label": true}            (label optional)
judge, pairwise:   {"id": "1", "question": "...", "response_a": "...", "response_b": "...", "label": "A"}
judge, score:      {"id": "1", "question": "...", "response": "...", "label": 4}                (0-5)
custom:            {"id": "1", "instructions": "...", "evidence": "...", "question": "...",
                    "choices": ["...", "..."], "answer": "<one of choices>", "cluster": "optional"}
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from . import stats
from .canonical import LETTERS, Gold, Task, read_jsonl, write_jsonl

POINTWISE_Q = "Is the response correct and complete for the question?"
PAIRWISE_Q = "Which response is better? Correctness is the primary criterion."
SCORE_Q = "Rate the response from 0 (useless or wrong) to 5 (fully correct and complete)."


def auroc(scores, labels) -> float | None:
    s, y = np.asarray(scores, float), np.asarray(labels, int)
    pos, neg = s[y == 1], s[y == 0]
    if not len(pos) or not len(neg):
        return None
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


def judge(rows: list[dict], mode: str, jev, escalate=None, threshold: float = 0.9, criterion: str | None = None) -> tuple[list, dict]:
    """Return per-row judgements and a summary. `escalate` is an optional frontier adapter."""
    out = []
    for r in rows:
        if mode == "pointwise":
            p = jev.decide(criterion or POINTWISE_Q, state=f"Question:\n{r['question']}\n\nResponse:\n{r['response']}", kind="noul")
            verdict, conf, prob = p["true"] >= 0.5, max(p.values()), p["true"]
            opts = ["correct", "not correct"]
        elif mode == "pairwise":
            p = jev.decide(criterion or PAIRWISE_Q, state=f"Question:\n{r['question']}\n\nResponse A:\n{r['response_a']}\n\nResponse B:\n{r['response_b']}",
                           options=["Response A is better", "Response B is better"])
            verdict = "A" if p["Response A is better"] >= 0.5 else "B"
            conf, prob = max(p.values()), p["Response A is better"]
            opts = ["Response A is better", "Response B is better"]
        elif mode == "score":
            p = jev.decide(criterion or SCORE_Q, state=f"Question:\n{r['question']}\n\nResponse:\n{r['response']}", kind="score")
            prob = sum(int(k) * v for k, v in p.items())   # expected score
            verdict, conf = int(round(prob)), max(p.values())
            opts = [str(i) for i in range(6)]
        else:
            raise ValueError("mode must be pointwise, pairwise or score")
        row = {"id": r.get("id"), "judge": "jev9b", "verdict": verdict, "confidence": conf, "prob": prob, "distribution": p, "cost_usd": 0.0}
        if escalate is not None and conf < threshold:
            evidence = row_state(r, mode)
            t = Task(f"judge-{r.get('id')}", "custom", "judge", str(r.get("id")), criterion or {"pointwise": POINTWISE_Q, "pairwise": PAIRWISE_Q, "score": SCORE_Q}[mode],
                     evidence, "Choose the option that applies.", tuple(opts))
            res = escalate.run(t)
            if res.answer_id:
                idx = LETTERS.index(res.answer_id)
                row.update({"judge": escalate.system, "cost_usd": res.cost_usd,
                            "verdict": (idx == 0) if mode == "pointwise" else ("A" if idx == 0 else "B") if mode == "pairwise" else idx})
            else:
                row.update({"escalation_status": res.status})
        if "label" in r:
            row["label"] = r["label"]
        out.append(row)
    return out, summarize_judgements(out, mode)


def row_state(r, mode):
    if mode == "pairwise":
        return f"Question:\n{r['question']}\n\nResponse A:\n{r['response_a']}\n\nResponse B:\n{r['response_b']}"
    return f"Question:\n{r['question']}\n\nResponse:\n{r['response']}"


def summarize_judgements(out: list, mode: str) -> dict:
    s = {"n": len(out), "escalated": sum(o["judge"] != "jev9b" for o in out), "cost_usd": sum(o["cost_usd"] for o in out)}
    lab = [o for o in out if "label" in o]
    if lab:
        if mode == "score":
            err = [abs(o["verdict"] - int(o["label"])) for o in lab]
            s.update({"labelled": len(lab), "mae": float(np.mean(err)), "exact": float(np.mean([e == 0 for e in err])),
                      "spearman": float(_spearman([o["prob"] for o in lab], [int(o["label"]) for o in lab]))})
        else:
            y = [bool(o["label"]) if mode == "pointwise" else str(o["label"]).upper() == "A" for o in lab]
            v = [bool(o["verdict"]) if mode == "pointwise" else o["verdict"] == "A" for o in lab]
            k = sum(a == b for a, b in zip(v, y))
            lo, hi = stats.wilson(k, len(lab))
            s.update({"labelled": len(lab), "agreement": k / len(lab), "ci95": [lo, hi],
                      "jev_auroc": auroc([o["prob"] for o in lab], y)})
            s["coverage_curve"] = coverage_curve([(o["confidence"], a == b) for o, a, b in zip(lab, v, y) if o["judge"] == "jev9b"])
    return s


def _spearman(a, b):
    from scipy.stats import spearmanr
    return spearmanr(a, b).correlation


def coverage_curve(conf_correct: list[tuple[float, bool]], thresholds=(0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 0.99)) -> list[dict]:
    """For each threshold: share of items JEV-9B keeps and its accuracy on them."""
    out = []
    for t in thresholds:
        kept = [c for p, c in conf_correct if p >= t]
        out.append({"threshold": t, "coverage": len(kept) / max(1, len(conf_correct)),
                    "accuracy_on_kept": (sum(kept) / len(kept)) if kept else None})
    return out


# ------------------------------------------------------------------ custom tasks through the study protocol
def custom_tasks(path: Path) -> list[tuple[Task, Gold | None]]:
    pairs = []
    for i, r in enumerate(read_jsonl(path)):
        choices = tuple(r["choices"])
        t = Task(str(r.get("id", i)), r.get("family", "custom"), "custom", str(r.get("cluster", r.get("id", i))),
                 r.get("instructions", "Choose the correct option."), r.get("evidence", ""), r["question"], choices,
                 {k: v for k, v in r.items() if k.startswith("meta_")})
        g = Gold(t.task_id, LETTERS[choices.index(r["answer"])], r["answer"]) if "answer" in r else None
        pairs.append((t, g))
    return pairs


def custom_report(pairs, results: list[dict], margin: float = stats.MARGIN) -> dict:
    gold = {t.task_id: g for t, g in pairs if g}
    by = {}
    for r in results:
        by.setdefault(r["system"], {})[r["task_id"]] = r
    rep = {"systems": {}}
    clusters = {t.task_id: t.cluster_id for t, _ in pairs}
    for s, rs in by.items():
        lab = [tid for tid in rs if tid in gold]
        corr = [int(rs[t]["status"] == "ok" and rs[t]["answer_id"] == gold[t].answer_id) for t in lab]
        cost = sum(rs[t]["cost_usd"] for t in rs)
        lo, hi = stats.wilson(sum(corr), len(corr)) if corr else (None, None)
        rep["systems"][s] = {"n": len(rs), "labelled": len(lab), "accuracy": float(np.mean(corr)) if corr else None,
                             "ci95": [lo, hi], "cost_usd": cost, "usd_per_1k": 1000 * cost / max(1, len(rs)),
                             "failures": sum(r["status"] != "ok" for r in rs.values())}
    jev = by.get("jev9b-s1", {})
    for fr in [s for s in by if s not in ("jev9b-s1", "jev9b-s2")]:
        ids = [t for t in jev if t in by[fr] and t in gold]
        if not ids:
            continue
        rows = [{"cluster": clusters[t], "x": int(jev[t]["status"] == "ok" and jev[t]["answer_id"] == gold[t].answer_id),
                 "y": int(by[fr][t]["status"] == "ok" and by[fr][t]["answer_id"] == gold[t].answer_id)} for t in ids]
        res = stats.paired_delta(rows)
        cheaper = rep["systems"]["jev9b-s1"]["usd_per_1k"] < rep["systems"][fr]["usd_per_1k"]
        res["conclusion"] = stats.classify(res, cheaper, margin=margin, min_clusters=20)
        res["confidence_gate"] = gate_table(jev, by[fr], gold, ids)
        rep[f"jev9b-s1_vs_{fr}"] = res
    return rep


def gate_table(jev: dict, fr: dict, gold: dict, ids: list) -> list[dict]:
    """Accuracy and frontier share if JEV-9B answers when its confidence >= t and the frontier answers otherwise."""
    out = []
    for t in (0.0, 0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 1.01):
        acc, esc, cost = [], 0, 0.0
        for i in ids:
            conf = max((jev[i].get("distribution") or {"x": 0}).values())
            use_jev = conf >= t
            r = jev[i] if use_jev else fr[i]
            esc += not use_jev
            cost += jev[i]["cost_usd"] + (0 if use_jev else fr[i]["cost_usd"])
            acc.append(int(r["status"] == "ok" and r["answer_id"] == gold[i].answer_id))
        out.append({"threshold": t, "accuracy": float(np.mean(acc)), "share_escalated": esc / len(ids), "cost_usd": cost})
    return out


def write_report(rep: dict, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(rep, indent=2, default=float))
    lines = ["# Custom evaluation report", "", "| System | n | Accuracy | 95% CI | Failures | USD / 1k |", "|---|---|---|---|---|---|"]
    for s, v in rep["systems"].items():
        ci = "" if v["ci95"][0] is None else f"{100 * v['ci95'][0]:.1f}–{100 * v['ci95'][1]:.1f}"
        acc = "" if v["accuracy"] is None else f"{100 * v['accuracy']:.1f}%"
        lines.append(f"| {s} | {v['n']} | {acc} | {ci} | {v['failures']} | {v['usd_per_1k']:.3f} |")
    for k, v in rep.items():
        if k.startswith("jev9b-s1_vs_"):
            lines += ["", f"## {k}", "", f"Δ accuracy (JEV-9B − frontier) = {100 * v['delta']:.1f} points, 95% CI "
                      f"[{100 * v['lo']:.1f}, {100 * v['hi']:.1f}], {v['clusters']} clusters ({v['method']}).",
                      f"**Verdict:** {v['conclusion']}", "", "Confidence gate (JEV-9B answers when confident, else the frontier):", "",
                      "| Threshold | Accuracy | Escalated | Cost USD |", "|---|---|---|---|"]
            lines += [f"| {g['threshold']:.2f} | {100 * g['accuracy']:.1f}% | {100 * g['share_escalated']:.0f}% | {g['cost_usd']:.3f} |"
                      for g in v["confidence_gate"]]
    (out_dir / "report.md").write_text("\n".join(lines) + "\n")
    return out_dir / "report.md"
