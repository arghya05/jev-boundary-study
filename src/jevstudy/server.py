"""JEV-as-a-Judge: a self-hostable HTTP API for cheap, calibrated LLM evaluation.

    pip install -e '.[server]'
    VLLM_URL=http://127.0.0.1:8000 JUDGE_API_KEY=change-me uvicorn jevstudy.server:app --port 8080

Endpoints (JSON in, JSON out):
    POST /v1/judge     {question, response, criterion?}                  -> P(correct)
    POST /v1/compare   {question, response_a, response_b, criterion?}    -> P(A better), P(B better), position-debiased
    POST /v1/score     {question, response, criterion?}                  -> 0-5 distribution + expected score
    POST /v1/decide    {question, options[2..16], state?}                -> distribution over options
    POST /v1/batch     {mode, items:[...]}                               -> list of results
    GET  /v1/health

Every request may set `escalate`: {"to": "self" | "astra" | "fable", "threshold": 0.9, "api_key": "..."}.
Below the threshold the item is re-judged by JEV-9B's own reasoning mode ("self", same GPU, no API bill)
or by a frontier model with the caller's key. Responses report the deciding system, confidence,
latency and cost.
"""
from __future__ import annotations

import os
import time

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from .canonical import LETTERS, Task
from .toolkit import JevClient

GPU_USD_PER_HR = float(os.environ.get("GPU_USD_PER_HR", "0.59"))
PAIRWISE_Q = "Which response is better? Correctness is the primary criterion."
POINTWISE_Q = "Is the response correct and complete for the question?"
SCORE_Q = "Rate the response from 0 (useless or wrong) to 5 (fully correct and complete)."

app = FastAPI(title="JEV-as-a-Judge", version="0.1.0",
              description="Calibrated one-pass LLM evaluation with JEV-9B, with optional escalation.")
_jev: JevClient | None = None


def jev() -> JevClient:
    global _jev
    if _jev is None:
        _jev = JevClient(os.environ.get("VLLM_URL", "http://127.0.0.1:8000"))
    return _jev


def auth(authorization: str | None = Header(default=None)):
    key = os.environ.get("JUDGE_API_KEY")
    if key and authorization != f"Bearer {key}":
        raise HTTPException(status_code=401, detail="invalid or missing bearer token")


class Escalate(BaseModel):
    to: str = Field("self", pattern="^(self|astra|fable)$")
    threshold: float = Field(0.9, ge=0.0, le=1.0)
    api_key: str | None = None  # caller's provider key for astra/fable; never logged


class JudgeIn(BaseModel):
    question: str
    response: str
    criterion: str | None = None
    escalate: Escalate | None = None


class CompareIn(BaseModel):
    question: str
    response_a: str
    response_b: str
    criterion: str | None = None
    escalate: Escalate | None = None


class DecideIn(BaseModel):
    question: str
    options: list[str] = Field(min_length=2, max_length=16)
    state: str = ""
    escalate: Escalate | None = None


class BatchIn(BaseModel):
    mode: str = Field(pattern="^(judge|compare|score|decide)$")
    items: list[dict] = Field(max_length=1000)


def _gpu_cost(seconds: float) -> float:
    return seconds * GPU_USD_PER_HR / 3600


def _escalate(esc: Escalate, instructions: str, state: str, question: str, options: list[str]) -> dict:
    """Re-decide one item with JEV-9B System 2 or a frontier model; returns {choice, system, cost_usd}."""
    t = Task("api", "api", "api", "api", instructions, state, question, tuple(options))
    if esc.to == "self":
        from .adapters.jev9b import Jev9bS2Adapter
        ad = Jev9bS2Adapter(os.environ.get("VLLM_URL", "http://127.0.0.1:8000"), GPU_USD_PER_HR, "b63f651")
    else:
        if not esc.api_key:
            raise HTTPException(status_code=400, detail=f"escalate.to={esc.to} needs escalate.api_key")
        rates = {"input": 10.0, "cached_input": 1.0, "cache_write": 12.5, "cache_read": 0.25, "output": 50.0}
        if esc.to == "astra":
            import openai
            from .adapters.openai_astra import AstraAdapter
            ad = AstraAdapter(rates)
            ad.client = openai.OpenAI(api_key=esc.api_key, max_retries=0, timeout=600)
        else:
            import anthropic
            from .adapters.anthropic_fable import FableAdapter
            ad = FableAdapter(rates)
            ad.client = anthropic.Anthropic(api_key=esc.api_key, max_retries=0, timeout=600)
    r = ad.run(t)
    if not r.answer_id:
        return {"choice": None, "system": ad.system, "status": r.status, "cost_usd": r.cost_usd}
    return {"choice": options[LETTERS.index(r.answer_id)], "system": ad.system, "status": "ok", "cost_usd": r.cost_usd}


def judge_one(x: JudgeIn) -> dict:
    t0 = time.perf_counter()
    state = f"Question:\n{x.question}\n\nResponse:\n{x.response}"
    p = jev().decide(x.criterion or POINTWISE_Q, state=state, kind="noul")
    out = {"p_correct": p["true"], "verdict": p["true"] >= 0.5, "confidence": max(p.values()), "system": "jev9b"}
    if x.escalate and out["confidence"] < x.escalate.threshold:
        e = _escalate(x.escalate, x.criterion or POINTWISE_Q, state, "Is the response correct?", ["correct", "not correct"])
        if e["choice"]:
            out.update({"verdict": e["choice"] == "correct", "system": e["system"]})
        out["escalation_cost_usd"] = e["cost_usd"]
    out["latency_s"] = time.perf_counter() - t0
    out["cost_usd"] = _gpu_cost(out["latency_s"]) + out.get("escalation_cost_usd", 0.0)
    return out


def compare_one(x: CompareIn) -> dict:
    """Position-debiased pairwise judgement: ask in both orders and average (as in the JEV-H harness)."""
    t0 = time.perf_counter()
    q = x.criterion or PAIRWISE_Q
    opts = ["Response A is better", "Response B is better"]
    p1 = jev().decide(q, state=f"Question:\n{x.question}\n\nResponse A:\n{x.response_a}\n\nResponse B:\n{x.response_b}", options=opts)
    p2 = jev().decide(q, state=f"Question:\n{x.question}\n\nResponse A:\n{x.response_b}\n\nResponse B:\n{x.response_a}", options=opts)
    pa = (p1[opts[0]] + p2[opts[1]]) / 2
    out = {"p_a_better": pa, "p_b_better": 1 - pa, "winner": "A" if pa >= 0.5 else "B", "confidence": max(pa, 1 - pa),
           "position_consistent": (p1[opts[0]] >= 0.5) == (p2[opts[1]] >= 0.5), "system": "jev9b"}
    if x.escalate and out["confidence"] < x.escalate.threshold:
        e = _escalate(x.escalate, q, f"Question:\n{x.question}\n\nResponse A:\n{x.response_a}\n\nResponse B:\n{x.response_b}",
                      "Which response is better?", opts)
        if e["choice"]:
            out.update({"winner": "A" if e["choice"] == opts[0] else "B", "system": e["system"]})
        out["escalation_cost_usd"] = e["cost_usd"]
    out["latency_s"] = time.perf_counter() - t0
    out["cost_usd"] = _gpu_cost(out["latency_s"]) + out.get("escalation_cost_usd", 0.0)
    return out


def score_one(x: JudgeIn) -> dict:
    t0 = time.perf_counter()
    p = jev().decide(x.criterion or SCORE_Q, state=f"Question:\n{x.question}\n\nResponse:\n{x.response}", kind="score")
    exp = sum(int(k) * v for k, v in p.items())
    lat = time.perf_counter() - t0
    return {"expected_score": exp, "score": int(round(exp)), "distribution": p, "confidence": max(p.values()),
            "system": "jev9b", "latency_s": lat, "cost_usd": _gpu_cost(lat)}


def decide_one(x: DecideIn) -> dict:
    t0 = time.perf_counter()
    p = jev().decide(x.question, state=x.state, options=x.options)
    best = max(p, key=p.get)
    out = {"choice": best, "distribution": p, "confidence": p[best], "system": "jev9b"}
    if x.escalate and p[best] < x.escalate.threshold:
        e = _escalate(x.escalate, "Choose the correct option.", x.state, x.question, x.options)
        if e["choice"]:
            out.update({"choice": e["choice"], "system": e["system"]})
        out["escalation_cost_usd"] = e["cost_usd"]
    out["latency_s"] = time.perf_counter() - t0
    out["cost_usd"] = _gpu_cost(out["latency_s"]) + out.get("escalation_cost_usd", 0.0)
    return out


@app.get("/v1/health")
def health():
    return {"status": "ok", "model": "autotrust/JEV-9B@b63f651", "vllm_url": os.environ.get("VLLM_URL", "http://127.0.0.1:8000")}


@app.post("/v1/judge", dependencies=[Depends(auth)])
def judge(x: JudgeIn):
    return judge_one(x)


@app.post("/v1/compare", dependencies=[Depends(auth)])
def compare(x: CompareIn):
    return compare_one(x)


@app.post("/v1/score", dependencies=[Depends(auth)])
def score(x: JudgeIn):
    return score_one(x)


@app.post("/v1/decide", dependencies=[Depends(auth)])
def decide(x: DecideIn):
    return decide_one(x)


@app.post("/v1/batch", dependencies=[Depends(auth)])
def batch(x: BatchIn):
    fn = {"judge": (judge_one, JudgeIn), "compare": (compare_one, CompareIn), "score": (score_one, JudgeIn),
          "decide": (decide_one, DecideIn)}[x.mode]
    return {"results": [fn[0](fn[1](**it)) for it in x.items]}
