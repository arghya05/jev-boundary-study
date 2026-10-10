# Public benchmark evidence protocol

Draft, 4 October 2026. No data runs, predictions, or results exist. This is the current empirical-study protocol; the earlier DASC/solver track is superseded.

## Panels and priority

| Family | Source | Final panel | Expected rows |
|---|---|---|---:|
| Logical reasoning, first full-panel candidate | [Yale-LILY/FOLIO](https://github.com/Yale-LILY/FOLIO) | Public validation | 204 |
| Intent classification | [PolyAI author data](https://github.com/PolyAI-LDN/task-specific-datasets), [card](https://huggingface.co/datasets/PolyAI/banking77) | Banking77 test | 3,080 |
| Adversarial inference | [facebook/anli](https://huggingface.co/datasets/facebook/anli) | test_r3 | 1,200 |
| Correctness judging | [ScalerLab/JudgeBench](https://huggingface.co/datasets/ScalerLab/JudgeBench), [author code](https://github.com/ScalerLab/JudgeBench) | gpt and claude, separately scored | 350 and 270 |

Total proposed broad-study rows: **5,104**. Counts must be asserted against the exact pinned release before execution. The 620 JudgeBench rows are response pairs, not necessarily 620 distinct original questions; retain original source/question keys for clustering.

FOLIO is first because its public validation panel is relatively small and tests the reasoning boundary. The budget is flexible, without a numeric ceiling; price additional panels after pilot telemetry and add them for coverage or precision. A fixed public subset has value but cannot be labeled a full-panel score or leaderboard reproduction.

## Development versus final evaluation

The pilot contains 24 cases, six from each family: Banking77 train, ANLI train_r3, FOLIO train with final source-story separation, and independently authored judge-practice cases. JudgeBench final pairs are not used for prompt tuning or rule training. If cross-split FOLIO source stories overlap, exclude the overlapping development story and log the audit; preserve the final evaluation panel.

Separate inferencer inputs from gold labels, ANLI reason/explanation fields, FOLIO logical forms, proof annotations, and any trusted final answers. Gold is accessible to the scorer only. Features and natural-example annotations used to explain performance must be defined without seeing model predictions.

Record author repository/Hugging Face commit, source path, license, downloaded file hash, split, item ID, source-story/question ID, and normalization code hash. Use author Banking77 raw data if the legacy dataset loader is incompatible with the pinned environment. Do not execute unreviewed legacy remote loader code merely to obtain a CSV.

Verify license and upstream task restrictions before redistributing. Hugging Face hosting does not itself confer unrestricted rights. IDs plus retrieval scripts are acceptable when raw text cannot be republished.

## Task definitions and prompts

All models receive identical task information and choice descriptions, using the canonical prompt described in [the fairness protocol](FAIR_COMPARISON_PROTOCOL.md).

- **Banking77:** one customer utterance and the full list of 77 intent labels/descriptions defined by a frozen taxonomy. Do not select a smaller candidate set using gold labels or another model. Map generated labels to author classes using a frozen gold-blind mapping. Accuracy is primary; macro-F1 is secondary.
- **ANLI R3:** premise, hypothesis, and entailment/neutral/contradiction choices. Explain semantics consistently; use the dataset's documented label mapping. Do not expose label, reason, or generator/evaluator metadata.
- **FOLIO:** premises and claim, with the source's true/false/unknown semantics. Preserve full natural-language content and all 204 final rows. Do not filter to a solver-supported subset. Unknown is not abstention. Verify source semantics for inconsistent premises before freezing the instructions.
- **JudgeBench:** question and response A/B; decide the more correct answer under the benchmark objective, not its verbosity or style. Hide gold ranking and response-generator metadata. Score the two published splits separately. Keep native published presentation in the primary benchmark reproduction; a frozen shared A/B reversal is a separately priced robustness condition.

If a prompt or score normalization differs from the publisher's evaluation, identify the deviation and avoid claiming an exact leaderboard reproduction. Completing a published test split under our controlled prompt is a full-panel evaluation of that split, not automatically a new official SOTA entry.

## Required systems and records

Primary systems: direct official Jev, direct OpenAI frontier, direct Claude frontier. Use frozen reasoning-enabled frontier effort settings and adequate output headroom. No solver, decomposition, generated solution, retrieval, memory, or extra Jev prompt is permitted in the primary track.

One prediction record per item/model must include:

- Dataset version, split, item ID, original source cluster ID, task/prompt hash, candidate order, and protocol hash.
- Requested/resolved model ID, native adapter and SDK versions, effort, output limit, output extraction version, and batch/standard status.
- Decision or operational failure, raw response reference, termination reason, timestamps, retries, and transport status.
- Billable input/cache/output/reasoning fields as reported, actual monetary charge or reconciled estimate with provenance, and ledger reservation IDs.

Gold label is joined in a separate scored file after inference. Structured outputs or a frozen label parser are permitted. Do not use another paid LLM to “repair” unfavorable answers. Missing, invalid, truncated, and failed outputs stay in the official denominator unless the source protocol explicitly defines another treatment.

## Completion and stopping

No public-panel inference starts until the complete required comparison has an expected and conservative cost forecast and its statistical precision is credible for the proposed claim. No fixed dollar ceiling is required.

If a service failure or cost anomaly interrupts a panel, label it incomplete and release the prespecified attempted prefix and failure ledger. Do not silently drop missing models or compute an apparent win on the easiest successfully answered cases. Fully paired subset summaries may be diagnostic only, alongside the complete attempted denominator.

Dataset order and source strata are fixed before outcomes. Any cost-related interruption follows accounting or a scope change, never whether Jev is currently winning. Length-correlated stopping can still bias partial results and must be reported.

## Analysis and release

Report full-panel accuracy, paired differences/adjusted intervals, sample and independent-cluster counts, failure rates, and actual cost. Keep per-panel tables; do not average 77-class routing and two-class judging into an unexplained universal score.

Use benchmark-supplied labels, not agreement with a frontier as ground truth. Human label-dispute review is blinded and secondary; retain original official scores and publish the review rule.

The quality margin and multiplicity procedure are frozen before calls. No significant difference is not evidence of equivalence. The draft four-panel design has eight family/provider comparisons; incomplete panels cannot be used to narrow the registered hypothesis family opportunistically.

Release exact prompt/wrapper text, dataset IDs/revisions, predictions where permitted, scorer, analysis settings, dependency locks, and RunPod instructions. Published historical frontier scores may be background only; they cannot replace matched calls under this protocol.

Controlled synthetic tasks supplement the public results. They must not replace the public panels in the abstract or be presented as established frontier leaderboards.
