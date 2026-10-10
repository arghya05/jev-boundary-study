"""Command line entry point. All commands are meant to run on the RunPod pod."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path

from . import analysis, controlled
from . import datasets as ds
from .canonical import PROTOCOL_VERSION, Task, read_jsonl, render, task_hash, write_jsonl
from .run import (Cache, Ledger, collect_anthropic_batch, collect_openai_batch, load_tasks, run_sync,
                  submit_anthropic_batch, submit_openai_batch)

ROOT = Path(os.environ.get("JEVSTUDY_ROOT", Path.cwd()))
PANELS = ROOT / "data" / "panels"
RAW = ROOT / "data" / "raw"
MANI = ROOT / "manifests"
RES = ROOT / "results"
JEV_REVISION = "b63f651ce8ed64481d3f5e73ecdb05f740042f01"
HF_DATASET_REVISIONS = {"facebook/anli": "8e4813d81f46d313dac7892e1c28076917cfcdf9",
                        "ScalerLab/JudgeBench": "57dd5e0b9817d07f05ec8f45a91b2ce1e310e308"}


def _save_panel(name, pairs):
    PANELS.mkdir(parents=True, exist_ok=True)
    write_jsonl(PANELS / f"{name}.tasks.jsonl", [t.to_json() for t, _ in pairs])
    write_jsonl(PANELS / f"{name}.gold.jsonl", [g.__dict__ for _, g in pairs])  # read only by the scorer
    return {"panel": name, "n": len(pairs), "clusters": len({t.cluster_id for t, _ in pairs}),
            "task_hashes_sha256": hashlib.sha256("".join(sorted(task_hash(t) for t, _ in pairs)).encode()).hexdigest()}


def cmd_prepare(a):
    MANI.mkdir(exist_ok=True)
    srcs, panels = [], []
    pilot, s = ds.build_dev_pilot(RAW)
    srcs += s
    panels.append(_save_panel("dev_pilot", pilot))
    panels.append(_save_panel("controlled_dev", controlled.dev_panel()))
    for name, fn in (("folio_final", ds.load_folio_final), ("anli_final", ds.load_anli_final),
                     ("banking_final", ds.load_banking_final), ("judgebench_final", ds.load_judgebench_final)):
        pairs, s = fn(RAW)
        srcs += s
        panels.append(_save_panel(name, pairs))
    panels.append(_save_panel("controlled_final", controlled.final_panel(evidence_removal=True)))
    uniq = {x["name"]: x for x in srcs}
    json.dump({"protocol": PROTOCOL_VERSION, "sources": list(uniq.values()), "licenses": ds.LICENSES,
               "pinned_commits": {"Yale-LILY/FOLIO": ds.FOLIO_COMMIT, "PolyAI-LDN/task-specific-datasets": ds.BANKING_COMMIT},
               "hf_dataset_revisions": HF_DATASET_REVISIONS, "panels": panels,
               "notes": ["FOLIO v0.0 from the authors' GitHub; HF copy is gated. 'Uncertain'/'Unknown' -> Unknown.",
                         "Banking77 presented as 16 candidates (gold + 15 nearest train-centroid labels) because "
                         "JEV-9B's choice head supports at most 16 options; identical candidates for all systems.",
                         "Clusters: FOLIO premise set; ANLI premise; JudgeBench source+original_id; controlled graph seed."]},
              open(MANI / "datasets_manifest.json", "w"), indent=2)
    json.dump({"seed": ds.DEV_SEED, "sealed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "dev_pilot": [t.task_id for t, _ in pilot],
               "controlled_dev_seeds": controlled.DEV_SEEDS, "controlled_final_seeds": controlled.FINAL_SEEDS},
              open(MANI / "development_ids.json", "w"), indent=2)
    ex = pilot[0][0]
    json.dump({"protocol": PROTOCOL_VERSION, "example_task_id": ex.task_id, "example_task_hash": task_hash(ex),
               "canonical_text": render(ex)}, open(MANI / "prompt_manifest.json", "w"), indent=2)
    print(json.dumps(panels, indent=2))


def _adapters(names, gpu_rate):
    rc = json.load(open(MANI / "rate_card.json"))
    out = []
    for n in names:
        if n == "astra":
            from .adapters.openai_astra import AstraAdapter
            out.append(AstraAdapter(rc["gpt-6-astra"]))
        elif n == "fable":
            from .adapters.anthropic_fable import FableAdapter
            out.append(FableAdapter(rc["claude-fable-5-1"]))
        elif n in ("jev-s1", "jev-s2"):
            from huggingface_hub import hf_hub_download
            from .adapters.jev9b import Jev9bS1Adapter, Jev9bS2Adapter
            url = os.environ.get("VLLM_URL", "http://127.0.0.1:8000")
            if n == "jev-s1":
                dh = json.load(open(hf_hub_download("autotrust/JEV-9B", "adapter_vllm/decision_head.json", revision=JEV_REVISION)))
                cal = json.load(open(hf_hub_download("autotrust/JEV-9B", "calibration.json", revision=JEV_REVISION)))
                out.append(Jev9bS1Adapter(url, dh, cal, gpu_rate, JEV_REVISION))
            else:
                out.append(Jev9bS2Adapter(url, gpu_rate, JEV_REVISION))
        else:
            raise SystemExit(f"unknown system {n}")
    return out


def cmd_run(a):
    tasks = load_tasks(PANELS / f"{a.panel}.tasks.jsonl")
    if a.ids:
        keep = set(a.ids.split(","))
        tasks = [t for t in tasks if t.task_id in keep]
    if a.limit:
        tasks = tasks[: a.limit]
    RES.mkdir(exist_ok=True)
    (RES / "raw").mkdir(exist_ok=True)
    ledger = Ledger(RES / "budget_ledger.jsonl", a.stage_forecast)
    adapters = _adapters(a.systems.split(","), a.gpu_rate)
    out = RES / "raw" / f"{a.panel}.{a.run_name}.jsonl"
    print(f"running {len(tasks)} tasks x {[x.system for x in adapters]} -> {out}")
    run_sync(tasks, adapters, out, ledger, Cache(RES / "cache"), seed=a.seed, concurrency=a.concurrency)
    print("ledger", ledger.summary())


def cmd_batch_submit(a):
    tasks = load_tasks(PANELS / f"{a.panel}.tasks.jsonl")
    cache = Cache(RES / "cache")
    ledger = Ledger(RES / "budget_ledger.jsonl", a.stage_forecast)
    for ad in _adapters(a.systems.split(","), 0):
        todo = [t for t in tasks if not cache.get(ad.request_key(t))]
        wd = RES / "batches" / a.panel / ad.system
        if not todo:
            print(ad.system, "nothing to submit")
            continue
        bid = (submit_openai_batch if ad.system.startswith("astra") else submit_anthropic_batch)(ad, todo, wd, ledger)
        print(ad.system, "submitted", len(todo), bid)
    print("ledger", ledger.summary())


def cmd_batch_collect(a):
    tasks = {t.task_id: t for t in load_tasks(PANELS / f"{a.panel}.tasks.jsonl")}
    cache = Cache(RES / "cache")
    ledger = Ledger(RES / "budget_ledger.jsonl")
    for ad in _adapters(a.systems.split(","), 0):
        wd = RES / "batches" / a.panel / ad.system
        for fn, idf in ((collect_openai_batch, "openai_batch_id.txt"), (collect_anthropic_batch, "anthropic_batch_id.txt")):
            p = wd / idf
            if p.exists() and not (wd / "collected").exists():
                bid = p.read_text().strip()
                st = fn(ad, bid, tasks, RES / "raw" / f"{a.panel}.batch.jsonl", ledger, cache)
                print(ad.system, bid, st)
                if st == "collected":
                    (wd / "collected").write_text(time.ctime())
    print("ledger", ledger.summary())


def cmd_analyze(a):
    names = a.panels.split(",")
    tf = [PANELS / f"{n}.tasks.jsonl" for n in names]
    gf = [PANELS / f"{n}.gold.jsonl" for n in names]
    rf = sorted((RES / "raw").glob("*.jsonl"))
    df = analysis.load_frame(tf, gf, rf)
    out = RES / a.out
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "item_level.csv", index=False)
    acc = analysis.accuracy_table(df)
    acc.to_csv(out / "accuracy.csv", index=False)
    print(acc.to_string(index=False))
    panels = sorted({(r.split, r.family) for r in df.itertuples()})
    analysis.write_json(analysis.paired_comparisons(df, panels), out / "paired.json")
    if "controlled_final" in names or "controlled_dev" in names:
        split = "controlled_final" if "controlled_final" in names else "controlled_dev"
        analysis.write_json(analysis.controlled_effects(df, split), out / "controlled.json")
    tasks = {d["task_id"]: Task.from_json(d) for f in tf for d in read_jsonl(f)}
    analysis.write_json(analysis.router_evaluation(df, tasks, sorted(df.split.unique())), out / "router.json")
    print("wrote", out)


def cmd_env(a):
    import importlib.metadata as md
    lock = {"python": sys.version, "platform": platform.platform(),
            "packages": {p: md.version(p) for p in ("anthropic", "openai", "numpy", "pandas", "scipy", "requests", "huggingface_hub")}}
    try:
        lock["packages"]["vllm"] = md.version("vllm")
    except md.PackageNotFoundError:
        pass
    json.dump(lock, open(MANI / "environment_lock.json", "w"), indent=2)
    print(json.dumps(lock, indent=2))


def main(argv=None):
    p = argparse.ArgumentParser("jevstudy")
    sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("prepare").set_defaults(fn=cmd_prepare)
    sp.add_parser("env").set_defaults(fn=cmd_env)
    for name, fn in (("run", cmd_run), ("batch-submit", cmd_batch_submit), ("batch-collect", cmd_batch_collect)):
        r = sp.add_parser(name)
        r.add_argument("--panel", required=True)
        r.add_argument("--systems", default="jev-s1,astra,fable")
        r.add_argument("--run-name", default="main")
        r.add_argument("--ids")
        r.add_argument("--limit", type=int)
        r.add_argument("--seed", type=int, default=20261010)
        r.add_argument("--concurrency", type=int, default=1)
        r.add_argument("--gpu-rate", type=float, default=float(os.environ.get("GPU_USD_PER_HR", "0")))
        r.add_argument("--stage-forecast", type=float, default=None,
                       help="review trigger: stop new paid calls if spent+committed would exceed this")
        r.set_defaults(fn=fn)
    an = sp.add_parser("analyze")
    an.add_argument("--panels", required=True)
    an.add_argument("--out", default="analysis")
    an.set_defaults(fn=cmd_analyze)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
