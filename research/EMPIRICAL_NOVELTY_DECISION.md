# Empirical novelty decision (Stage 0, step 2)

Reviewed 10 October 2026. This is a targeted desk re-check, not a systematic review. Sources were read through web fetches of the abstract or HTML, model cards and READMEs. "Inspected" means that the stated sections were read. It does not mean that a result was reproduced. No inference was run and $0 was spent. **This document does not certify novelty.**

## 0. Scope change since the earlier audits

Official TypeSafe Jev API access is unavailable. The user chose to replace it with **`autotrust/JEV-9B`** ([model card](https://huggingface.co/autotrust/JEV-9B)), served with vLLM on RunPod. This overrides the handoff line "community checkpoints are not substitutes" by explicit user decision. Every claim must therefore refer to **"JEV-9B, a community distillation of Jev 1.13"** and never to official Jev.

Facts from the model card that matter for this study (author-reported and unverified):

- Architecture: frozen Qwen3.5-9B, plus a LoRA (r=16) and a 24-slot fp32 decision head (~40M trainable parameters). It was distilled by KL from Jev 1.13 output distributions on ~498k teacher-labelled rows. It is not affiliated with TypeSafe.
- Interface limits: `choice` accepts 2–16 options; `noul` is yes/no; `score` is 0–5. **Inputs over 1,024 tokens are truncated** (head 60% / tail 40%) unless the limit is raised, and training used inputs of ≤1,024 tokens.
- Fidelity to the teacher: choice top-1 agreement is 90.2% and mean KL is 0.019 in distribution. The out-of-distribution KL is 0.234. On a gold benchmark the student trails the teacher at every option count (2/4/8/16 options: 0.868/0.774/0.735/0.694 vs 0.890/0.801/0.782/0.769). Option-shuffle flips are 11.5% for the student vs 7.0% for the teacher.
- The card states that the model "mirrors the teacher's mistakes … including in multi-hop reasoning, arithmetic, dates, counting".
- The same weights also serve a **System 2** path (the base Qwen3.5-9B with `enable_thinking`). This gives a same-weights reasoning control that official Jev never offered.

Comparators: `gpt-6-astra` at high reasoning effort and `claude-fable-5-1` with adaptive thinking at high effort. Both were proposed in PLAN.md; their availability and prices must be rechecked in Stage 0 step 3.

## 1. Closest prior work: re-check results

### 1a. The S01–S16 register (from GAP_INVENTORY.md), rechecked for G01/G03 relevance

| ID | Source | Re-check finding relevant to G01/G03 | Overlap with this study |
|---|---|---|---|
| S01 | [Evaluating and Benchmarking the System One Model Jev, 2609.37647](https://arxiv.org/html/2609.37647v1) | Full HTML searched (first ~100k of 104k characters). There is **no analysis by depth or hop count, and no ProofWriter, ProntoQA or FOLIO**. Section 4.1.4 notes weak spots on tasks needing "several steps". The baselines have thinking disabled. The limitations section expects reasoning to raise baseline accuracy. | Low for the depth mechanism. High for the general "where Jev is weak" framing. |
| S02 | [JEV-as-a-Judge, 2609.26550](https://arxiv.org/html/2609.26550v1) | On JudgeBench, the largest gap is in the reasoning category (68.4% vs 95.9%). The frontier comparators include GPT-6 Astra **at low reasoning effort**. Escalation is confidence-based with a task-level guidance table. **No depth or length features are used as predictors.** | High for "Jev loses on reasoning" and for confidence escalation. Medium for G03. |
| S03 | [jev-frontier-100](https://github.com/softpudding/jev-frontier-100) | 100 items across 10 categories, with uncalibrated easy/medium/hard labels and **no hop control**. Jev 1.13 scores 77% vs 96.7% for Qwen3.5-4B with a 2,048-token thinking budget. Thinking budget strongly moves accuracy. It is exploratory and post hoc. | Medium: reasoning budget versus one-pass, but no controlled depth and no frontier APIs. |
| S04 | [Code Owns the Simulation…, 2610.01834](https://arxiv.org/abs/2610.01834) | Unchanged: externalising computation is prior work. | Affects only the "supplied intermediate consequences" condition. |
| S05 | [JevAdvBench, 2609.31142](https://arxiv.org/html/2609.31142v1) | Unchanged: perturbation and batching controls. | Controls only. |
| S06–S08 | Probability Contracts; Do System One Decisions Add Up?; Beyond Calibration | Unchanged: probability coherence and interfaces. | Not claimed. |
| S09 | [DecisionBench](https://huggingface.co/datasets/Hanno-Labs/decision-bench) | Unchanged: task metadata and reasoning flags. | A "reasoning_required" flag alone is not a G03 contribution. |
| S10–S13 | Security prioritisation, jevotron, JevNext, Open-Jev | Unchanged. Open-Jev already evaluates a community student independently. | "A community model was evaluated" is not new. |
| S14/S15 | [RouteLLM](https://arxiv.org/abs/2406.18665), [FrugalGPT](https://arxiv.org/abs/2305.05176) | Learned routing and cascades are established. | High for any generic routing claim. |
| S16 | [Cheaper, Faster, and Wrong in the Same Places, 2609.29769](https://arxiv.org/abs/2609.29769) | Shared errors limit escalation. | Control: report error overlap. |

### 1b. New close sources found in this pass (not in the S01–S16 register)

| New ID | Source | What it does | Why it matters |
|---|---|---|---|
| **N1 (closest to G01)** | [Hard-Decisions benchmark (Anthus AI, v0.1.0, results 2026-10-09)](https://hard-decisions.anth.us/) | Evaluates decision models on ProofWriter at proof depths 0–5, 3,600 items, open-world and closed-world. Open-world accuracy from depth 0 to depth 5: official Jev 97.7%→81.0%; **GPT-6 Luna with reasoning off** 93.3%→46.0%; Kev-9B 89.3%→41.2%. **Only depth is controlled.** The authors state that length, rule and fact counts, negation and paraphrase covary with depth. No reasoning-enabled frontier and no routing analysis. MIT licence, with a saved-answers results file. | Decision model × depth curves already exist, and in them **official Jev degrades more slowly than a non-reasoning LLM**. G01's distinction narrows to the points in §2. The released Jev answers may provide an **official-Jev external-validity bridge** (§4). |
| N2 | [General Decision Models: Benchmarking and Insights Beyond Jev, 2610.03935](https://arxiv.org/html/2610.03935) | 25 decision-model configurations compared with GPT-6 Luna/Sol (non-thinking) and open models in thinking and non-thinking modes. Thinking adds ~6–9 points. "Reasoning-intensive tasks are not well captured by single-pass distillation." Accuracy is reported against context length, but **there is no depth analysis**, **no reasoning-enabled GPT or Claude**, and no router. | Establishes in general terms that one-pass models trail on reasoning-heavy tasks and that distillation recovers little. G01 must add a *controlled, quantified* depth effect, not the qualitative statement. |
| N3 | [LLM-as-Jev, 2610.02076](https://arxiv.org/html/2610.02076v2) | Shows that general LLMs read out as Jev-style decision models. Long-input (>1,500 token) accuracy suffers when training data is short. | Supports treating JEV-9B's ≤1,024-token training as a length confound to control. |
| N4 | [PostHog Jeeves-9B](https://huggingface.co/PostHog/jeeves) ([wiki](https://github.com/PostHog/jeeves/wiki)) | A Qwen3.5-9B decision model that reasons before choosing. Reports thinking 0.840 vs no-thinking 0.804 on its test split. No depth breakdown and no frontier comparison. | Evidence that reasoning helps decision models. It is an optional extra "reasoning decision model" arm and is not required. |
| N5 | [QMFOL / QMFOLBench, 2606.20227](https://www.alphaxiv.org/abs/2606.20227) | Generated monadic first-order logic tasks with independently controlled depth, width, label type (True/False/Unknown) and distractors. Six reasoning models and two LLMs. Performance declines with complexity, and Unknown/False labels are harder. | **Depth and distractor-controlled generators for reasoning LLMs already exist.** It is unclear whether length is matched. It contains no decision models. |
| N6 | [Reasoning Models Lose their Way with Long Deduction (ProloNg), ICML 2026](https://icml.cc/virtual/2026/82459) | Prolog deduction up to depth 22 and 62k tokens, testing 8 frontier reasoning models. Most fail beyond depth 10. Length grows with depth. | Frontier reasoning models also have depth ceilings. Depths 1/3/5 will probably not saturate the frontiers, so the frontier side of G01 is a known quantity. |
| N7 | [ProofWriter, 2012.13048](https://arxiv.org/abs/2012.13048); [PrOntoQA](https://github.com/asaparov/prontoqa) and its [OOD/distractor extension, 2305.15269](https://arxiv.org/abs/2305.15269); [LogicBench](https://arxiv.org/abs/2404.15522); [Multi-LogiEval](https://arxiv.org/abs/2406.17169) | Classic depth-stratified, distractor-capable deduction benchmarks for LLMs. | Depth controls are **not** new and should be reused or cited (§2). |
| N8 | [Rerouting LLM Routers, 2501.01818](https://arxiv.org/abs/2501.01818); [RouterEval, 2503.10657](https://arxiv.org/abs/2503.10657); [RouterArena, 2510.00202](https://arxiv.org/html/2510.00202v3); [VDAR-Router, 2607.18098](https://arxiv.org/pdf/2607.18098); [Gatekeeper, 2502.19335](https://arxiv.org/abs/2502.19335); [Token-level LM cascades, 2404.10136](https://arxiv.org/abs/2404.10136); TRACER-style surrogate→LLM deferral ([overview, 2604.14531](https://www.alphaxiv.org/overview/2604.14531)) | Learned routers, difficulty-feature routers, classifier→LLM deferral. Confidence-based deferral is "remarkably hard to surpass" for classification cascades. | G03 must beat a **small-model confidence gate**, not only length or family lookup (§3). |
| N9 | Other community students ([persly-jev-9b](https://huggingface.co/persly/persly-jev-9b), [smha1012/jev-9b](https://huggingface.co/smha1012/jev-9b)) | Self-reported KL to the teacher and JevBench gaps relative to Jev. Not peer-reviewed. | Student/teacher gaps are reported on cards. No paper compares a distilled decision student against reasoning frontiers under controlled depth. |

I found no paper, repository or benchmark that crosses **controlled dependency depth × matched length × distractors** against **both a one-pass decision model and high-effort reasoning frontier APIs**. A search that fails to find something is not proof that it does not exist. N1 shows that this space was being populated within the past week.

## 2. Claim-by-claim matrix

| Claim | Already established (sources) | What this study tests | New evidence that would matter | Kill / narrow condition |
|---|---|---|---|---|
| C1. One-pass decision models are weaker than LLMs on reasoning-heavy tasks | S01 §4.1.4, S02 (JudgeBench reasoning gap), S03, N2 | Not claimed as new; used only as background | — | — |
| C2. Accuracy falls with proof depth | ProofWriter, PrOntoQA, LogicBench, Multi-LogiEval, QMFOL, ProloNg for LLMs; N1 for decision models including Jev | Not claimed as new | — | — |
| **C3 (G01 core). Paired depth × model interaction**: with length, rule count and distractors matched, does depth reduce JEV-9B accuracy *more steeply* than for high-effort reasoning gpt-6-astra and claude-fable-5-1? | N1 compares Jev only to *non-reasoning* LLMs, with length confounded. S02 uses *low-effort* frontiers and no depth control. N2/N5/N6 have no decision model or no matched pairing. | Six-cell design: depth 1/3/5 × 0/8 distractors, fixed rule count, length-matched filler, independent derivability labels, seed-clustered paired CIs. | A depth-slope **difference** with an adjusted CI that excludes 0 and survives length and distractor matching. A null interaction under N1's configuration would also be informative. | Interaction CI includes 0 at adequate power, or the effect disappears once length is matched. Report this as a negative result and do not claim a boundary. |
| C4. Same-weights reasoning control (new with JEV-9B) | N2 and N4 show that thinking helps; there is no controlled-depth version | Comparing JEV-9B System 1 with the System 2 thinking path (same Qwen3.5-9B backbone) at each depth isolates "one forward pass vs reasoning" from model scale and family. | System 2 recovers the depth slope while System 1 does not. This is evidence for a computation-not-recognition account that is not confounded by frontier scale. | System 1 and System 2 have similar slopes. Then the frontier advantage reflects scale or knowledge, not reasoning. |
| C5. Recognition vs computation (surface check) | Not established by the sources found | A per-rule surface-recognition probe (depth-1 single-rule items) shows whether deep errors reduce to misreading | Deep errors persist despite near-ceiling single-rule recognition | Surface errors explain the slope. |
| **C6 (G03). Pre-inference feature rule for model sufficiency** | S14/S15/N8 routing; S02 confidence escalation; S09 metadata | A frozen rule over observable features (estimated dependency structure, connective counts, length) compared with length-only, family lookup, **JEV-9B confidence gate**, an established router adaptation, all-X policies and an oracle. Evaluated on unseen templates and leave-one-family-out. | The rule matches or beats the confidence gate at equal or lower cost, or adds to it (feature + confidence), on held-out templates and families. | It does not beat the confidence gate or length-only. Then report G03 as negative and keep it descriptive. |
| C7. Reproducible open-weights decision arm | N1 (open models), N2, Open-Jev | Pinned JEV-9B revision with vLLM, fully re-runnable | The decision-model side is reproducible by anyone. This is an engineering plus, not novelty. | — |
| C8. Cost and quality operating points | S01, S02, N1 | GPU-hour cost for JEV-9B vs API cost for frontiers, both measured | Contributes to deployment guidance only. It is not novel. | — |
| C9. Claims about official Jev | — | **Not tested directly** | Only through the optional N1 bridge (§4) | Never stated without the bridge. Even with it, state it only as partial evidence. |

**Note on depth controls (point 2 of the brief):** ProofWriter, RuleTaker, PrOntoQA (including the multi-distractor OOD variant), LogicBench, Multi-LogiEval, QMFOL and ProloNg already provide depth-stratified and distractor-controlled deduction benchmarks for LLMs. Depth control and a generator are therefore **not** contributions. G01's only candidate addition is the **paired comparison of a one-forward-pass decision model against reasoning-enabled frontier models (plus a same-weights System 2 arm) under jointly matched depth, length, rule-count and distractor controls**. That comparison must be quantified as a depth × model interaction with seed-clustered uncertainty. The study should reuse or align with an existing generator (ProofWriter-style open-world semantics, compatible with N1) rather than present a new one. A bespoke generator is justified only for length matching, and it should be validated against ProofWriter labels.

## 3. Chosen contribution

- **Primary: G01 (C3, with C4 and C5 as mechanism arms) + G03 (C6).**
- **G02: exclude from the primary design.** Reasons: (i) QMFOL (N5) already reports that Unknown/False labels are harder, and S02/S10 cover missing evidence, so the incremental claim is thin. (ii) The premise-removal × depth cells multiply calls and the testing family at a time when the 1,024-token limit already constrains item construction. (iii) Power for C3 is the binding constraint. At most, run a small, separately labelled **exploratory** G02 arm after C3 is powered, with no confirmatory claim.
- G03 adjustments forced by the new setting:
  - JEV-9B confidence is now nearly free (local, ~ms), so "without first buying Jev's confidence" no longer holds. A **confidence-gate baseline is mandatory**, and the honest target is "features add to, or replace, confidence."
  - Hard interface constraints (input >1,024 tokens, >16 options) are trivial routing rules. Report them as **eligibility constraints**, not as findings of the learned rule.

## 4. Consequences of the JEV-9B substitution

What **can** be claimed:
- Behavioural results for "JEV-9B, a community distillation of Jev 1.13" (pinned HF revision, vLLM version, calibration files).
- A same-weights System 1 vs System 2 contrast (C4), which official Jev could not provide. This strengthens the mechanism arm.
- **Reproducibility with open weights, which is a real plus.** Anyone can re-run the decision-model arm without API access or vendor drift. Cost is measured GPU time, not a vendor price.

What **cannot** be claimed:
- Anything about official Jev's accuracy, cost, latency or failure profile. The student trails the teacher on gold accuracy, is more sensitive to option order, has OOD KL 0.234, and was trained only on ≤1,024-token inputs. **External validity to official Jev is untested.**
- That a JEV-9B deficit reflects the "decision-model architecture class" (G19 still applies).
- Cost advantages of the Jev API (no Jev bill exists in this study).

Required design changes:
1. **Item length:** keep every controlled item and canonical prompt ≤1,024 JEV-9B tokens. Log the tokenized length per model. Do not raise the limit in the primary arm because that is out of distribution. Length-matched filler must also fit within the limit.
2. **Panels:** **Banking77 (77 options) is incompatible** with `choice` (≤16). Drop it from the primary scope, or move it to a clearly separate hierarchical-decomposition track that is not the same task. Many JudgeBench items will exceed 1,024 tokens. Either restrict to a pre-registered, length-eligible subset (named as a subset, with the selection bias disclosed) or drop it. **FOLIO** and **ANLI** fit, but this must be verified per item. Narrow the title and claims to logical/NLI decisions.
3. **Option-order control:** with 11.5% shuffle flips, run every JEV-9B item under ≥2 fixed option permutations, average the probabilities, and report the permutation variance. Use the same canonical order for the frontiers.
4. **Serving fidelity:** reproduce the card's client-side head bias and per-kind temperature. Validate against the card's example outputs before any evaluation. Pin the vLLM build (Qwen3.5 support, LoRA on lm_head, `allowed_token_ids`).
5. **Infrastructure:** the plan previously assumed no GPU. JEV-9B needs a RunPod GPU pod. Price it, confirm it before starting (per user instructions), and delete test pods afterwards.
6. **Optional official-Jev bridge (recommended, low cost):** N1 releases saved Jev answers on 3,600 ProofWriter items. Running JEV-9B on the identical items and prompts gives a direct student-vs-teacher agreement and accuracy check, stratified by depth. This is still not official-Jev evidence on *our* matched items. First confirm the licence and that the answers file and prompt format are recoverable.
7. **Hypothesis direction:** N1 shows official Jev degrading *less* than a non-reasoning LLM. Pre-register C3 as two-sided, and include a frontier "reasoning low or off" sensitivity arm, if affordable, so that N1's pattern can be reconciled with ours.

## 5. Verdict: **conditional GO (narrowed), as an empirical extension, not a foundational claim**

GO to Stage 0 steps 3–8 and to a priced pilot only under all of these conditions:

1. Frame the paper as a controlled empirical study of JEV-9B (a community distillation of Jev 1.13) against high-effort reasoning frontiers. Drop "foundational" and every "first" claim. Cite N1, N2, N5 and N6 prominently.
2. The primary hypothesis is the **depth × model interaction under matched length, rule count and distractors** (C3), with the C4 same-weights arm. A main effect of depth is not a result.
3. G03 is evaluated against a JEV-9B confidence gate and an established router adaptation on unseen templates. If it does not beat them, report it as negative.
4. G02 is excluded from confirmatory analysis.
5. Remove Banking77 from the primary scope. Scope JudgeBench to length-eligible items or drop it. All controlled items stay ≤1,024 tokens.
6. Before paid frontier calls, the pilot confirms that: (a) JEV-9B serving reproduces the card's calibration; (b) depth 1/3/5 items can be length-matched within 1,024 tokens; and (c) the frontiers are not at ceiling at depth 5 (otherwise add depths 7/9 within the length limit, or more distractors).
7. A power analysis on pilot discordances shows that the C3 interaction can be estimated to a useful precision with seed-clustered CIs.

**NO-GO / stop triggers:** a paper or benchmark appears (for example, an N1 update) that adds reasoning-enabled frontiers with length matching; the pilot shows the depth effect is explained by length or surface recognition; the frontiers saturate at every feasible depth within the limit; or JEV-9B serving cannot reproduce the card's calibration.

Residual uncertainty: this pass relied on summaries of abstracts and HTML pages for N1–N6, and full methods were not audited. N1 is unpublished and was updated the day before this review. Its full methods, its Jev version and the availability of its saved answers must be read before freezing.
