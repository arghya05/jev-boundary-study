# Gap inventory: 20 questions identified in this review

Updated 4 October 2026. No experiments executed. The budget remains flexible, with no fixed dollar ceiling.

**Answer to the novelty question: only partly.** The plan targets plausible unresolved explanatory questions, but the general idea of identifying where Jev is cheaper or weaker than LLMs is already covered. No candidate below is cleared as unprecedented. This inventory includes every question identified in the current targeted review, including rejected novelty claims and required controls; it is not an exhaustive map of all literature.

Adding all these questions to the file does **not** mean executing 20 experiment campaigns. Choose a coherent primary contribution, then run only the supporting controls needed for it. Cost and sufficient statistical power determine the useful scope.

## Status definitions

- **Candidate:** a potentially useful empirical contribution; absence from the reviewed sources is not proof of novelty.
- **Extension:** additional evidence for an established question; useful, but insufficient as a foundational claim alone.
- **Control/replication:** known issue that must be measured to make the comparison credible.
- **Separate track/limit:** a question requiring different assumptions or access; do not merge it into the same-prompt primary result.

## A. Candidate explanatory questions

| ID | Precise question | Closest overlap and remaining uncertainty | Experiment and public anchor | Status |
|---|---|---|---|---|
| G01 | Does computational dependency depth explain Jev's relative deficit after semantic recognition, input length, and distractors are controlled? | S01–S04 already discuss reasoning limits, counterfactuals, and external computation. A confound-controlled quantitative boundary against native reasoning-enabled frontiers is a candidate addition; generic “multi-step tasks are harder” is insufficient. | Verified rule graphs with depth 1/3/5, matched length/rules, crossed irrelevant facts; paired Jev/OpenAI/Claude effects. Check transfer on FOLIO and independently annotated reasoning examples. | Candidate; not cleared |
| G02 | Does insufficient evidence produce a different failure pattern from sufficient evidence that requires more computation? | S02 and S10 already cover missing evidence, contradictions, and difficult judgments; S06 separates information sets from reported probabilities. The proposed joint depth-by-evidence interaction and natural-task transfer are not established by this review. | On a fixed graph, remove a decisive premise without replacing it with a misleading fact; independently verify the resulting True/False/Unknown label. Cross with depth and length-matched filler. FOLIO/ANLI are natural anchors, with audited task semantics. | Candidate; not cleared |
| G03 | Can a small set of observable task features predict which model is sufficient on unseen templates and task families, without first buying Jev's confidence? | S02 already studies selective use and transfer failures; S14/S15 already learn or optimize routing; S09 supplies reasoning/task metadata. Routing or a “reasoning_required” flag is not new. A validated explanatory rule that outperforms length/domain proxies is the candidate result. | Freeze features and rule on development; compare with length-only, domain lookup, an existing routing approach when applicable, and all-Jev/all-frontier policies. Test unseen graph templates and leave-one-family-out transfer across funded public panels. | Candidate; not cleared |

The proposed paper should be organized around **G01–G03 jointly**, if the close-prior review confirms a meaningful distinction. A stronger frontier version or another table is insufficient. Failure to transfer is a result that narrows the claim, not a reason to hide a task family.

G02 is an **optional additional factor**, not part of the existing 288-condition base count. Adding evidence-removal conditions increases calls and changes the testing family; price and freeze them before execution.

## B. Important extensions and controls

| ID | Question or evidence gap | What is already covered | Experiment needed here | Classification |
|---|---|---|---|---|
| G04 | At what allowed quality loss and error consequence does a Jev replacement become economically sensible? | S02 already measures operating tradeoffs; S06 studies decision loss; cost-sensitive decision theory is established. | Prespecified noninferiority margin, paired uncertainty, actual billed costs, and class-dependent error-loss sensitivity. Never treat nonsignificance as equivalence. | Extension; no independent novelty claim |
| G05 | Does Jev's apparent advantage survive credible native frontier reasoning? | S01's baselines disable thinking; S03 varies reasoning budgets; S02 and S13 already include strong API comparisons. | Same canonical tasks, native high/recommended effort and adequate headroom; separately funded effort sensitivity. Log every configuration and truncation. | Extension and essential control |
| G06 | Is the result robust to a fair prompt and native output interface? | S02, S06, and S08 already examine forms/interfaces; S01 notes prompt limitations. | Audit exact native wrappers; freeze common zero-shot text; run equally resourced development-only prompt sensitivity. Keep model-specific optimized results separate. | Control |
| G07 | Do changed decisions correspond to changed truth, and unchanged decisions to preserved truth? | S03 has counterfactual pairs; S05 has single-edit attacks; S10 has controlled variants. | Independent oracle labels plus blinded human semantic validation for changed and invariant pairs; measure paired correctness, not merely agreement with each model's clean output. | Extension/control; counterfactual testing itself is established |
| G08 | Are old benchmark scores inflated by exposure, rather than transferable competence? | S01 explicitly discusses exposure uncertainty and perturbation tests. | Preserve public-panel results but add freshly generated sealed graphs and verified answer-changing variations. Compare original/transformed scores; do not claim proof of contamination or its absence. | Control/extension |
| G09 | Can confidence or a cascade conceal confident, shared mistakes under shift? | S02 and S16 directly address confidence, deferral, and shared errors. | Paired error overlap, risk/coverage curves, and frozen threshold transfer, only if needed to interpret a policy. Count every first-stage and escalated call. | Replication; reject as untouched novelty |
| G10 | Are probabilities coherent across coarse/fine labels, negations, and equivalent forms? | S07/S08 directly study coherence; S06 connects interfaces and decision consequences. | Optional matched direct/hierarchical/form comparisons using known semantics. Do not demand numerical frontier confidence in the primary label-only track or compare incompatible probability channels as calibrated equals. | Replication; reject as untouched novelty |
| G11 | Do shared-state batching and question packaging change decisions or only repeat noise? | S05 Appendix B explicitly compares batched and single-question requests; S11 tests layout-sensitive batching. | Prespecified single/bundled/repeated conditions with identical focal evidence/questions and documented packing. Synchronous cost/latency and batch quality reported separately. | Replication/control; not an unexplored batching discovery |
| G12 | Can irrelevant persuasion or polished wrong answers shift correct judgments? | S02 covers answer style; S05 covers request attacks; S10 covers adversarial descriptions. | Gold-verified correctness under matched style/distractor edits; distinguish attacker success, correctness change, and ordinary rerun noise. JudgeBench plus controlled cases. | Extension/control |
| G13 | Does the economic advantage survive realistic reasoning-token tails, retries, cache writes, and remote overhead? | S01/S02 already report fees and timing; invoice/accounting discipline is established. | Item-level usage and aggregate bill reconciliation; conditional token/cost distributions; actual interactive and offline operating points; consistent shared RunPod allocation. | Essential cost control |
| G14 | Does the boundary change with candidate-set size or an absent valid answer? | S07 studies label hierarchies; S09 includes varying candidate counts; S12 explores different answer encodings. | Optional verified synthetic candidate-size experiment. Preserve all 77 options in official Banking77 scores. Test “none valid” only in a separate task where that option has a defined gold meaning. | Extension; no general “candidate sets are unexplored” claim |
| G15 | Are failures caused by reasoning limits or by parsing, truncation, timeout, and service behavior? | S02 evaluates valid verdicts and answer extraction; S06 retains served failures. | One frozen scorer, native structured outputs, generous development-verified time/output limits, explicit operational statuses, full denominators, and shared transient-retry policy. | Essential control |
| G16 | Would model-independent labels change the ranking relative to LLM consensus or ambiguous references? | S02 includes blinded human adjudication; public benchmarks already offer external labels; S05 documents label provenance limits. | Retain supplied benchmark gold; optionally audit disputed cases blindly and report original/adjudicated views separately. Never use a tested frontier as its own evaluator. | Control/extension |

## C. Separate tracks and limits that prevent overclaiming

| ID | Question | Why it is separate | Appropriate treatment | Classification |
|---|---|---|---|---|
| G17 | Is Jev the best deployment choice compared with inexpensive classifiers or deterministic code, rather than only expensive frontiers? | A frontier-only comparison cannot establish optimality over all alternatives. A supervised classifier has different labeled-data access and setup cost from zero-shot APIs. | Optional deployment-alternative track with declared training data, remote setup costs, and inference costs. Use exact code only where the input semantics permit it. Retain the matched direct frontier track. | Separate comparison; required only for an “optimal overall” claim |
| G18 | Does the explanation hold across languages, domains, and model revisions? | S01 already includes multilingual work; one vendor version is not evidence about an architecture class. | Broaden only after the English/core study is stable; preregister new languages/versions and retest the rule without outcome tuning. Date every deployment recommendation. | Generalization extension |
| G19 | Can the experiment prove why the proprietary model behaves this way internally? | Black-box accuracy, confidence, and latency do not identify hidden training, architecture, FLOPs, or internal reasoning. Community replicas differ. | State an observable behavioral mechanism. An architectural claim requires additional controlled access or independently specified model experiments, beyond this hosted-API study. | Identification limit; not resolved by another benchmark |
| G20 | Would semantic parsing, a solver, active queries, or conformal prediction make Jev a novel reasoning system? | Logic-LM, LINC, formal-uncertainty work, neural logic, active testing, and the historical second-pass audit already overlap these components. | Keep the earlier DASC idea superseded. Any hybrid needs its own novelty case, baselines, full cost, and separate comparison; it cannot inherit the raw same-prompt claim. | Excluded historical method track |

## Prior-work register and inspection limits

These links support the overlap assessment. “Inspected” means the relevant available sections/card/README were read, not successful reproduction or a complete line-by-line code audit.

| Source | Primary reference | Material inspected for this inventory |
|---|---|---|
| S01 | [Evaluating and Benchmarking the System One Model Jev](https://arxiv.org/html/2609.37647v1) | Baseline protocol, reasoning/contamination discussion, prompt limitations, fees and throughput |
| S02 | [JEV-as-a-Judge](https://arxiv.org/html/2609.26550v1) | Contribution, public panels, interfaces, style controls, confidence/deferral, threshold-transfer discussion |
| S03 | [jev-frontier-100](https://github.com/softpudding/jev-frontier-100) | README task construction, oracle/counterfactual design, reasoning budgets, exploratory-release limits |
| S04 | [Code Owns the Simulation, Jev Owns the Evaluation](https://arxiv.org/abs/2610.01834) | Prior targeted review of task and external-computation framing |
| S05 | [JevAdvBench](https://arxiv.org/html/2609.31142v1) | Attack design, label provenance, repeat-noise controls, Appendix B batching comparison |
| S06 | [Probability Contracts](https://arxiv.org/html/2609.37470v1) | Related-work/contribution framing, decision-loss discussion, limitations, post-hoc policy appendix |
| S07 | [Do System One Decisions Add Up?](https://arxiv.org/html/2609.33971v1) | Direct/hierarchical comparison, practical implications, limitations and conclusion |
| S08 | [Beyond Calibration](https://arxiv.org/abs/2609.33209) | Abstract of logically linked probability checks; full methods not audited here and no reproduction |
| S09 | [DecisionBench canonical dataset](https://huggingface.co/datasets/Hanno-Labs/decision-bench) | Dataset schema and author release record: task/domain metadata, reasoning flags, varying candidates and source provenance |
| S10 | [Jev security prioritization](https://github.com/san3ncrypt3d/jev-security-prioritization) | README experiment families, frontier comparison, reference-rubric and synthetic-data limitations |
| S11 | [jevotron batching benchmark](https://cmungall.github.io/jevotron/analysis/batching/) | Author report of presentation-sensitive batching and checked-in response provenance |
| S12 | [JevNext](https://github.com/Bring-AI/JevNext/blob/main/README.md) | README alternative numeric/choice encodings and dependency-round caveats |
| S13 | [Open-Jev](https://github.com/Zefan-Cai/Open-Jev) | Current README independent controls, public holdout, community-model identity and limitations |
| S14 | [RouteLLM](https://arxiv.org/abs/2406.18665) | Paper record/abstract: learned routing already established; complete algorithm adaptation remains a follow-up if a rule is developed |
| S15 | [FrugalGPT](https://arxiv.org/abs/2305.05176) | Paper record/abstract: cost-aware model selection/cascading already established |
| S16 | [Cheaper, Faster, and Wrong in the Same Places](https://arxiv.org/abs/2609.29769) | Earlier targeted review of shared rubric errors and fallback limits |

S09's author release describes 43 tasks across 28 domains. Therefore “a new cross-domain Jev benchmark” is also not a safe standalone novelty claim. The release's task metadata can be background or a separately priced external test, subject to license and gold-provenance checks. It is not automatically added to the four-panel bill.

The newer overlap strengthens the stop rule: no first-ever claims for cheap judging, probability coherence, counterfactual evaluation, task metadata, or batching stability.

## Recommended coherent paper

**Primary question:** can model-independent evidence and task structure explain and predict when direct Jev is sufficient relative to reasoning-enabled frontier models?

Use G01/G03 as the main explanatory design, add G02 only when its interaction is both scientifically motivated and adequately powered, and apply G04–G08/G13–G16 as the necessary validity controls. Use G09–G12/G14 only where they address a specific alternative explanation, not as 20 separate novel contributions.

An abstract-worthy result requires a quantitative pattern beyond “Jev is cheaper and weak at reasoning,” replication on independent inputs, credible frontier settings, and held-out predictive improvement over simple proxies and relevant prior routing. If those conditions fail, the honest deliverable is a replication, extension, or narrower negative result.

The current plan **does not certify an untouched gap or a foundational contribution**. Before paid execution, the novelty decision must explain exactly how the proposed explanatory result differs from S01–S16 and reasonable adaptations of them.
