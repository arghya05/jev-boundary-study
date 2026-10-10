# Preregistration and execution freeze (M3)

Frozen 2026-10-10, after the development pilot and **before any held-out (final-panel) model call**. The git commit that adds this file to the public repository (github.com/arghya05/jev-boundary-study) is its timestamp. Any later deviation is listed in §9 with its reason; nothing below is changed after final outcomes are seen.

## 1. Systems (exact configurations)

| Key | Model | Configuration |
|---|---|---|
| `jev9b-s1` | autotrust/JEV-9B @ `b63f651c` (community distillation of TypeSafe Jev 1.13; **not** official Jev) | System 1 choice head via vLLM 0.31.0 LoRA `jev-decision`; head bias + per-kind temperature (0.984) applied client-side; one prefill pass; no truncation (max-model-len 32,768) |
| `astra-high` | gpt-6-astra | OpenAI Responses API, `reasoning.effort=high`, `max_output_tokens=32000`, strict JSON schema `{answer: enum}`, no tools, `store=false` |
| `fable-high` | claude-fable-5-1 | Anthropic Messages, adaptive thinking (default, always on), `output_config.effort=high`, `max_tokens=32000`, JSON-schema output, no tools, **no refusal fallback** |
| `jev9b-s2` (supplementary) | same JEV-9B weights, base lm_head (Qwen3.5-9B) | `enable_thinking=true`, temperature 0.6, top-p 0.95, max_tokens 16,000; same canonical text + one-line JSON answer request |

Official TypeSafe Jev is not evaluated (no API access; weights not public). All conclusions name JEV-9B.

## 2. Panels and denominators

| Panel | Rows | Independent clusters | Role |
|---|---:|---:|---|
| FOLIO v0.0 validation (`5d7bb84`) | 204 | 73 stories | primary, natural deduction |
| ANLI test_r3 | 1,200 | 1,128 premises | primary, adversarial NLI |
| Controlled dependency panel, 48 sealed seeds (424242–424289) | 288 base + 96 paired controls + 32 exploratory evidence-removal | 48 graph seeds | primary for G01 |
| JudgeBench gpt + claude | 350 + 270 | 268 source questions | secondary (inputs exceed JEV-9B's 1,024-token training length) |
| Banking77-16 test | 3,080 | 3,080 | secondary (16 candidates: gold + 15 nearest train-centroid labels, identical for every system; not the 77-way benchmark) |

All rows of every listed panel are run for every system. Operational failures (error, refusal, truncation, invalid) are scored incorrect and stay in the denominator. Panel task-hash digests are in `manifests/datasets_manifest.json`.

## 3. Hypotheses

**H1 (G01, primary, two-sided).** On the controlled panel, the depth × system interaction
`DID = [acc_JEV(d5) − acc_JEV(d1)] − [acc_F(d5) − acc_F(d1)]` differs from zero, for F ∈ {astra-high, fable-high}. The pilot predicted negative (JEV-9B degrades, frontiers do not); a positive or null result is reported as such.

**H1b.** The irrelevant-context effect `DID(c8 vs c0)` is smaller in magnitude than the depth effect for JEV-9B (i.e. length alone does not explain the depth effect). Text length is matched across depths by construction (mean 465 vs 466 characters).

**H1c (mechanism, supplementary).** JEV-9B System 2 (same weights, thinking) shows no depth decline comparable to System 1: the System-1 vs System-2 DID across d1→d5 is negative.

**H2 (public panels, primary).** For each primary panel (FOLIO, ANLI) and each frontier, classify per §5. Secondary panels (JudgeBench, Banking77-16) use the same rule but are reported as secondary.

**H3 (G03).** A pre-call feature rule (7 surface features, `router.FEATURES`) and the feature rule + JEV-9B confidence achieve accuracy within 2 points of always-frontier at lower cost more often than (a) length-only, (b) task-family lookup, (c) a JEV-9B confidence gate alone, under leave-one-family-out over all five families and on the unseen controlled template T2. The oracle is reported as an unattainable bound.

## 4. Analysis

* Primary family for H2: 2 primary panels × 2 frontiers = 4 comparisons; Bonferroni α = 0.05/4 for the two-sided intervals. Secondary family (JudgeBench gpt, JudgeBench claude, Banking77-16 × 2 frontiers = 6) is adjusted separately (α = 0.05/6).
* Interval: Newcombe hybrid score paired interval when every cluster has one row; otherwise percentile cluster bootstrap (B = 10,000) over the stated clusters. Simulation coverage at 40–204 clusters: 0.94–0.96 (pilot check, `stats.simulate_coverage`).
* H1 family: 2 frontiers × {depth5 vs 1, depth3 vs 1, context 8 vs 0} = 6 DIDs, Bonferroni α = 0.05/6, cluster bootstrap over 48 seeds.
* Noninferiority margin: 2 accuracy points, fixed. A comparison with fewer than 20 independent clusters is "inconclusive".
* Paired controls: decision-changing (follows the verified label change) and decision-preserving (answer invariance under renaming + reordering) rates per system, descriptive with Wilson intervals.

## 5. Decision rule (per panel × frontier)

JEV-9B more accurate if adjusted lower bound of Δ > 0; comparable and cheaper if lower bound > −0.02 and JEV-9B's measured cost is lower; frontier materially more accurate if upper bound < −0.02; otherwise inconclusive.

## 6. Cost and latency tracks

* Accuracy runs: synchronous API calls with client concurrency 8, provider order randomised per item; cost = actual billed usage × dated list prices (`manifests/rate_card.json`). A batch-price view (×0.5, both providers support batch for these models) is reported as a derived view, not a measured operating point.
* JEV-9B cost = A40 pod $/hr × measured GPU wall-clock for the panel (not per-call latency sums, which overstate under concurrency). An "official Jev list-price" view ($0.042/M input) is shown for context only.
* Latency track: a sealed 100-item FOLIO subset at concurrency 1, nonstreaming, interleaved provider order. JEV-9B latency is local GPU time without a network hop and is not compared as like-for-like with remote APIs.

## 7. Robustness and ablations (prespecified)

1. **Option-order reversal**: FOLIO (204) and the controlled base panel (288) with choices reversed, all four systems; report flip rates.
2. **Effort sensitivity**: `astra-max` and `fable-max` on FOLIO and the controlled base panel.
3. **System 1 vs System 2** at fixed weights (H1c), all panels.
4. **Length strata**: JudgeBench and ANLI by input length (≤ / > 1,024 JEV tokens).
5. **Exploratory G02**: evidence-removed items (32), descriptive only.

## 8. Stopping rules

Stop new paid calls and review if: actual spend exceeds the conservative forecast (`results/forecast.csv`) by 50%; a model's resolved version changes mid-run; failure rate for any system exceeds 10% on a panel (investigate before continuing). Never retry because an answer is wrong; at most one transient-transport retry.

## 9. Deviations from PLAN.md (declared before final calls)

1. Official Jev → JEV-9B (no access). All claims renamed.
2. Banking77 presented with 16 candidates (JEV-9B maximum); secondary only.
3. JudgeBench secondary (out-of-training-length inputs for JEV-9B; no truncation applied).
4. G02 exploratory only (novelty review).
5. Human blinded fidelity review of controlled items replaced by an automated round-trip parse of every sentence back to its formula plus two independent reference scorers; no human reviewers were available. This is a limitation.
6. Primary accuracy uses synchronous calls (measured frontier cost was ~$0.004–0.03 per item, so the batch discount does not change any conclusion); batch prices reported as derived.
7. Added arm `jev9b-s2` (novelty review recommendation).
8. 2026-10-10 operational incident: a code-sync error deleted raw result files and the spend ledger on the pod during the pilot. Panels were regenerated with identical task-hash digests; results and ledger were rebuilt from the response cache (`jevstudy restore`); no call was repeated or lost except one $0 credit-error response.

## 10. Amendments (declared 2026-10-10 during the final run, before any final-panel outcome was analysed)

Both amendments are **exploratory**; they do not enter the primary or secondary testing families.

* **A1 — deeper controlled extension.** The pilot put both frontiers (and JEV-9B System 2) at ceiling at depth 5, so the frontier side of the depth interaction is uninformative at 1/3/5. `controlled_deep`: 24 fresh seeds (777000–777023), depths 1/5/9, 12 rules, 8 irrelevant facts, template T1 (72 items; mean evidence length 862/866/863 characters). All four systems. Reported descriptively with cluster-bootstrap intervals. The brute-force reference scorer was generalised to decide entailment per connected predicate component (exact); the frozen controlled panels' gold labels were re-derived and are byte-identical.
* **A2 — ProofWriter bridge to official Jev.** Hard-Decisions v0.1.0 (MIT; results 2026-10-09) publishes official Jev's open-world ProofWriter accuracy by proof depth (0.977, 0.877, 0.848, 0.799, 0.719, 0.810 for depths 0–5) but not its item IDs. `proofwriter_bridge`: 900 items from tasksource/proofwriter test (`ee4d22d`), OWA, 50 per depth × label, sealed seed, with Hard-Decisions' task wording verbatim. JEV-9B System 1 only. Compared at the distribution level (same depth strata and label balance, different items); this is partial external-validity evidence about the student–teacher gap, not evidence about official Jev on our panels.
