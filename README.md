# When Can a Decision Model Replace a Reasoning LLM?

> 📄 **Research paper:** [*When Can a Decision Model Replace a Reasoning LLM? Controlled Evidence on Accuracy, Depth and Cost*](research-paper/JevBoundary_Paper.pdf) (preprint) · [LaTeX source](research-paper/) · [preregistration](research/PREREGISTRATION.md) · [item-level results](results/final_item_level.csv)

A controlled, preregistered comparison of **JEV-9B** — an open-weights community
distillation of the one-pass decision model TypeSafe Jev 1.13 — against
**GPT-6 Astra** and **Claude Fable 5.1** with native reasoning at high effort,
plus a **same-weights reasoning arm** (JEV-9B's own base model with thinking on).

### Research results at a glance

<!-- RESULTS-TABLE:START -->
*Final results are being collected; this table is regenerated from `results/final_summary.json` when the run completes.*
<!-- RESULTS-TABLE:END -->

## What is in this repository

| Path | Contents |
|---|---|
| [`src/jevstudy/`](src/jevstudy/) | Gold-blind study package: canonical tasks, dataset builders, controlled generator with two independent reference scorers, provider adapters, spend ledger and cache, statistics, routing, paper assets |
| [`tests/`](tests/) | Tests for gold exclusion, prompt parity, cache keys, cost accounting, retries, scorer agreement, interval behaviour |
| [`research/`](research/) | Original plan, novelty audits, **novelty decision**, **preregistration** and amendments |
| [`manifests/`](manifests/) | Dataset sources with SHA-256, model revisions, rate card, development IDs, latency subset |
| [`results/`](results/) | Pilot analysis, cost forecast, spend ledger, final summary and item-level predictions |
| [`research-paper/`](research-paper/) | Paper PDF, LaTeX source, generated tables and figures |
| [`runpod/`](runpod/) | Pod lifecycle, vLLM serving and the full-run scripts |

## Scope and honesty notes

* **Not official Jev.** No API access was available; every decision-model claim is about JEV-9B (`autotrust/JEV-9B@b63f651`).
* **Matched content, not matched interfaces.** All systems get identical instructions, evidence, question and choices; transport wrappers differ and are published.
* **Failures count.** Errors, refusals, truncations and invalid outputs stay in every denominator.
* **No dataset text is redistributed.** Panels are rebuilt from pinned sources by `jevstudy prepare`; only the controlled panels (generated here) are committed.

## Reproduce

```bash
pip install -e '.[test]' && pytest -q            # local checks
runpod/pod.sh create && runpod/pod.sh sync && runpod/pod.sh secrets
runpod/pod.sh ssh 'cd /workspace/jev && bash runpod/setup_remote.sh && bash runpod/start_vllm.sh'
# on the pod:
jevstudy prepare && jevstudy variants && jevstudy amendments
bash runpod/full_run.sh
python -m jevstudy.paper_assets --root . --out research-paper
```

Requires `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` and `HF_TOKEN` in the pod's secrets file (never committed).
