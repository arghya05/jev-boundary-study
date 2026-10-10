# jev-judge — cheap, calibrated LLM evaluation with a one-pass decision model

[![Tests](https://github.com/arghya05/jev-boundary-study/actions/workflows/test.yml/badge.svg)](https://github.com/arghya05/jev-boundary-study/actions/workflows/test.yml)
[![Release](https://img.shields.io/github/v/release/arghya05/jev-boundary-study)](https://github.com/arghya05/jev-boundary-study/releases)
![License](https://img.shields.io/badge/license-Apache--2.0-blue)

> 📄 **Research paper:** [*When Can a Decision Model Replace a Reasoning LLM? Controlled, Cost-Accounted Evidence for a Distilled One-Pass Judge*](research-paper/JevBoundary_Paper.pdf) (preprint, NeurIPS 2026 style) · [LaTeX source](research-paper/) · [preregistration](research/PREREGISTRATION.md) · [item-level results](results/final_item_level.csv)

**jev-judge** lets you use **JEV-9B** — an open-weights, one-forward-pass decision model (a community
distillation of TypeSafe Jev 1.13) — as an **LLM-as-a-judge** that costs fractions of a cent, answers in
under a tenth of a second and returns a calibrated probability, and escalates the items it is unsure about
to its own reasoning mode or to a frontier model. It ships with the fair-comparison protocol from the paper
so you can **prove on your own data** whether it is good enough before you rely on it.

### Research results at a glance

Every number below is regenerated from committed evidence by
[`src/jevstudy/paper_assets.py`](src/jevstudy/paper_assets.py); the paper states the conditions, comparators
and limitations of each. Frontier models: **GPT-6 Astra** and **Claude Fable 5.1**, both at high reasoning effort.
JEV-H = our harness (two option orders, escalate below 0.90 confidence to JEV-9B's own thinking mode).

| Question | Benchmark | JEV-9B / JEV-H | Frontier | Verdict |
|---|---|---|---|---|
| Pairwise judging of chat responses | RewardBench, 500 sealed pairs | JEV-H **94.4%** at $0.65 / 1k | Astra 93.8% ($4.01), Fable 90.2% ($5.78) | **JEV-H best measured**; ahead of Fable (+4.2 [+0.4, +8.2]) only because Fable refuses 25 Safety pairs — tied without them (94.1 vs 94.9); tied with Astra |
| One-pass judging, no escalation | RewardBench | JEV-9B 87.0% at $0.17 / 1k | Fable 90.2% | Within 1.8 points of Fable [−6.4, +2.6], ~34× cheaper; inconclusive |
| Hard correctness judging | JudgeBench (partial, 349 rows) | JEV-9B 68.2%, JEV-H 88.2% | ~94% | **Frontier better** |
| Hallucination detection | HaluEval-QA, 1,000 | JEV-9B 82.7%, JEV-H 87.7% | 90.6–93.3% | Frontier better — and answer **length alone** scores AUROC 0.976 here |
| Natural-language deduction | FOLIO, 204 | JEV-9B 69.6%, JEV-H 84.3% | 86.8–90.2% | One-pass: frontier materially better; harness: inconclusive |
| Adversarial NLI | ANLI r3, 1,200 | JEV-9B 64.2%, JEV-H **74.6%** | 74.9–77.3% | Harness within 0.3 points of Astra |
| Same weights with thinking | FOLIO | JEV-9B S2 **85.8%** at $0.61 / 1k | Astra 86.8% at $8.97 / 1k | The one-pass deficit is computation, not knowledge |
| Does dependency depth drive one-pass errors? | Controlled panel, length-matched | DID depth 5 vs 1: −5.2 [−24, +14] | — | **Not supported** (preregistered hypothesis failed) |
| Interactive latency | 100 FOLIO items, concurrency 1 | **0.08 s** median | 1.9–2.7 s | ~25–35× faster |
| Does it transfer to official Jev? | ProofWriter depth 5 | JEV-9B 40.6% | official Jev 81.0% | **No** — the student is not the teacher |

Whole study: **$65.04** in API calls plus **$3.66** of A40 GPU time.

## Quickstart

```bash
pip install "https://github.com/arghya05/jev-boundary-study/releases/download/v0.1.0/jev_judge-0.1.0-py3-none-any.whl" "vllm==0.31.0"
# (PyPI: `pip install jev-judge` once the first PyPI release is live)
jev-judge serve --model-dir JEV-9B                    # downloads autotrust/JEV-9B@b63f651 and starts vLLM (GPU >= 24 GB)
jev-judge judge --input examples/judge_pairwise.jsonl --mode pairwise --out judged/
```

Python:

```python
from jevjudge import JevClient, Router
jev = JevClient("http://127.0.0.1:8000")
jev.compare("Is 91 prime?", "Yes.", "No, 91 = 7 x 13.")      # {'A': 0.0001, 'B': 0.9999}
jev.judge("What is the capital of Australia?", "Sydney.")      # P(correct) = 0.10
Router(jev, frontier="fable", threshold=0.9)                   # JEV-9B when confident, Claude otherwise
```

HTTP API (self-hosted LLM-as-a-judge service, see [docs/API.md](docs/API.md)):

```bash
docker build -t jev-judge -f deploy/Dockerfile . && docker run --gpus all -p 8080:8080 -e JUDGE_API_KEY=change-me jev-judge
curl -s localhost:8080/v1/compare -H "Authorization: Bearer change-me" -H 'content-type: application/json' \
  -d '{"question":"Is 91 prime?","response_a":"Yes.","response_b":"No, 91 = 7 x 13.","escalate":{"to":"self","threshold":0.9}}'
```

**Before you trust it on your task**, run the paper's protocol on a labelled sample of your own data:

```bash
jev-judge custom --tasks my_labelled_tasks.jsonl --systems jev-s1,astra --stage-forecast 5 --out my_check/
```

It reports accuracy and cost for each system, the paired difference with a 95% interval, a frozen verdict
(more accurate / comparable and cheaper / frontier better / inconclusive) and the accuracy-vs-escalation
curve for choosing a threshold. See the [startup guide](docs/STARTUP_GUIDE.md).

## When to use it — and when not to

* **Use it** as the default first-pass judge for pairwise preference and pass/fail judgements, with escalation on;
  for classification-style decisions; anywhere volume, latency or privacy matter.
* **Do not use it alone** for judgements that require multi-step reasoning or factual verification of long answers
  (JudgeBench, deduction): escalate, or use a frontier model. Its probabilities are well calibrated on chat
  judging (ECE 0.026) but **overconfident by 6–11 points on reasoning tasks** — recalibrate on your data.
* `/v1/score` (0–5 rubric) is experimental and not validated by the paper.

## What is in this repository

| Path | Contents |
|---|---|
| [`src/jevstudy/`](src/jevstudy/) (`jevjudge` alias) | Judge toolkit and HTTP API; gold-blind study package: canonical tasks, dataset builders, controlled generator with two independent reference scorers, provider adapters, spend ledger and cache, statistics, routing, JEV-H harness, paper assets |
| [`research-paper/`](research-paper/) | Paper PDF, LaTeX source, generated tables, figures and number macros |
| [`research/`](research/) | Original plan, novelty audits and decision, **preregistration with amendments A1–A6** |
| [`results/`](results/) | Item-level predictions, summaries, spend ledger, run logs |
| [`manifests/`](manifests/) | Dataset sources with SHA-256, model revisions, rate card, sealed IDs and samples |
| [`docs/`](docs/) | Startup guide and API reference |
| [`deploy/`](deploy/), [`runpod/`](runpod/) | Docker image; RunPod lifecycle and full-run scripts |
| [`tests/`](tests/) | 31 tests: gold exclusion, prompt parity, cache keys, cost accounting, retries, scorer agreement, interval behaviour, harness rules, API |

## Scope and honesty notes

* **Not official Jev.** No API access was available; every decision-model result is about `autotrust/JEV-9B@b63f651`, which
  the paper shows tracks its teacher on shallow reasoning but not deep reasoning.
* **Preregistered, with every deviation declared** before the affected results existed (budget-driven reductions included).
* **Failures count.** Errors, refusals, truncations and invalid outputs stay in every denominator.
* **No dataset text is redistributed**; panels are rebuilt from pinned sources (`jev-judge prepare`).

## Reproduce

```bash
pip install -e '.[test,server]' && pytest -q
runpod/pod.sh create && runpod/pod.sh sync && runpod/pod.sh secrets
runpod/pod.sh ssh 'cd /workspace/jev && bash runpod/setup_remote.sh && bash runpod/start_vllm.sh'
# on the pod:
jev-judge prepare && jev-judge variants --harness && jev-judge amendments && jev-judge judge-track
bash runpod/full_run.sh            # see research/PREREGISTRATION.md for the lean scope actually run
python -m jevstudy.harness --root . && python -m jevstudy.paper_assets --root . --out research-paper
```

## License

Apache-2.0 (see [LICENSE](LICENSE) and [NOTICE](NOTICE)). Original implementation; JEV-9B and the benchmark datasets are
used under their own licences and are not redistributed.

## Citation

```bibtex
@misc{mukherjee2026jevjudge,
  title  = {When Can a Decision Model Replace a Reasoning LLM? Controlled, Cost-Accounted Evidence for a Distilled One-Pass Judge},
  author = {Mukherjee, Arghya},
  year   = {2026},
  url    = {https://github.com/arghya05/jev-boundary-study}
}
```
