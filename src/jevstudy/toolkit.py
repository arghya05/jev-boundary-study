"""Practical toolkit: use JEV-9B for typed decisions and evaluations, and escalate to a frontier model when needed.

    from jevstudy.toolkit import JevClient, Router

    jev = JevClient("http://localhost:8000")                 # vLLM serving autotrust/JEV-9B (see docs/STARTUP_GUIDE.md)
    p = jev.decide("Is the answer correct?", state="Q: 17*3?  A: 51", options=["yes", "no"])
    # -> {"yes": 0.97, "no": 0.03}

    router = Router(jev, frontier="astra", threshold=0.85)   # pick the threshold with `jevstudy custom` on YOUR data
    out = router.decide(question, state, options)            # JEV-9B when confident, frontier otherwise

The router's default threshold is a placeholder: the paper shows that whether JEV-9B is
good enough is task-dependent, so calibrate on a labelled sample of your own task first.
"""
from __future__ import annotations

import json
import math

import requests

from .adapters.jev9b import HF_REPO
from .canonical import LETTERS, Task

JEV_REVISION = "b63f651ce8ed64481d3f5e73ecdb05f740042f01"


def _download(name: str) -> dict:
    from huggingface_hub import hf_hub_download
    return json.load(open(hf_hub_download(HF_REPO, name, revision=JEV_REVISION)))


class JevClient:
    """Typed decisions from JEV-9B System 1 (one forward pass, calibrated probabilities)."""

    def __init__(self, url: str = "http://localhost:8000", decision_head: dict | None = None, calibration: dict | None = None):
        self.url = url.rstrip("/")
        self.dh = decision_head or _download("adapter_vllm/decision_head.json")
        self.temp = (calibration or _download("calibration.json"))["per_kind"]

    def decide(self, question: str, state: str = "", options: list[str] | None = None, kind: str = "choice") -> dict:
        """kind: 'choice' (2-16 free-text options), 'noul' (yes/no -> {'false','true'}) or 'score' (0-5)."""
        if kind == "noul":
            options = ["false", "true"]
        elif kind == "score":
            options = [str(i) for i in range(6)]
        if not options or not 2 <= len(options) <= 16:
            raise ValueError("choice needs 2-16 options")
        lines = options if kind != "choice" else [f"{LETTERS[i]}) {o}" for i, o in enumerate(options)]
        prompt = f"[kind] {kind}\n[state] {state}\n[question] {question}\n[options]\n" + "\n".join(lines) + "\n[decision]:"
        s = self.dh["slots"]["ranges"][kind][0]
        ids = self.dh["verbalizer_ids"][s: s + len(options)]
        r = requests.post(f"{self.url}/v1/completions", timeout=120, json={
            "model": "jev-decision", "prompt": prompt, "max_tokens": 1, "temperature": 1.0, "logprobs": len(ids),
            "allowed_token_ids": ids, "add_special_tokens": False, "return_tokens_as_token_ids": True})
        r.raise_for_status()
        lp = {int(k.split(":")[1]): v for k, v in r.json()["choices"][0]["logprobs"]["top_logprobs"][0].items()}
        z = [(lp.get(t, -1e9) + self.dh["bias"][s + i]) / self.temp[kind] for i, t in enumerate(ids)]
        m = max(z)
        e = [math.exp(x - m) for x in z]
        return {o: v / sum(e) for o, v in zip(options, e)}

    def judge(self, question: str, response: str, criterion: str = "Is the response correct and complete?") -> float:
        """LLM-as-a-judge style pass/fail probability for one response (yes/no decision)."""
        return self.decide(criterion, state=f"Question:\n{question}\n\nResponse:\n{response}", kind="noul")["true"]

    def compare(self, question: str, response_a: str, response_b: str) -> dict:
        """Pairwise judging; returns P(A better), P(B better)."""
        p = self.decide("Which response is better? Correctness is the primary criterion.",
                        state=f"Question:\n{question}\n\nResponse A:\n{response_a}\n\nResponse B:\n{response_b}",
                        options=["Response A is better", "Response B is better"])
        return {"A": p["Response A is better"], "B": p["Response B is better"]}


class Router:
    """Confidence-gated escalation: JEV-9B answers when its top probability >= threshold, else a frontier model."""

    def __init__(self, jev: JevClient, frontier: str = "astra", threshold: float = 0.85, rates: dict | None = None):
        self.jev, self.threshold = jev, threshold
        rates = rates or {"input": 10.0, "cached_input": 1.0, "cache_write": 12.5, "cache_read": 0.25, "output": 50.0}
        if frontier == "astra":
            from .adapters.openai_astra import AstraAdapter
            self.frontier = AstraAdapter(rates)
        elif frontier == "fable":
            from .adapters.anthropic_fable import FableAdapter
            self.frontier = FableAdapter(rates)
        else:
            raise ValueError("frontier must be 'astra' or 'fable'")

    def decide(self, question: str, state: str, options: list[str], instructions: str = "Choose the correct option.") -> dict:
        p = self.jev.decide(question, state=state, options=options)
        best = max(p, key=p.get)
        if p[best] >= self.threshold:
            return {"answer": best, "system": "jev9b", "confidence": p[best], "distribution": p, "cost_usd": 0.0}
        t = Task("adhoc", "custom", "adhoc", "adhoc", instructions, state, question, tuple(options))
        r = self.frontier.run(t)
        ans = options[LETTERS.index(r.answer_id)] if r.answer_id else None
        return {"answer": ans, "system": self.frontier.system, "status": r.status, "jev_distribution": p, "cost_usd": r.cost_usd}
