# Research plan: when to use Jev and when to use a frontier LLM

**Consolidated entry point:** [PLAN.md](PLAN.md) contains the ordered study design, milestones, datasets, comparison rules, and cost scenarios. This file provides the extended rationale and supporting detail.

Prepared 4 October 2026. **Plan only; no experiments or results; $0 spent on model APIs or RunPod.** Claude will implement and execute later using [CLAUDE_HANDOFF.md](CLAUDE_HANDOFF.md). **The user has clarified that the budget is flexible, with no fixed numeric ceiling.** Costs below are estimates and scaling decisions, not spending caps. All future experiment execution belongs on RunPod.

This revision implements the user's clarified objective: determine **where official Jev beats frontier OpenAI and Claude models, where it offers comparable accuracy at lower cost, and where a frontier model earns its additional cost**. It supersedes the earlier semantic-parser/solver proposal. Building a new solver, training an open model, or comparing only small open LLMs is no longer the core experiment.

Working title: **“When Can Decision Models Replace Frontier LLMs? Controlled Evidence on Accuracy and Cost.”** The foundational ambition is an explanatory, transferable result about decision tasks. A benchmark score table alone will not establish that result. Novelty remains unconfirmed; publication or benchmark wins cannot be promised.

**Gap review update:** [GAP_INVENTORY.md](research/GAP_INVENTORY.md) records 20 identified questions with prior overlap, status, and an experiment. The strongest candidates concern controlled dependency depth, evidence sufficiency, and held-out prediction of the replacement boundary. Many other questions are already covered and are listed as controls or extensions. No gap is certified as untouched.

## 1. The decision the paper should support

For each tested task family and prespecified difficulty stratum, report four possible conclusions, separately against OpenAI and Claude:

| Finding | Evidence required | Practical implication |
|---|---|---|
| Jev has higher accuracy | Adjusted paired uncertainty supports a positive accuracy difference | Prefer Jev for the evaluated task if measured operational constraints also fit |
| Jev has comparable accuracy at lower cost | A prespecified noninferiority test passes and billed cost is lower | Prefer Jev when the permitted accuracy loss and error consequences fit |
| Frontier model is more accurate | Adjusted paired evidence shows a meaningful Jev deficit | Pay for that frontier model when the accuracy gain justifies its cost |
| Inconclusive or conflicting | Insufficient precision, unstable prompts, conflicting providers, or transfer failure | Make no replacement recommendation; collect evidence or restrict the claim |

A nonsignificant difference does **not** demonstrate comparable quality. “Needs a frontier LLM” means the tested frontier configuration performs better under the evaluated conditions. It does not prove that every possible Jev prompt, future version, or decision-model architecture must fail.

The main comparison is **direct official Jev versus direct frontier APIs**. Each receives the same task information, instructions, candidates, examples, and task prompt. No solver, retrieved answer, generated intermediate solution, or extra Jev queries are included in this primary track.

## 2. What the literature already covers

The original [Jev benchmark paper](https://arxiv.org/html/2609.37647v1) already investigates a broad capability profile. Its thinking-disabled open-model protocol leaves room for a stronger API comparison, but filling that omission alone is an empirical extension.

[JEV-as-a-Judge](https://arxiv.org/html/2609.26550v1) already studies frontier judge comparisons, task-dependent strengths and weaknesses, fees, latency, and escalation. We cannot claim to discover cheap Jev judging, confidence routing, or the general idea of choosing Jev versus an LLM.

[jev-frontier-100](https://github.com/softpudding/jev-frontier-100) already includes counterfactual task pairs and comparisons across reasoning budgets. [Code Owns the Simulation, Jev Owns the Evaluation](https://arxiv.org/abs/2610.01834) already explores computation supplied outside the model. Neither counterfactual examples nor exposing intermediate consequences is new by itself.

The candidate contribution is therefore narrower: **an independently validated, cross-task explanation of the replacement boundary, using controlled task changes that separate semantic recognition, dependency depth, and irrelevant context, with genuinely reasoning-enabled frontier baselines and quality-adjusted cost comparisons**. This is an inference about a possible gap, not proof of an untouched research area.

Read [the empirical novelty audit](research/EMPIRICAL_NOVELTY_AUDIT.md) before spending. The [literature inventory](research/LITERATURE_AUDIT.md) and [second-pass audit](research/NOVELTY_SECOND_PASS.md) preserve earlier research and rejected ideas; their solver-method recommendations are superseded. The review was targeted, not an exhaustive reading of every publication, repository, or Medium article.

The additional review also found direct work on [probability coherence](https://arxiv.org/abs/2609.33971), [interface-dependent decision loss](https://arxiv.org/abs/2609.37470), and [batch versus single-question stability](https://arxiv.org/html/2609.31142v1). [DecisionBench](https://huggingface.co/datasets/Hanno-Labs/decision-bench) already supplies a broad typed-decision dataset and task metadata. These findings further narrow the novelty claim; they are mapped in the gap inventory.

**Go/no-go criterion:** before the pilot, write a claim-by-claim comparison with the closest studies. A normal/high reasoning setting, two extra benchmarks, or a smaller API bill is insufficient by itself. Proceed only if a controlled, falsifiable explanation and a held-out validation design plausibly add material knowledge. If all proposed insights are already established, stop and report the overlap before spending.

## 3. Models and access

| Required system | Proposed version on research date | Role |
|---|---|---|
| Official TypeSafe Jev | `jev-1.13.0` | Decision-model system under study |
| OpenAI frontier | `gpt-6-astra` | Strong generative reasoning comparator |
| Claude frontier | `claude-fable-5-1` | Strong comparator from another provider |

These are proposed public API configurations, not a statement that every restricted-access model is covered. Recheck availability and vendor recommendations at execution. Freeze versions and effort settings **before held-out calls**, log the resolved version on every response, and document any service-side version change. If a named version is unavailable, stop that comparison until an explicit replacement protocol is frozen; do not silently substitute a cheaper model.

Use a vendor-supported high/recommended reasoning configuration with sufficient output headroom. Claude's documentation currently lists adaptive thinking and high default effort for Fable 5.1. OpenAI Astra supports several effort settings; freeze `high` for the primary proposal after checking the current guide. “High” across providers does not mean equal compute. A separately funded maximum-effort check may test sensitivity, but the main claim must name the actual effort settings.

Do not disable frontier reasoning, score only its first answer-token probability, force an inadequately small output limit, or require a long visible rationale to inflate its bill. Ask for the same final decision and allow the API's native internal reasoning. Account for all billed reasoning tokens even when the final output is one label.

Official sources: [Jev models and input billing](https://docs.typesafe.ai/models), [OpenAI Astra model](https://developers.openai.com/api/docs/models/gpt-6-astra), and [Claude models](https://platform.claude.com/docs/en/models/overview).

Official Jev's hosted weights were not established as publicly downloadable in this review. Independent [JEV-9B](https://huggingface.co/autotrust/JEV-9B) and [Open-Jev](https://github.com/Zefan-Cai/Open-Jev) projects are community implementations, not interchangeable with official Jev. A [community demo](https://huggingface.co/spaces/autotrust/jev-9b-decision-demo) may permit manual free testing, subject to availability. No universal free quota for the official API was verified. Free weights still need hardware. No open-weight replication or GPU model loading is required for this initial plan.

## 4. Public datasets: fixed roles and honest scope

| Task family | Public source and final split | Full released panel | Question |
|---|---|---:|---|
| Fine-grained intent decisions | [Banking77 author repository](https://github.com/PolyAI-LDN/task-specific-datasets), test | 3,080 | Can Jev select among 77 closely related intents economically? |
| Adversarial inference | [ANLI](https://huggingface.co/datasets/facebook/anli), `test_r3` | 1,200 | Does the advantage survive adversarial natural-language inference? |
| Logical reasoning | [FOLIO](https://github.com/Yale-LILY/FOLIO), public validation | 204 | Where does evidence interpretation or logical deduction require frontier reasoning? |
| Correctness judging | [JudgeBench](https://huggingface.co/datasets/ScalerLab/JudgeBench), `gpt` and `claude` | 350 + 270 = 620 | Can Jev choose the objectively better answer on difficult pairs? |

These panels contain **5,104 rows before auditing shared source questions**. They are the proposed broad-study menu; final scope follows the novelty review, pilot usage, and statistical power projection. JudgeBench's two response-generator splits are evaluated separately; combine using the published row counts only as a supplementary summary. Cluster uncertainty by original source question when it appears multiple times.

**First full-panel target:** FOLIO's 204 public validation items. Price the complete comparison using pilot-measured tokens and credible frontier headroom before launching it. If the forecast is poor value, revise the scope before test calls; do not shorten reasoning or cherry-pick easier FOLIO items. A completed FOLIO-only paper can support a logical-reasoning conclusion, not a general recommendation across all four families.

For a broader study, fund and preregister additional complete panels separately. A fixed sample from a public dataset is useful but must be called a **sampled public panel** with its exact IDs. It cannot be called a full benchmark, leaderboard reproduction, or SOTA score. Scoring counts, failed calls, unused rows, and official-protocol differences must be public.

Primary scoring uses supplied labels and the published task semantics. FOLIO's `Unknown` is a logical answer, not an API failure or abstention. Banking77 retains all 77 classes. ANLI exposes only premise, hypothesis, and allowed choices: exclude its label and explanation/reason fields. JudgeBench exposes question and candidate responses, never the gold ranking or generator identity. Dataset licenses and upstream redistribution rights must be checked before publishing raw text.

See [PUBLIC_BENCHMARK_PROTOCOL.md](research/PUBLIC_BENCHMARK_PROTOCOL.md) for split protection, task construction, and result requirements.

## 5. The controlled experiment that could explain the boundary

Do not infer a causal mechanism merely because Jev loses more often on a harder dataset. Different domains also differ in text length, familiarity, labels, and candidate count.

Build a supplementary **controlled dependency panel** from formal rule graphs, independently scored by an exact reference implementation. A development-only pilot checks whether the manipulations work. A later funded panel uses new graph/template seeds sealed before calls.

Vary dependency depth at 1, 3, and 5 steps while keeping the inference target, answer type, entity vocabulary, label balance, rule count, and total text length matched as closely as the construction permits. Fill shorter chains with unused rules. Cross this with 0 versus 8 irrelevant facts; balance the resulting token-length distributions within each depth cell. Record remaining length differences and include a length-matched sensitivity analysis.

Add paired controls:

1. **Decision-changing control:** change one decisive fact or rule so the verified gold answer changes. Measure whether each model changes its decision correctly.
2. **Decision-preserving control:** rename entities or reorder independent premises while retaining the verified gold answer. Measure correctness and invariance.
3. **Computation-disclosure check, secondary:** supply verified intermediate consequences, compared with a length-matched irrelevant-information condition. Give exactly the same augmented task to every model. This changes the information supplied and belongs in a separate condition. Charge any consequence computation and avoid presenting it as an intrinsic Jev improvement.

**Optional evidence-sufficiency interaction (G02):** remove a decisive premise and verify the resulting logical label, contrasting missing information with a complete but deeper inference chain. Existing work already tests missing evidence in other settings. The candidate addition is a controlled joint interaction and held-out transfer, not the observation that missing facts cause errors. These added conditions are outside the 288 base-condition count and must be priced and preregistered separately.

A possible funded target is 48 independent held-out base graphs, each with six depth/context conditions (288 decisions). Before pricing, freeze how many of these also receive the paired controls. This count is a design proposal, not a commitment that 48 graphs provide sufficient power. Base graphs, not their variants, are the independent units.

Labels must come from deterministic formal semantics, not whichever model is stronger. Validate the reference scorer with an independently implemented cross-check; have two blinded human readers review natural-language fidelity on a prespecified sample before calls. Generated wording must be templated or human-authored first; paid LLM generation is an extra experiment and must be priced. Publish reviewer time and disagreements. Limit the claim to the formal fragment actually supported.

The study should test a falsifiable pattern, such as: **after controlling text length and semantic difficulty, increasing dependency depth disproportionately reduces Jev accuracy, while irrelevant length alone explains less of the change; this pattern predicts relative performance on unseen graph templates and independently annotated natural examples.** The result could be absent or reversed. Do not equate API behavior with proof of the proprietary architecture or internal reasoning process.

Model-independent annotations for natural examples must be made before viewing model outcomes. Formal dependency depth is available only where a validated dependency graph exists. Do not invent exact “reasoning depth” from word count, a model's explanation, or an unvalidated heuristic for all ANLI/FOLIO/JudgeBench cases.

## 6. Fair comparison under the same prompt and environment

Use one canonical task object and one rendered text. Each item's hash covers instructions, evidence, question, candidates, candidate order, and examples. Native APIs require different request schemas; the semantic content stays identical and both the canonical text and complete wrappers are released.

Primary tasks are zero-shot. Use neutral wording, equal answer semantics, and a shared option-order schedule. Do not give Jev atomic hints while giving Claude/OpenAI a vague request. Do not provide a solution to one model. Keep tool use, retrieval, memory, and cross-item conversation off for all.

Run all API clients from the same RunPod instance, region, container, SDK pins, clock, and experimental window. Interleave requests in randomized provider order for paired synchronous measurements. Disable streaming for total-response latency and hold client concurrency at one in the latency track. Retry at most one transient transport failure under a shared policy; never retry because an answer is wrong.

Provider servers, GPUs, routing, hidden instructions, and tokenizers cannot be made identical. Report those limits explicitly: this is an end-to-end API system comparison, not a same-hardware model experiment. Identical text does not imply identical token counts. Enforce context feasibility before calls, never truncate only one model.

Use separate tracks:

- **Primary accuracy:** identical canonical task, native reasoning-enabled configurations, one decision per item.
- **Offline cost:** same accuracy configuration through verified batch support where available; document Jev's actual online billing if it lacks batch discounts.
- **Interactive latency:** synchronous versus synchronous, matched RunPod client conditions, actual standard prices.
- **Sensitivity, only if funded:** equal development effort for prompt variants, option reversal, effort changes, or small repeat sets. Freeze before final evaluation and report every variant.

Batch queue time is not interactive latency. Do not claim a combined cost/latency operating point using batch prices and unrelated synchronous times. An unresolved output limit or wrapper bias blocks the superiority claim.

See [FAIR_COMPARISON_PROTOCOL.md](research/FAIR_COMPARISON_PROTOCOL.md) for the review checklist and logging fields.

## 7. Statistics and a deployable selection rule

Primary endpoint: per-panel accuracy on all registered rows. Secondary endpoints: Banking77 macro-F1, failure rate, paired changes under interventions, billed dollars per 1,000 decisions, total experiment expense, and interactive p50/p95 latency where the sample supports it.

Define paired accuracy difference `delta = accuracy(Jev) - accuracy(frontier)`. Before seeing outcomes, set a meaningful tolerated loss; the draft uses **2 percentage points**, which must be justified for the intended deployment. Do not loosen the margin after a failed test. Report sensitivity to other margins as exploratory.

For each completed family and frontier:

- Superiority requires the adjusted lower confidence bound for delta to exceed zero.
- Comparable quality requires the adjusted one-sided lower bound to exceed -0.02.
- A materially better frontier requires the adjusted upper bound to be below -0.02.
- All other comparisons remain inconclusive or require a narrower statement.

For a final four-family study, prespecify eight family/provider comparisons and adjust the family of quality claims. Use Bonferroni simultaneous intervals as the simple conservative default, or a fully specified alternative frozen before outcomes. Depth interactions and secondary controls have a separate prespecified testing family; exploratory slices cannot create the abstract's main win.

Compute paired uncertainty at the independent source-story/question level. Use a paired discordance-based interval for independent rows and a prespecified cluster procedure where source questions or graph variants repeat. If the cluster count is too small for the chosen approximation, report uncertainty and avoid a certified boundary. Repeated calls and paired variants are not independent additional examples. Evaluate bootstrap coverage on simulation when implementing the statistics on RunPod.

The 24-item pilot is for feasibility and effect direction. It cannot certify a 2-point noninferiority margin or establish general frontier superiority. Power depends on paired discordances, not just total accuracy; estimate it from development and freeze a feasible final sample size before spending on held-out work.

For an optional predictive selection rule, use a simple prespecified model with a small feature set available **before** requesting a paid answer. Candidate features include input length, candidate count, explicit rule structure, and validated dependency depth where available. Compare with length-only and task-family lookup baselines. A rule that merely identifies which benchmark an item came from is insufficient evidence of a general boundary.

Freeze feature definitions and hyperparameters on development data. Validate on unseen templates and, only when multiple families are funded, leave-one-family-out transfer with no held-out outcome tuning. Report failures and recalibration requirements. Compare with relevant existing routing methods when proposing a routing contribution: generic learned routing is already studied in [RouteLLM](https://arxiv.org/abs/2406.18665) and cost-aware selection in [FrugalGPT](https://arxiv.org/abs/2305.05176). A Jev-confidence cascade is optional prior-work reproduction, not the claimed new principle; include the first Jev call in cascade costs.

Use a task-aware economic decision, rather than accuracy alone:

`expected loss(model) = cost per decision + error consequence * error probability`.

When frontier accuracy exceeds Jev by `gain > 0` and costs more by `extra_cost`, the illustrative break-even error consequence is `extra_cost / gain`. Plot sensitivity to that consequence and latency requirements. The formula is an established decision rule, not a new theorem. Average error costs can hide unequal harms; if class-dependent errors matter, use a prespecified loss matrix.

## 8. Cost comparison: billable quantities, not headline prices

Pricing snapshot, USD per million tokens:

| System | Standard input | Standard billed output | Batch input/output where documented |
|---|---:|---:|---|
| Official Jev | 0.042 | 0 | No extra batch discount assumed |
| OpenAI Astra | 10 | 50 | 5 / 25, subject to model/account support |
| Claude Fable 5.1 | 10 | 50 | 5 / 25 |

Sources: [Jev model pricing](https://docs.typesafe.ai/models), [OpenAI pricing and model details](https://developers.openai.com/api/docs/models/gpt-6-astra), [OpenAI Batch](https://developers.openai.com/api/docs/guides/batch), and [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing). Recheck rates, tiers, cache rules, taxes, and account availability before execution. Prices do not establish achieved accuracy, latency, or a real cost saving at matched quality.

Illustration for **one** decision with 1,500 billed input tokens and 2,000 frontier billed output tokens, including internal reasoning:

| Configuration | Illustrative marginal API cost |
|---|---:|
| Jev, 1,500 actual billed input tokens | $0.000063 |
| One frontier, standard | $0.115 |
| One frontier, batch | $0.0575 |

This produces a nominal batch/frontier-to-Jev ratio of about 913 under the stated token assumptions. It is **not an experimental result**, assumes equal input token counts only for arithmetic, and omits quality differences and infrastructure. Actual provider tokenization, output, and billed request shapes will differ.

For every item record uncached input, cache writes, cache reads, visible output, billed reasoning, actual tier, batch status, fees, retries, and final billed amount. Never double-count reasoning already included in output totals. Report actual invoice-based expense and an uncached standardized-price view separately. Account credits reduce out-of-pocket expense but do not make list-price inference intrinsically free.

Report **per-system marginal API cost** and **total study cost** separately. Allocate RunPod/storage/shared preprocessing consistently across systems; do not charge the entire common coordinator to Jev alone. Include Pod startup, idle time, downloads, retries, and discarded paid development calls in the study ledger. Optional training or human labor is separately disclosed. Cost per correct answer is descriptive and must not replace a matched-quality analysis.

## 9. Flexible budget with staged cost forecasts

There is **no fixed pilot or total spending ceiling**. The earlier $20 ceiling and provider subcaps are superseded by the user's latest instruction. This remains a plan-only deliverable; it does not start an experiment.

Use a small pilot to learn real token use, then price each useful expansion before launching it. Expand for scientific precision and a defensible contribution, not to search for favorable examples. Flexible spending does not justify repeated paid prompt search, unnecessary model downloads, or idle Pods.

Track official Jev input charges, each frontier's billed input/output/reasoning, remote coordinator time, storage, retries, controlled variants, and statistical validation separately. Keep both expected expense and a conservative upper projection for every stage; neither is an invented hard cap.

Use **24 fixed development examples**, six per family: Banking77 train, ANLI train_r3, FOLIO train with source stories separated from final evaluation, and six independently authored judge-practice cases. Do not tune on JudgeBench's final 620 pairs. Select by a sealed seed and stratification before seeing answers. Two telemetry cases are included in the 24 and are not repurchased.

For the first telemetry calls, estimate the full configured maximum charge alongside the expected charge. Start with one matched item and reconcile actual usage before queuing more. Do not disable reasoning to force a cheap bill. Count native SDK automatic retries and queued requests in outstanding commitments.

Illustrative **two-frontier batch API cost only**, using 1,500 input tokens and one call per model per item:

| Paired decisions | Billed output per frontier call | API cost for both frontier models |
|---:|---:|---:|
| 24 | 2,000 | $2.76 |
| 24 | 8,000 | $9.96 |
| 24 | 16,000 | $19.56 |
| 204 | 1,000 | $13.26 |
| 204 | 2,000 | $23.46 |
| 5,104 | 2,000 | $586.96 |
| 5,104 | 8,000 | $2,118.16 |

These are planning scenarios, not quotes or spending commitments. Jev, RunPod, storage, retries, controls, prompt sensitivity, and human work are extra. Banking77's complete option list and long JudgeBench pairs may exceed the illustrative input length. Broad coverage can therefore cost substantially more than the pilot; price the actual scope after telemetry.

A full FOLIO run is a relatively small next stage; the 1,000-output row is an observation scenario, not an instruction to cap reasoning at 1,000. A pilot plus full FOLIO costs more than the FOLIO row alone. Add JudgeBench, controlled variants, or the larger panels only when they improve the proposed paper's evidence.

Use a shared ledger for spent money, queued/in-flight commitments, expected remaining expense, and conservative stage totals. Reconcile after small request groups; investigate unexplained cost jumps or billing gaps before scaling. Unknown pricing or unobservable billed usage stops new paid calls until accounting is resolved. Stop RunPod while API batches wait; resume briefly to collect and score. No model weights need downloading. Every execution, scorer, statistical script, and model call runs remotely.

See [COST_COMPARISON.md](research/COST_COMPARISON.md) for cumulative stage scenarios, [LOW_COST_EXECUTION.md](research/LOW_COST_EXECUTION.md) for economical execution, [pilot_budget.csv](research/pilot_budget.csv) for estimate categories, and [budget_calculator.py](research/budget_calculator.py) for later remote calculation. The calculator has not been run as an experiment.

## 10. Execution stages and what would merit a paper

1. **Free desk review:** finish the empirical novelty comparison, freeze candidate hypotheses and task definitions, verify licenses/access, and make the RunPod package reviewable. No credentials or paid calls.
2. **Remote feasibility pilot:** execute at most the funded development pool, validate adapters, record tokens/failures, and inspect prespecified controlled development examples only if they fit. Report directional findings honestly.
3. **Cost and evidence checkpoint:** calculate the complete stage cost and statistical precision for the proposed claim. Scale to the least expensive adequate design; restrict the claim when coverage remains narrow. Flexible budget removes an arbitrary ceiling, not the need for worthwhile evidence.
4. **Locked public evaluation:** preregister IDs, prompt hashes, models, effort, output limits, scorer, statistical families, and stopping rules. Complete every funded registered panel; release all losses and failures.
5. **Controlled explanation and transfer:** use independently verified labels, sealed graph seeds, blinded annotations, and frozen prediction rules. Check whether the explanation survives unseen templates and domains. A failed generalization narrows the conclusion.
6. **Paper and release:** write claims from results, not desired wins. Publish reproducibility artifacts, cost ledger without secrets, prediction files where permitted, prompts, scorer, and a one-command remote reproduction.

The [AgentFoundry paper supplied as a quality reference](https://github.com/arghya05/agent-foundry/blob/main/research-paper/AgentFoundry_Paper.pdf) motivates complete evidence, explicit limitations, strong comparisons, and reproducibility. It does not mean this study needs to manufacture a theorem. A strong empirical paper can contribute a new explanation and benchmark; top-conference significance still needs evidence.

Required main exhibits are: public-panel accuracy with paired intervals; accuracy/cost operating points; controlled depth/context effects; counterfactual and invariance results; held-out selection-rule performance if supported; and failure cases where Jev should not be used. Provide separate tables for standard interactive and discounted offline operation.

**Stop or reframe** if the only result repeats existing Jev strengths and weaknesses, the explanation reduces to text length or benchmark identity, credible frontier reasoning cannot be funded, the apparent win depends on one favorable prompt, or uncertainty is too large to justify replacement. A negative or narrower reproducible result is preferable to an unsupported “foundational” claim.

## 11. Files for Claude

- [CLAUDE_HANDOFF.md](CLAUDE_HANDOFF.md): ordered implementation instructions.
- [research/protocol_draft.json](research/protocol_draft.json): machine-readable draft, with paid execution disabled.
- [research/PUBLIC_BENCHMARK_PROTOCOL.md](research/PUBLIC_BENCHMARK_PROTOCOL.md): datasets and evidence.
- [research/FAIR_COMPARISON_PROTOCOL.md](research/FAIR_COMPARISON_PROTOCOL.md): matched conditions and accounting.
- [research/EMPIRICAL_NOVELTY_AUDIT.md](research/EMPIRICAL_NOVELTY_AUDIT.md): closest work and novelty gate.
- [research/GAP_INVENTORY.md](research/GAP_INVENTORY.md): all 20 questions identified in this review, with covered versus candidate status.
- [research/LOW_COST_EXECUTION.md](research/LOW_COST_EXECUTION.md): remote-only budget controls.
- [research/COST_COMPARISON.md](research/COST_COMPARISON.md): model prices, cumulative scenarios, and quality-adjusted cost reporting.
- [research/verification.json](research/verification.json): planning-file checks only.

No result in this plan establishes an accuracy win, a general deployment boundary, a latency advantage, or a novel foundational contribution. Those are outcomes to test.
