# JEV-as-a-Judge HTTP API

A self-hosted LLM-as-a-judge service backed by **JEV-9B** (one forward pass, calibrated probabilities),
with optional escalation of low-confidence items to JEV-9B's own reasoning mode or to a frontier model.

## Run it

```bash
# one GPU container (vLLM + API)
docker build -t jev-judge -f deploy/Dockerfile .
docker run --gpus all -p 8080:8080 -e JUDGE_API_KEY=change-me jev-judge

# or, next to an existing vLLM server (see docs/STARTUP_GUIDE.md)
pip install -e '.[server]'
VLLM_URL=http://127.0.0.1:8000 JUDGE_API_KEY=change-me uvicorn jevstudy.server:app --port 8080
```

All `POST` endpoints require `Authorization: Bearer $JUDGE_API_KEY` when `JUDGE_API_KEY` is set.
Interactive docs are served at `/docs`.

## Endpoints

| Endpoint | Body | Returns |
|---|---|---|
| `POST /v1/judge` | `question`, `response`, `criterion?` | `p_correct`, `verdict`, `confidence` |
| `POST /v1/compare` | `question`, `response_a`, `response_b`, `criterion?` | `p_a_better`, `winner`, `position_consistent` (asked in both orders and averaged) |
| `POST /v1/score` (**experimental**) | `question`, `response`, `criterion?` | 0–5 `distribution`, `expected_score`, `score` |
| `POST /v1/decide` | `question`, `options` (2–16), `state?` | `distribution`, `choice` |
| `POST /v1/batch` | `mode` ∈ judge/compare/score/decide, `items` (≤ 1,000) | `results` |
| `GET /v1/health` | — | model and backend |

Every response includes `system` (which model decided), `confidence`, `latency_s` and `cost_usd`
(GPU time at `GPU_USD_PER_HR`, plus any escalation charge).

### Escalation

Add `"escalate": {"to": "self", "threshold": 0.9}` to send items below the threshold to JEV-9B's own
thinking mode (same GPU, no API bill), or `{"to": "astra" | "fable", "threshold": 0.9, "api_key": "<your key>"}`
to use GPT-6 Astra or Claude Fable 5.1 with your own provider key (never stored or logged).
Choose the threshold from the coverage curve that `jevstudy judge` reports on a labelled sample of your task.

## Example

```bash
curl -s localhost:8080/v1/compare -H "Authorization: Bearer change-me" -H 'content-type: application/json' -d '{
  "question": "Is 91 prime?",
  "response_a": "Yes, 91 has no divisors other than 1 and itself.",
  "response_b": "No, 91 = 7 x 13.",
  "escalate": {"to": "self", "threshold": 0.9}}'
```

## Know its limits

`/v1/score` is **experimental and not validated by the paper**: in a smoke test it rated a correct
one-sentence explanation 1.7/5. Prefer `/v1/judge` (pass/fail) and `/v1/compare` (pairwise), which the
paper evaluates on HaluEval-QA, RewardBench and JudgeBench.

JEV-9B is a community distillation of TypeSafe Jev 1.13, trained on inputs of at most 1,024 tokens and
up to 16 options. The paper measures where it is reliable and where it is not: it is weak on multi-step
reasoning, which is exactly what escalation is for. Validate on your own labelled data before relying on
it (`jevstudy custom`, `jevstudy judge` with labels).
