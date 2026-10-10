"""Anthropic claude-fable-5-1: adaptive thinking (always on), effort via output_config, structured final label.

No server-side refusal fallback is enabled: a fallback would silently answer with a
different model and contaminate the comparison. Refusals are recorded as failures.
"""
from __future__ import annotations

import json
import time

import anthropic

from ..canonical import Task, render, task_hash
from .base import TRANSIENT_HTTP, Adapter, Result, answer_schema, est_tokens


class FableAdapter(Adapter):
    def __init__(self, rates: dict, model="claude-fable-5-1", effort="high", max_tokens=32000, timeout=1800):
        self.system = f"fable-{effort}"
        self.rates = rates
        self.config = {"provider": "anthropic", "model": model, "effort": effort, "max_tokens": max_tokens,
                       "thinking": "adaptive(default, omitted display)", "format": "json_schema", "tools": "none"}
        self.client = anthropic.Anthropic(max_retries=0, timeout=timeout)

    def params(self, task: Task) -> dict:
        c = self.config
        return {
            "model": c["model"],
            "max_tokens": c["max_tokens"],
            "messages": [{"role": "user", "content": render(task)}],
            "output_config": {"effort": c["effort"], "format": {"type": "json_schema", "schema": answer_schema(task)}},
        }

    def max_cost(self, task: Task) -> float:
        r = self.rates
        return (est_tokens(render(task)) * r["input"] + self.config["max_tokens"] * r["output"]) / 1e6

    def cost(self, usage: dict, batch=False) -> float:
        r = self.rates
        k = r.get("batch_multiplier", 0.5) if batch else 1.0
        # output_tokens include thinking tokens
        return k * (usage["input_tokens"] * r["input"] + usage.get("cache_creation_input_tokens", 0) * r["cache_write"]
                    + usage.get("cache_read_input_tokens", 0) * r["cache_read"] + usage["output_tokens"] * r["output"]) / 1e6

    @staticmethod
    def parse(msg: dict) -> tuple[str, str | None, dict]:
        u = msg.get("usage") or {}
        usage = {k: u.get(k) or 0 for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")}
        stop = msg.get("stop_reason")
        if stop == "refusal":
            return "refusal", None, usage
        if stop == "max_tokens":
            return "truncated", None, usage
        text = "".join(b.get("text", "") for b in msg.get("content", []) if b.get("type") == "text")
        try:
            return "ok", json.loads(text)["answer"], usage
        except Exception:
            return "invalid", None, usage

    def run(self, task: Task) -> Result:
        attempts, err = 0, None
        while attempts < 2:
            attempts += 1
            t0 = time.perf_counter()
            try:
                msg = self.client.messages.create(**self.params(task)).model_dump()
                lat = time.perf_counter() - t0
                status, ans, usage = self.parse(msg)
                if ans is not None and ans not in task.choice_ids:
                    status, ans = "invalid", None
                return Result(self.system, task.task_id, task_hash(task), self.request_key(task), status, ans,
                              usage=usage, cost_usd=self.cost(usage), latency_s=lat, resolved_model=msg.get("model"),
                              attempts=attempts, raw={"id": msg.get("id"), "stop_reason": msg.get("stop_reason"),
                                                      "stop_details": msg.get("stop_details")})
            except (anthropic.APIConnectionError, anthropic.APITimeoutError) as e:
                err = repr(e)
            except anthropic.APIStatusError as e:
                err = f"{e.status_code}: {e.message}"
                if e.status_code not in TRANSIENT_HTTP:
                    break
                time.sleep(float(e.response.headers.get("retry-after", 20)))
        return Result(self.system, task.task_id, task_hash(task), self.request_key(task), "error", None,
                      attempts=attempts, error=err)

    # ------------------------------------------------------------ batch
    def batch_request(self, task: Task) -> dict:
        return {"custom_id": task.task_id, "params": self.params(task)}
