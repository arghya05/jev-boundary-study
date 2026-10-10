"""OpenAI gpt-6-astra via the Responses API, native reasoning, structured final label."""
from __future__ import annotations

import json
import time

import openai

from ..canonical import Task, render, task_hash
from .base import ANSWER_SCHEMA_NAME, TRANSIENT_HTTP, Adapter, Result, answer_schema, est_tokens


class AstraAdapter(Adapter):
    def __init__(self, rates: dict, model="gpt-6-astra", effort="high", max_output_tokens=32000, timeout=1800):
        self.system = f"astra-{effort}"
        self.rates = rates
        self.config = {"provider": "openai", "model": model, "effort": effort, "max_output_tokens": max_output_tokens,
                       "api": "responses", "format": "json_schema_strict", "tools": "none", "store": False}
        self.client = openai.OpenAI(max_retries=0, timeout=timeout)  # SDK retries disabled; we retry once ourselves

    def params(self, task: Task) -> dict:
        c = self.config
        return {
            "model": c["model"],
            "input": render(task),
            "reasoning": {"effort": c["effort"]},
            "max_output_tokens": c["max_output_tokens"],
            "text": {"format": {"type": "json_schema", "name": ANSWER_SCHEMA_NAME, "schema": answer_schema(task), "strict": True}},
            "store": False,
        }

    def max_cost(self, task: Task) -> float:
        r = self.rates
        return (est_tokens(render(task)) * r["input"] + self.config["max_output_tokens"] * r["output"]) / 1e6

    def cost(self, usage: dict, batch=False) -> float:
        r = self.rates
        k = r.get("batch_multiplier", 0.5) if batch else 1.0
        cached = usage.get("cached_input_tokens", 0)
        # output_tokens already include reasoning tokens; do not add them again
        return k * ((usage["input_tokens"] - cached) * r["input"] + cached * r["cached_input"]
                    + usage["output_tokens"] * r["output"]) / 1e6

    @staticmethod
    def parse(resp: dict) -> tuple[str, str | None, dict]:
        u = resp.get("usage") or {}
        usage = {
            "input_tokens": u.get("input_tokens", 0),
            "cached_input_tokens": (u.get("input_tokens_details") or {}).get("cached_tokens", 0),
            "output_tokens": u.get("output_tokens", 0),
            "reasoning_tokens": (u.get("output_tokens_details") or {}).get("reasoning_tokens", 0),
        }
        status = resp.get("status")
        if status == "incomplete":
            return "truncated", None, usage
        text = ""
        for item in resp.get("output", []):
            if item.get("type") == "message":
                for part in item.get("content", []):
                    if part.get("type") == "refusal":
                        return "refusal", None, usage
                    if part.get("type") == "output_text":
                        text += part.get("text", "")
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
                resp = self.client.responses.create(**self.params(task)).model_dump()
                lat = time.perf_counter() - t0
                status, ans, usage = self.parse(resp)
                if ans is not None and ans not in task.choice_ids:
                    status, ans = "invalid", None
                return Result(self.system, task.task_id, task_hash(task), self.request_key(task), status, ans,
                              usage=usage, cost_usd=self.cost(usage), latency_s=lat, resolved_model=resp.get("model"),
                              attempts=attempts, raw={"id": resp.get("id"), "status": resp.get("status"),
                                                      "incomplete_details": resp.get("incomplete_details")})
            except (openai.APIConnectionError, openai.APITimeoutError) as e:
                err = repr(e)
            except openai.APIStatusError as e:
                err = f"{e.status_code}: {e.message}"
                if e.status_code not in TRANSIENT_HTTP:
                    break
                time.sleep(float(e.response.headers.get("retry-after", 20)))
        return Result(self.system, task.task_id, task_hash(task), self.request_key(task), "error", None,
                      attempts=attempts, error=err)

    # ------------------------------------------------------------ batch
    def batch_line(self, task: Task) -> dict:
        return {"custom_id": task.task_id, "method": "POST", "url": "/v1/responses", "body": self.params(task)}
