# Claude handoff: implement the Jev/frontier boundary study

Read [PLAN.md](PLAN.md) first, then [RESEARCH_PLAN.md](RESEARCH_PLAN.md) for extended rationale. This handoff supersedes the previous DASC solver instructions. The requested deliverable from Codex was **a plan only**. Nothing has been executed; no benchmark results exist; experiment charges are $0.

## Objective and constraints

Determine where **official Jev** has higher accuracy than strong OpenAI and Claude APIs, where quality is comparable but cheaper, where the frontiers perform better, and where evidence is inconclusive. Keep the same canonical task prompt, evidence, candidates, examples, and evaluation cases across models. Include an actual cost comparison.

All execution goes on **RunPod**, including API clients, scorers, statistics, and any reference graph scorer. Do not run experimental workloads on the user's laptop. Local document/package preparation is allowed.

**Latest budget instruction: flexible budget, no hard numeric limits.** The earlier $20 ceiling and provider subcaps are withdrawn. Do not require the user to choose an exact dollar ceiling. Paid execution is disabled in [the protocol](research/protocol_draft.json) because this deliverable is plan only; a later execution request and the empirical novelty gate govern starting work. Use measured usage, staged forecasts, and scientific value to scale; do not treat flexibility as a reason for unnecessary calls.

Official Jev is the main decision model; community checkpoints are not substitutes. No model training, self-hosting, open-weight baseline, solver-assisted decision system, or prompt-search campaign is required in the primary comparison.

## Stage 0: prepare without spending

1. Read the empirical novelty audit, [the 20-question gap inventory](research/GAP_INVENTORY.md), fairness protocol, public-benchmark protocol, and cost policy. Covered gaps are controls or replications, not novel contributions.
2. Recheck the closest prior papers against the exact intended empirical contribution, including the added Probability Contracts/coherence papers, JevAdvBench batching controls, DecisionBench, domain-specific repositories, and relevant routing methods. Write `research/EMPIRICAL_NOVELTY_DECISION.md` stating what is already established, what is being tested, and what new evidence would matter. Select a coherent G01/G03 contribution, with G02 optional; do not execute all 20 questions as separate campaigns. If the candidate merely repeats existing findings, stop before provisioning.
3. Verify official API model availability, current reasoning recommendations, pricing, batch support, and account access without sending paid inference. Proposed models are `jev-1.13.0`, `gpt-6-astra`, and `claude-fable-5-1`. Resolve versions; never silently downgrade.
4. Prepare a small remote package with a pinned environment and separate modules for dataset loading, canonical tasks, provider adapters, billing ledger, gold-blind predictions, scoring, and analysis.
5. Pin author dataset revisions, split IDs, licenses, and row counts. Exclude labels/explanations/proofs from inference objects. Identify shared source-story/question clusters before sampling.
6. Create a fixed 24-case development pool: six Banking77 train, six ANLI train_r3, six FOLIO train from disjoint stories, and six independently authored correctness-judging practice cases. Public final rows cannot be development data. Select the seed and IDs before observing model outcomes.
7. Render a single canonical text for each case. Publish task hashes and native request wrappers. Fix neutral zero-shot wording, answer semantics, and shared candidate order.
8. Implement expenditure reservations, explicit retry limits, and exact response caching before enabling inference. Credentials belong only in the user's remote secret environment; never in manifests, logs, or repository files.

Required preparation artifacts: `datasets_manifest.json`, `models_manifest.json`, `prompt_manifest.json`, `development_ids.json`, `rate_card.json`, `budget_ledger.json`, and a container/environment lock. These are files Claude must create later, not artifacts already supplied.

Tests should target material risks: gold-field exclusion, correct label mapping, identical canonical task hashes, no cache collision across effort/model settings, no double-counted reasoning tokens or queued commitments, retries, and cluster leakage. Do not reproduce the implementation line by line in tests.

## Stage 1: remote feasibility, after the novelty gate and execution request

Use a cheap suitable RunPod coordinator, without loading model weights. A short initial session and an inexpensive available instance are planning preferences, not hard duration or dollar caps. Obtain a live quote and count startup, idle, storage, and later collection sessions. Stop the Pod while API batches wait.

Validate adapters and scorers using remote synthetic fixtures before paid model calls. Then use the first two development items for telemetry, reusing their responses in the pilot.

For **every** paid request, record expected and maximum configured billable tokens/fees and account for queued commitments. The first request cannot rely on an average output estimate from nonexistent telemetry. Reconcile actual usage in small groups and revise the next-stage forecast if it changes materially; do not disable thinking or enforce a misleadingly short answer budget.

Frontier primary settings use native supported reasoning, with proposed high/recommended effort, final-label output, and sufficient output headroom. SDK hidden retries must be disabled or bounded and included in the reservation. One transient retry maximum; no retry for model disagreement or incorrect answers.

Prefer batch for offline accuracy/cost only when the exact model and configuration are supported. Stop RunPod while waiting for batches. Reserve queued requests, persist batch IDs, and resume briefly for collection. Batch response time cannot substantiate a synchronous latency claim.

Start with the fixed 24-case development pool. Optional controlled development transformations belong to a separately priced fixed list. Expand development only for a prespecified feasibility or precision question, not to search for Jev wins.

Produce `pilot_report.md` with token distributions, failures, actual charges, paired directional accuracy, prompt-interface concerns, and a cost projection for each proposed final panel. State explicitly that the pilot does not establish noninferiority, SOTA, or a general replacement boundary.

## Stage 2: freeze a scientifically useful study and its cost forecast

Use measured billable usage to price the **entire** proposed stage: all required systems, controls, retries, shared infrastructure, statistical checks, and any sensitivity work. Present a compact minimum-evidence design and a stronger expanded design, with expected and conservative expense, precision, and the claim each supports.

FOLIO's 204-item validation panel is the first full-panel candidate. Compare its projected value with adding JudgeBench or controlled interventions, and freeze the chosen scope before test outcomes. Never select the easiest test rows or cut reasoning to make the result look favorable.

Additional panels are Banking77 test (3,080), ANLI test_r3 (1,200), and JudgeBench gpt/claude (350/270). Price each expansion and include it when it adds needed coverage or precision. A partial panel must retain its sampled-panel name and exact IDs. A FOLIO-only result supports a logical-reasoning claim only.

Before test calls freeze:

- All final IDs, revisions, cluster keys, canonical prompt hashes, model versions, native wrappers, effort, output limits, tools-off policy, and option order.
- Official task semantics and scorer; operational failures remain in the denominator.
- Primary comparisons, the justified noninferiority margin (draft 2 percentage points), adjusted paired intervals, independent sampling units, and stopping rules.
- Controlled-panel graph/template seeds, human validation protocol, and any predictive rule/features. Fit or tune only on permitted development data.
- Flexible-budget stage forecast, rate snapshot, queued commitments, and policies for cost anomalies, model-version drift, or incomplete matched results.

Commit the freeze manifest to a public timestamped repository or preregistration service when the user authorizes publication. Preparing it locally is sufficient before that step; do not silently publish personal data or secrets.

## Stage 3: locked evaluation and analysis

Run every funded registered row against every required model. The inferencer has no gold-label access. The scorer joins labels only after outputs are saved. Preserve raw response metadata and a sanitized release view.

For synchronous latency, use the same RunPod client, region, software, clock, and window, concurrency one, streaming off, and randomized/interleaved provider order. Log end-to-end total response time and failed attempts. Provider GPUs/hidden infrastructure cannot be controlled and must be disclosed.

Report Jev superiority, noninferiority plus cheaper cost, meaningful frontier advantage, or inconclusive evidence separately for each provider and panel. Do not force the four-way deployment labels when uncertainty is large.

A complete four-family study has eight primary family/provider comparisons; use the frozen simultaneous interval procedure. Source stories/questions and graph seeds are clusters. Reruns, response-order reversals, and graph variants are not new independent cases.

Keep offline batch expense separate from synchronous latency operating points. Record all billed input/output/reasoning/cache categories without double counting, failed-call charges, retries, shared Pod/storage costs, and credits versus list-price economic cost.

For the controlled panel, test prespecified depth/context interactions and decision-changing versus decision-preserving behavior. For a selection rule, evaluate unseen templates and funded held-out families against length-only and task-family baselines. Do not interpret a benchmark-identity classifier as a general mechanism.

## Stage 4: paper and release, only to the extent evidence supports

Create public-panel score tables with paired uncertainty; quality/cost plots; separate interactive latency plots when adequately sampled; controlled intervention figures; failure examples; and a results-to-claims matrix.

Release permitted predictions, scorer, canonical prompts/wrappers, frozen IDs/revisions, RunPod reproduction instructions, dependency locks, statistical settings, and a sanitized billing ledger. Where raw redistribution is restricted, release IDs and retrieval instructions instead.

Use the AgentFoundry paper as a rigor reference, not as a source of fabricated theorem requirements. The abstract must distinguish completed panels, incomplete panels, exploratory findings, and validated conclusions. Remove the “foundational” framing if the study adds only another ranking or repeats existing boundaries.

Stop or narrow the project when credible frontier runs are unaffordable, prior work already establishes the proposed insight, results depend on an asymmetric prompt, the explanation fails held-out validation, or precision cannot support replacement. Report that outcome plainly.
