# Startup guide: cheap, calibrated LLM evaluation with JEV-9B

This guide takes you from zero to evaluating your own LLM outputs with **JEV-9B** (an open-weights,
one-forward-pass decision model) and escalating only the uncertain items to a frontier model.
Every recommendation here comes from the measurements in the [paper](../research-paper/JevBoundary_Paper.pdf);
read its limitations before relying on it for high-stakes decisions.

## 1. Why use a decision model as a judge?

| | JEV-9B (one pass) | Frontier LLM-as-judge (GPT-6 Astra / Claude Fable 5.1, high effort) |
|---|---|---|
| Cost per 1,000 judgements | cents of GPU time | dollars to tens of dollars |
| Latency | ~0.1 s on one A40 | seconds per call |
| Output | a calibrated probability per option | a label (no calibrated probability) |
| Runs privately on your GPU | yes | no |
| Multi-step reasoning | weak (degrades with dependency depth) | strong |

The practical pattern is therefore **JEV-9B first, frontier only when JEV-9B is unsure** — and to
measure, on a labelled sample of *your* task, whether that pattern keeps the accuracy you need.

## 2. Serve JEV-9B

On any GPU host with ≥ 24 GB (an A40/L40S/A6000 at ≈ $0.35–0.80/h on RunPod works):

```bash
pip install "vllm==0.31.0" "git+https://github.com/arghya05/jev-boundary-study"
jevstudy serve --model-dir JEV-9B              # downloads autotrust/JEV-9B@b63f651 (~18 GB) and starts vLLM on :8000
```

`runpod/pod.sh create && runpod/pod.sh sync && runpod/pod.sh ssh 'bash /workspace/jev/runpod/setup_remote.sh && bash /workspace/jev/runpod/start_vllm.sh'`
does the same on a fresh RunPod pod. Stop the pod when you are not using it.

## 3. Judge your model's outputs

```bash
export VLLM_URL=http://127.0.0.1:8000
# pass/fail ("is this response correct?")
jevstudy judge --input my_outputs.jsonl --mode pointwise --out judged/
# A vs B
jevstudy judge --input my_pairs.jsonl --mode pairwise --out judged_pairs/
# 0-5 rubric score
jevstudy judge --input my_outputs.jsonl --mode score --criterion "Rate factual accuracy from 0 to 5." --out scored/
# escalate anything JEV-9B is < 90% sure about to GPT-6 Astra
OPENAI_API_KEY=... jevstudy judge --input my_pairs.jsonl --mode pairwise --escalate astra --threshold 0.9 --out judged_pairs/
```

Input rows (JSON lines; `label` is optional and enables agreement metrics):

```json
{"id": "1", "question": "What is 17 * 3?", "response": "51", "label": true}
{"id": "2", "question": "Is 91 prime?", "response_a": "Yes.", "response_b": "No, 91 = 7 x 13.", "label": "B"}
```

`judged/summary.json` reports agreement with your labels (with a 95% interval), JEV-9B's AUROC, how
many items were escalated, total cost, and a **coverage curve**: for each confidence threshold, the
share of items JEV-9B keeps and its accuracy on them. Pick the threshold from that curve.

From Python:

```python
from jevstudy.toolkit import JevClient, Router
jev = JevClient("http://127.0.0.1:8000")
jev.judge("What is 17*3?", "51")                       # -> P(correct)
jev.compare("Is 91 prime?", "Yes.", "No, 91 = 7 x 13.") # -> {"A": ..., "B": ...}
router = Router(jev, frontier="fable", threshold=0.9)  # JEV-9B when confident, Claude otherwise
```

## 4. Before you trust it: prove it on your task

```bash
jevstudy custom --tasks my_labelled_tasks.jsonl --systems jev-s1,astra --stage-forecast 5 --out my_check/
```

Each task: `{"id", "instructions", "evidence", "question", "choices": [...], "answer": "<one choice>"}`.
The command runs both systems on identical canonical prompts and writes `my_check/report.md` with
accuracy and cost for each system, the paired accuracy difference with a 95% interval, a frozen
**verdict** (JEV-9B more accurate / comparable and cheaper / frontier materially better / inconclusive,
using a 2-point margin), and a confidence-gate table showing how accuracy and cost move as you
escalate more items. `--stage-forecast` stops paid calls before your spend would exceed it.

A sample of 200–500 labelled items from your real traffic is usually enough to see whether the gate
reaches the frontier's accuracy band; fewer than ~20 independent items is reported as inconclusive.

## 5. What the paper found (read before deploying)

* JEV-9B is far cheaper and faster than both frontiers on every panel.
* On reasoning-heavy tasks (FOLIO deduction, adversarial NLI, deep rule chains) it is **materially less
  accurate**; its accuracy falls with dependency depth while the reasoning models' does not.
* The same weights with thinking enabled (JEV-9B System 2) recover most of that gap at local GPU cost —
  the JEV-H harness uses this instead of a paid API for uncertain items.
* See the paper's judge-track tables (RewardBench, HaluEval-QA, JudgeBench) for judging accuracy, and
  its routing tables for how much of the frontier's accuracy a confidence gate keeps at what cost.

## 6. Cost control checklist

* Use `--stage-forecast` on every paid command; it reserves the configured maximum before each call.
* Use batch APIs (`jevstudy batch-submit` / `batch-collect`) for offline evaluation — half price.
* Responses are cached by exact content, model and settings: re-running never re-bills an answered item.
* Stop GPU pods when idle (`runpod/pod.sh stop`).
