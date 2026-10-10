"""JEV-H: permutation-debiased, calibrated self-escalation harness around JEV-9B (preregistration A4).

For each item:
  1. JEV-9B System 1 on the canonical option order and on the reversed order; map the reversed
     distribution back to canonical letters and average the two.
  2. If the averaged top probability >= THRESHOLD (0.90, fixed a priori), answer its argmax.
  3. Otherwise answer with JEV-9B System 2 (same weights, thinking); if System 2 failed, keep step 2's argmax.

Cost = both System-1 calls + System 2's per-item share of GPU time on escalated items.
No parameter is fitted. The harness reads only model outputs, never gold.

    python -m jevstudy.harness --root .      # writes results/raw/harness_jevh.jsonl (system "jev9b-h")
"""
from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path

from .canonical import LETTERS, read_jsonl

THRESHOLD = 0.90
SYSTEM = "jev9b-h"


def unreverse(dist: dict, n: int) -> dict:
    return {LETTERS[n - 1 - LETTERS.index(k)]: v for k, v in dist.items()}


def combine(s1: dict | None, s1_rev: dict | None, s2: dict | None, n_choices: int, s2_cost_per_item: float,
            threshold: float = THRESHOLD) -> dict:
    """Return a result row (answer, status, cost, provenance) for one item."""
    dists = []
    if s1 and s1.get("distribution"):
        dists.append(s1["distribution"])
    if s1_rev and s1_rev.get("distribution"):
        dists.append(unreverse(s1_rev["distribution"], n_choices))
    cost = sum(r.get("cost_usd", 0.0) for r in (s1, s1_rev) if r)
    if not dists:
        return {"status": "error", "answer_id": None, "cost_usd": cost, "route": "none", "confidence": None}
    avg = {k: sum(d.get(k, 0.0) for d in dists) / len(dists) for k in LETTERS[:n_choices]}
    best = max(avg, key=avg.get)
    conf = avg[best]
    if conf >= threshold:
        return {"status": "ok", "answer_id": best, "cost_usd": cost, "route": "s1", "confidence": conf,
                "distribution": avg, "n_orders": len(dists)}
    if s2 and s2.get("status") == "ok" and s2.get("answer_id"):
        return {"status": "ok", "answer_id": s2["answer_id"], "cost_usd": cost + s2_cost_per_item, "route": "s2",
                "confidence": conf, "distribution": avg, "n_orders": len(dists)}
    return {"status": "ok", "answer_id": best, "cost_usd": cost + (s2_cost_per_item if s2 else 0.0), "route": "s1-fallback",
            "confidence": conf, "distribution": avg, "n_orders": len(dists)}


def s2_rate_per_item(root: Path) -> dict:
    """USD per System-2 item for each panel: logged pod-hours over the panel's run window x $/h / items run."""
    rate = json.load(open(root / "manifests" / "rate_card.json")).get("jev9b", {}).get("usd_per_hr", 0.59)
    hours, starts = defaultdict(float), {}
    wf = root / "results" / "gpu_windows.jsonl"
    for e in (read_jsonl(wf) if wf.exists() else []):
        if e["track"] != "B":
            continue
        if e["event"] == "start":
            starts[e["panel"]] = e["t"]
        elif e["panel"] in starts:
            hours[e["panel"]] += (e["t"] - starts.pop(e["panel"])) / 3600
    out = {}
    for panel, h in hours.items():
        p = root / "data" / "panels" / f"{panel}.tasks.jsonl"
        n = sum(1 for _ in open(p)) if p.exists() else 0
        out[panel] = h * rate / n if n else 0.0
    return out


def build(root: Path, panels: list[str], threshold: float = THRESHOLD) -> Path:
    latest = {}
    for f in sorted((root / "results" / "raw").glob("*.jsonl")):
        if f.name.startswith("harness"):
            continue
        for r in read_jsonl(f):
            if r.get("mode") == "sync-latency":
                continue
            if r["system"] in ("jev9b-s1", "jev9b-s2"):
                latest[(r["system"], r["task_id"])] = r
    per_item = s2_rate_per_item(root)
    out_rows = []
    for panel in panels:
        tasks = read_jsonl(root / "data" / "panels" / f"{panel}.tasks.jsonl")
        c = per_item.get(panel, 0.0)
        for t in tasks:
            tid = t["task_id"]
            res = combine(latest.get(("jev9b-s1", tid)), latest.get(("jev9b-s1", tid + "-rev")),
                          latest.get(("jev9b-s2", tid)), len(t["choices"]), c, threshold)
            out_rows.append({"system": SYSTEM, "task_id": tid, "task_hash": "", "request_key": f"harness-{tid}",
                             "status": res["status"], "answer_id": res["answer_id"], "distribution": res.get("distribution"),
                             "usage": {"input_tokens": 0, "output_tokens": 0}, "cost_usd": res["cost_usd"],
                             "latency_s": None, "resolved_model": "JEV-H(threshold=%.2f)" % threshold, "attempts": 1,
                             "mode": "derived", "error": None, "raw": {"route": res["route"], "confidence": res["confidence"],
                                                                         "n_orders": res.get("n_orders")},
                             "created_at": time.time(), "cache_hit": False})
    path = root / "results" / "raw" / "harness_jevh.jsonl"
    with open(path, "w") as f:
        for r in out_rows:
            f.write(json.dumps(r) + "\n")
    return path


PANELS = ["folio_final", "anli_final", "controlled_final", "judgebench_final", "banking_final",
          "controlled_deep", "rewardbench", "halueval"]


def escalation_ids(root: Path, panel: str, ids_file: str | None = None, threshold: float = THRESHOLD) -> list[str]:
    """Items whose two-order System-1 confidence is below the threshold (model outputs only, never gold)."""
    latest = {}
    for f in sorted((root / "results" / "raw").glob("*.jsonl")):
        for r in read_jsonl(f):
            if r["system"] == "jev9b-s1" and r.get("mode") != "sync-latency":
                latest[r["task_id"]] = r
    keep = set(json.load(open(ids_file))["ids"]) if ids_file else None
    out = []
    for t in read_jsonl(root / "data" / "panels" / f"{panel}.tasks.jsonl"):
        if keep is not None and t["task_id"] not in keep:
            continue
        res = combine(latest.get(t["task_id"]), latest.get(t["task_id"] + "-rev"), None, len(t["choices"]), 0.0, threshold)
        if res["route"] != "s1":
            out.append(t["task_id"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--escalated", help="panel name: write manifests/escalated_<panel>.json instead of building")
    ap.add_argument("--ids", help="restrict --escalated to an ids manifest")
    a = ap.parse_args()
    if a.escalated:
        ids = escalation_ids(Path(a.root), a.escalated, a.ids)
        json.dump({"ids": ids, "rule": f"two-order S1 confidence < {THRESHOLD}"},
                  open(Path(a.root) / "manifests" / f"escalated_{a.escalated}.json", "w"))
        print(a.escalated, "escalated", len(ids))
        return
    p = build(Path(a.root), PANELS)
    rows = read_jsonl(p)
    routes = defaultdict(int)
    for r in rows:
        routes[r["raw"]["route"]] += 1
    print(p, len(rows), dict(routes))


if __name__ == "__main__":
    main()
