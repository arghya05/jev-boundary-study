"""autotrust/JEV-9B served by vLLM on the RunPod pod.

System 1 (`jev9b-s1`): the community distillation of Jev 1.13 - one prefill pass
through the decision LoRA, choice probabilities from the verbalizer logprobs plus
the published head bias, divided by the per-kind temperature (model card recipe).

System 2 (`jev9b-s2`): the same weights' base model (Qwen3.5-9B, unchanged) with
thinking enabled, given the identical canonical text. Supplementary arm that
separates one-pass decisions from reasoning at fixed scale.

Cost is GPU time: pod $/hr x wall-clock seconds, allocated per call.
"""
from __future__ import annotations

import json
import math
import re
import time

import requests

from ..canonical import Task, choice_lines, jev_state, render, task_hash
from .base import Adapter, Result

HF_REPO = "autotrust/JEV-9B"


class Jev9bS1Adapter(Adapter):
    def __init__(self, url: str, decision_head: dict, calibration: dict, gpu_usd_per_hr: float, revision: str):
        self.system = "jev9b-s1"
        self.url = url.rstrip("/")
        self.dh = decision_head
        self.temp = calibration["per_kind"]["choice"]
        self.gpu_rate = gpu_usd_per_hr
        self.config = {"model": HF_REPO, "revision": revision, "path": "System1 choice head via vLLM LoRA jev-decision",
                       "template": "bare-v1", "temperature_calibration": self.temp}

    def prompt(self, task: Task) -> str:
        return (f"[kind] choice\n[state] {jev_state(task)}\n[question] {task.question}\n[options]\n"
                + "\n".join(choice_lines(task)) + "\n[decision]:")

    def run(self, task: Task) -> Result:
        s = self.dh["slots"]["ranges"]["choice"][0]
        ids = self.dh["verbalizer_ids"][s: s + len(task.choices)]
        prompt = self.prompt(task)
        t0 = time.perf_counter()
        try:
            r = requests.post(f"{self.url}/v1/completions", timeout=300, json={
                "model": "jev-decision", "prompt": prompt, "max_tokens": 1, "temperature": 1.0,
                "logprobs": len(ids), "allowed_token_ids": ids, "add_special_tokens": False,
                "return_tokens_as_token_ids": True})
            r.raise_for_status()
            body = r.json()
        except Exception as e:
            return Result(self.system, task.task_id, task_hash(task), self.request_key(task), "error", None,
                          error=repr(e), mode="local")
        lat = time.perf_counter() - t0
        lp = {int(k.split(":")[1]): v for k, v in body["choices"][0]["logprobs"]["top_logprobs"][0].items()}
        z = [(lp.get(t, -1e9) + self.dh["bias"][s + i]) / self.temp for i, t in enumerate(ids)]
        m = max(z)
        e = [math.exp(x - m) for x in z]
        dist = {cid: v / sum(e) for cid, v in zip(task.choice_ids, e)}
        ans = max(dist, key=dist.get)
        n_in = (body.get("usage") or {}).get("prompt_tokens", 0)
        return Result(self.system, task.task_id, task_hash(task), self.request_key(task), "ok", ans,
                      distribution=dist, usage={"input_tokens": n_in, "output_tokens": 0},
                      cost_usd=lat * self.gpu_rate / 3600, latency_s=lat, resolved_model=f"{HF_REPO}@{self.config['revision']}",
                      mode="local")


ANSWER_RE = re.compile(r'"answer"\s*:\s*"([A-P])"|(?:final answer|answer)\s*(?:is)?\s*[:\-]?\s*\(?([A-P])\)?\b', re.I)


def parse_free_answer(text: str, valid: tuple[str, ...]) -> str | None:
    hits = [a or b for a, b in ANSWER_RE.findall(text)]
    hits = [h.upper() for h in hits if h and h.upper() in valid]
    if hits:
        return hits[-1]
    tail = text.strip().splitlines()[-1] if text.strip() else ""
    m = re.fullmatch(r"\W*([A-P])\W*", tail)
    return m[1] if m and m[1] in valid else None


class Jev9bS2Adapter(Adapter):
    def __init__(self, url: str, gpu_usd_per_hr: float, revision: str, max_tokens=16000):
        self.system = "jev9b-s2"
        self.url = url.rstrip("/")
        self.gpu_rate = gpu_usd_per_hr
        self.config = {"model": HF_REPO, "revision": revision, "path": "System2 base lm_head, enable_thinking=True",
                       "max_tokens": max_tokens, "suffix": 'Respond with JSON {"answer": "<choice identifier>"}.'}

    def run(self, task: Task) -> Result:
        text = render(task) + "\n" + self.config["suffix"]
        t0 = time.perf_counter()
        try:
            r = requests.post(f"{self.url}/v1/chat/completions", timeout=1800, json={
                "model": HF_REPO, "messages": [{"role": "user", "content": text}],
                "max_tokens": self.config["max_tokens"], "temperature": 0.6, "top_p": 0.95,
                "chat_template_kwargs": {"enable_thinking": True}, "seed": 0})
            r.raise_for_status()
            body = r.json()
        except Exception as e:
            return Result(self.system, task.task_id, task_hash(task), self.request_key(task), "error", None,
                          error=repr(e), mode="local")
        lat = time.perf_counter() - t0
        ch = body["choices"][0]
        content = ch["message"].get("content") or ""
        usage = {"input_tokens": body["usage"]["prompt_tokens"], "output_tokens": body["usage"]["completion_tokens"]}
        if ch.get("finish_reason") == "length":
            status, ans = "truncated", None
        else:
            ans = parse_free_answer(content, task.choice_ids)
            status = "ok" if ans else "invalid"
        return Result(self.system, task.task_id, task_hash(task), self.request_key(task), status, ans, usage=usage,
                      cost_usd=lat * self.gpu_rate / 3600, latency_s=lat, resolved_model=f"{HF_REPO}@{self.config['revision']}",
                      mode="local", raw={"finish_reason": ch.get("finish_reason"), "content_tail": content[-300:]})
