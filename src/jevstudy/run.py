"""Execution: spend ledger with reservations, exact response cache, interleaved sync runs, provider batches.

The runner is gold-blind: it reads only task files, never gold files.
"""
from __future__ import annotations

import json
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .adapters.base import Result
from .canonical import Task, read_jsonl, task_hash


class BudgetStop(RuntimeError):
    pass


class Ledger:
    """Append-only spend ledger. Every paid call reserves its configured maximum before dispatch."""

    def __init__(self, path: Path, stage_forecast_usd: float | None = None):
        self.path = Path(path)
        self.lock = threading.Lock()
        self.spent = 0.0
        self.committed = 0.0
        self.stage_forecast = stage_forecast_usd
        if self.path.exists():
            for ev in read_jsonl(self.path):
                if ev["event"] == "settle":
                    self.spent += ev["cost_usd"]

    def _log(self, ev: dict):
        with open(self.path, "a") as f:
            f.write(json.dumps({**ev, "t": time.time()}) + "\n")

    def reserve(self, key: str, system: str, max_usd: float):
        with self.lock:
            # A forecast is a review trigger, not a hard cap: exceeding it stops new calls until reviewed.
            if self.stage_forecast is not None and self.spent + self.committed + max_usd > self.stage_forecast:
                raise BudgetStop(f"stage forecast ${self.stage_forecast:.2f} would be exceeded "
                                 f"(spent {self.spent:.2f} + committed {self.committed:.2f} + {max_usd:.2f})")
            self.committed += max_usd
            self._log({"event": "reserve", "key": key, "system": system, "max_usd": max_usd})

    def settle(self, key: str, system: str, max_usd: float, cost: float, usage: dict):
        with self.lock:
            self.committed -= max_usd
            self.spent += cost
            self._log({"event": "settle", "key": key, "system": system, "cost_usd": cost, "usage": usage})

    def summary(self) -> dict:
        return {"spent_usd": round(self.spent, 4), "committed_usd": round(self.committed, 4)}


class Cache:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> dict | None:
        p = self.root / f"{key}.json"
        return json.loads(p.read_text()) if p.exists() else None

    def put(self, key: str, result: dict):
        if result["status"] == "error":
            return  # transport failures are not cached
        (self.root / f"{key}.json").write_text(json.dumps(result))


def load_tasks(path) -> list[Task]:
    return [Task.from_json(d) for d in read_jsonl(path)]


def run_sync(tasks: list[Task], adapters: list, out_path: Path, ledger: Ledger, cache: Cache,
             seed: int = 0, concurrency: int = 1, log=print, fresh: bool = False, mode_tag: str | None = None) -> list[dict]:
    """Each task is sent to every adapter in a seeded random provider order.

    concurrency=1 is the latency track (one request in flight overall).
    """
    out_path = Path(out_path)
    write_lock = threading.Lock()
    results = []

    def one(task: Task):
        order = list(adapters)
        random.Random(f"{seed}-{task.task_id}").shuffle(order)
        rows = []
        for ad in order:
            key = ad.request_key(task)
            hit = None if fresh else cache.get(key)
            if hit:
                hit = {**hit, "cache_hit": True}
                rows.append(hit)
                continue
            mx = ad.max_cost(task)
            ledger.reserve(key, ad.system, mx)
            res: Result = ad.run(task)
            ledger.settle(key, ad.system, mx, res.cost_usd, res.usage)
            d = {**res.to_json(), "cache_hit": False}
            if mode_tag:
                d["mode"] = mode_tag
            else:
                cache.put(key, d)
            rows.append(d)
            log(f"{task.task_id:<40} {ad.system:<12} {res.status:<9} ans={res.answer_id} "
                f"${res.cost_usd:.4f} {res.latency_s or 0:.1f}s  ledger={ledger.summary()}")
        with write_lock:
            with open(out_path, "a") as f:
                for r in rows:
                    f.write(json.dumps(r) + "\n")
        return rows

    if concurrency == 1:
        for t in tasks:
            results += one(t)
    else:
        with ThreadPoolExecutor(concurrency) as ex:
            for rows in ex.map(one, tasks):
                results += rows
    return results


def failure_rates(results: list[dict]) -> dict:
    by = {}
    for r in results:
        by.setdefault(r["system"], []).append(r["status"] != "ok")
    return {k: sum(v) / len(v) for k, v in by.items()}


# ---------------------------------------------------------------- provider batches (offline accuracy/cost track)
def submit_openai_batch(adapter, tasks: list[Task], workdir: Path, ledger: Ledger) -> str:
    workdir.mkdir(parents=True, exist_ok=True)
    src = workdir / "openai_batch_input.jsonl"
    with open(src, "w") as f:
        for t in tasks:
            f.write(json.dumps(adapter.batch_line(t)) + "\n")
    for t in tasks:
        ledger.reserve(adapter.request_key(t), adapter.system + "-batch", adapter.max_cost(t) * 0.5)
    up = adapter.client.files.create(file=open(src, "rb"), purpose="batch")
    b = adapter.client.batches.create(input_file_id=up.id, endpoint="/v1/responses", completion_window="24h")
    (workdir / "openai_batch_id.txt").write_text(b.id)
    return b.id


def submit_anthropic_batch(adapter, tasks: list[Task], workdir: Path, ledger: Ledger) -> str:
    workdir.mkdir(parents=True, exist_ok=True)
    for t in tasks:
        ledger.reserve(adapter.request_key(t), adapter.system + "-batch", adapter.max_cost(t) * 0.5)
    b = adapter.client.messages.batches.create(requests=[adapter.batch_request(t) for t in tasks])
    (workdir / "anthropic_batch_id.txt").write_text(b.id)
    return b.id


def collect_openai_batch(adapter, batch_id: str, tasks: dict, out_path: Path, ledger: Ledger, cache: Cache) -> str:
    b = adapter.client.batches.retrieve(batch_id)
    if b.status != "completed":
        return b.status
    lines = adapter.client.files.content(b.output_file_id).text.splitlines()
    seen = set()
    with open(out_path, "a") as f:
        for line in lines:
            d = json.loads(line)
            t = tasks[d["custom_id"]]
            seen.add(t.task_id)
            body = (d.get("response") or {}).get("body") or {}
            if d.get("error") or not body:
                status, ans, usage = "error", None, {"input_tokens": 0, "output_tokens": 0}
            else:
                status, ans, usage = adapter.parse(body)
                if ans is not None and ans not in t.choice_ids:
                    status, ans = "invalid", None
            cost = adapter.cost(usage, batch=True) if status != "error" else 0.0
            key = adapter.request_key(t)
            ledger.settle(key, adapter.system + "-batch", adapter.max_cost(t) * 0.5, cost, usage)
            r = Result(adapter.system, t.task_id, task_hash(t), key, status, ans, usage=usage, cost_usd=cost,
                       resolved_model=body.get("model"), mode="batch", error=json.dumps(d.get("error")) if d.get("error") else None)
            row = {**r.to_json(), "cache_hit": False}
            cache.put(key, row)
            f.write(json.dumps(row) + "\n")
    _missing(tasks, seen, adapter, out_path, ledger)
    return "collected"


def collect_anthropic_batch(adapter, batch_id: str, tasks: dict, out_path: Path, ledger: Ledger, cache: Cache) -> str:
    b = adapter.client.messages.batches.retrieve(batch_id)
    if b.processing_status != "ended":
        return b.processing_status
    seen = set()
    with open(out_path, "a") as f:
        for item in adapter.client.messages.batches.results(batch_id):
            t = tasks[item.custom_id]
            seen.add(t.task_id)
            if item.result.type == "succeeded":
                msg = item.result.message.model_dump()
                status, ans, usage = adapter.parse(msg)
                if ans is not None and ans not in t.choice_ids:
                    status, ans = "invalid", None
                model = msg.get("model")
            else:
                status, ans, usage, model = "error", None, {"input_tokens": 0, "output_tokens": 0}, None
            cost = adapter.cost(usage, batch=True) if status != "error" else 0.0
            key = adapter.request_key(t)
            ledger.settle(key, adapter.system + "-batch", adapter.max_cost(t) * 0.5, cost, usage)
            row = {**Result(adapter.system, t.task_id, task_hash(t), key, status, ans, usage=usage, cost_usd=cost,
                            resolved_model=model, mode="batch",
                            error=None if status != "error" else item.result.type).to_json(), "cache_hit": False}
            cache.put(key, row)
            f.write(json.dumps(row) + "\n")
    _missing(tasks, seen, adapter, out_path, ledger)
    return "collected"


def _missing(tasks: dict, seen: set, adapter, out_path: Path, ledger: Ledger):
    """Rows absent from a batch result remain failures in the denominator."""
    with open(out_path, "a") as f:
        for tid, t in tasks.items():
            if tid not in seen:
                key = adapter.request_key(t)
                ledger.settle(key, adapter.system + "-batch", adapter.max_cost(t) * 0.5, 0.0, {})
                f.write(json.dumps({**Result(adapter.system, tid, task_hash(t), key, "error", None, mode="batch",
                                             error="missing from batch output").to_json(), "cache_hit": False}) + "\n")
