# Jev versus frontier LLMs: research and execution plan

Prepared 4 October 2026. **Start here.** This is the consolidated plan for Claude to implement later. No experiment has run; API and RunPod experiment spending is $0. The budget is flexible, with no fixed dollar ceiling. Every experimental workload must run on RunPod.

## Objective and proposed contribution

Establish, under controlled comparisons, **where official Jev is more accurate than frontier OpenAI/Claude models, where it provides comparable quality at lower cost, and where a frontier model is worth the extra expense**.

Working paper title: **“When Can Decision Models Replace Frontier LLMs? Controlled Evidence on Accuracy and Cost.”**

The proposed contribution is an explanation of the boundary and a test of whether it transfers to new tasks. Merely showing that Jev is cheap, comparing newer APIs, or reporting another benchmark ranking is insufficient.

| Research question | Falsifiable hypothesis | Evidence needed |
|---|---|---|
| G01: computation versus recognition | Increasing dependency depth disproportionately reduces Jev accuracy after length, distractors, and surface interpretation are controlled | Paired controlled interventions, with independent labels and confidence intervals |
| G03: transferable model choice | A small set of observable features predicts which model is sufficient on unseen inputs better than length-only or task-family lookup | Frozen rule, unseen graph templates, and held-out task-family evaluation when broad claims are made |
| G02, optional: evidence sufficiency | Missing information produces a different failure pattern from complete information requiring deeper deduction | Verified premise-removal conditions crossed with depth, separately priced and preregistered |

These are **candidate gaps, not confirmed unprecedented findings**. Existing work already covers Jev judging, strengths and weaknesses, cascades, counterfactual tests, probability coherence, and batching. The [20-question gap inventory](research/GAP_INVENTORY.md) maps the overlap and supporting controls. The [empirical novelty audit](research/EMPIRICAL_NOVELTY_AUDIT.md) defines the gate before spending.

The paper can support a foundational empirical insight only if a material explanatory result survives these controls and independent validation. Neither frontier wins nor top-conference acceptance is guaranteed.

## Models and comparison contract

| System | Proposed ID from the research-date documentation | Configuration |
|---|---|---|
| Official TypeSafe Jev | `jev-1.13.0` | One native typed decision per task |
| OpenAI frontier | `gpt-6-astra` | Native reasoning enabled; proposed high effort |
| Claude frontier | `claude-fable-5-1` | Native adaptive reasoning; proposed high/recommended effort |

Recheck account access, vendor recommendations, pricing, and exact versions before execution. Freeze the chosen configuration before final evaluation and log resolved versions. Do not silently substitute weaker models. The primary claim refers to these tested configurations, not every frontier model or maximum-effort setting.

Official references: [Jev model documentation](https://docs.typesafe.ai/models), [OpenAI Astra](https://developers.openai.com/api/docs/models/gpt-6-astra), and [Claude models](https://platform.claude.com/docs/en/models/overview).

All three systems receive the **same canonical task text, evidence, instructions, candidates, candidate order, and examples**. Primary evaluation is zero-shot. Native transport schemas differ; release complete wrappers and audit them for asymmetric hints, omissions, or output demands. Equal text does not imply equal tokenization or internal compute.

Keep retrieval, tools, memory, solver assistance, and extra decomposition queries off in the primary comparison. Ask for a final label while allowing sufficient native internal reasoning. Never disable thinking or shorten output headroom merely to make the frontier look worse or cheaper.

Use the same RunPod client, region, pinned environment, and experimental window. Provider-side hardware and hidden serving behavior remain outside our control. This is a matched API-system study, not a same-hardware experiment.

## Dataset selection and order

| Priority | Dataset and final split | Full public panel | Role |
|---|---|---:|---|
| 1 | [FOLIO](https://github.com/Yale-LILY/FOLIO), public validation | 204 | Natural-language deduction and evidence interpretation |
| 2 | [JudgeBench](https://huggingface.co/datasets/ScalerLab/JudgeBench), gpt and claude splits | 350 + 270 | Difficult correctness judging; score splits separately |
| 3 | [Banking77](https://github.com/PolyAI-LDN/task-specific-datasets), test | 3,080 | Fine-grained intent decisions with all 77 candidates |
| 4 | [ANLI](https://huggingface.co/datasets/facebook/anli), test_r3 | 1,200 | Adversarial natural-language inference |

The broad menu totals 5,104 rows before shared-question auditing. Freeze the final included panels **before observing held-out model outcomes**. Order is for operational staging and costing, not permission to add only datasets favorable to Jev.

Start with FOLIO and the controlled panel as a compact reasoning study. Add JudgeBench for judging evidence. A general recommendation spanning different decision tasks requires broader validation, such as Banking77 and ANLI. If only the smaller study is completed, narrow the title and claims accordingly.

Use official labels and source semantics. Exclude gold answers, ANLI explanations, FOLIO logical forms/proofs, and JudgeBench response-generator identity from inference. Keep operational failure separate from logical Unknown. Preserve all final rows and published label distributions.

Pin release commits, IDs, hashes, licenses, source clusters, and scorer mappings. A sampled panel must be labeled as sampled; it is not a full benchmark or official SOTA result. Check redistribution rights before releasing text.

## Experiment 1: remote development pilot

Prepare **24 development cases**, six per family:

- Banking77 train.
- ANLI train_r3.
- FOLIO train, with source stories separated from final evaluation.
- Independently authored correctness-judging practice cases, outside JudgeBench.

Select cases with a sealed seed and label stratification before viewing model outputs. The first two cases supply billing/interface telemetry and are reused in the pilot.

The pilot tests adapter correctness, token usage, truncation, failure handling, and whether the controlled manipulations behave as intended. It does not establish superiority, a two-point noninferiority margin, or general model-selection performance.

Prepare remote fixtures first. Then issue small matched groups of paid requests, accounting for expected and configured maximum usage, queued commitments, and native SDK retries. Allow at most one transient retry; never retry an incorrect answer. Cache by full task/model/version/effort/schema/protocol hashes.

Deliver `pilot_report.md` with actual usage, directional paired results, failures, total charges, and expected/conservative forecasts for complete later stages. Expand development for a prespecified feasibility or power question, not to search for Jev wins.

## Experiment 2: controlled dependency benchmark

Construct a limited, explicitly documented formal fragment with deterministic truth semantics. A suitable initial fragment uses finite entities, signed facts, acyclic rules, and open-world True/False/Unknown answers. Public FOLIO evaluation remains unrestricted by this fragment.

For each controlled example:

1. Generate a rule graph and target claim from a sealed base seed.
2. Compute derivability independently of model responses. True means the claim follows; False means its explicit negation follows; Unknown means neither follows. Reject contradictory generated worlds before model calls.
3. Produce dependency depths 1, 3, and 5, with fixed total rule count and matched text length using unused rules.
4. Cross depth with 0 versus 8 irrelevant facts. Balance label distribution and record remaining length/surface confounds.
5. Add a fixed subset of verified answer-changing fact/rule edits and answer-preserving entity renaming or premise reorderings.
6. Cross-check the reference semantics with an independently implemented scorer and obtain blinded human review of natural-language fidelity.

An initial final-design candidate is **48 independent base seeds × six depth/context conditions = 288 decisions per model**. This is a proposed sample size, subject to independent-cluster power analysis. Paired edits, evidence-removal conditions, and any larger sample are extra calls that must be counted.

Include a surface-recognition check if needed to test whether a depth effect is explained by misreading individual rules. Supplying verified intermediate consequences is a separate information condition given identically to all models; report its computation cost and avoid attributing the resulting gain to intrinsic Jev capability.

Use fresh held-out graph and language-template seeds. Group every variant from a seed together in uncertainty calculations and train/test splits. No generated gold label may depend on the tested models.

Measure accuracy differences, sensitivity to answer-changing edits, and correctness under answer-preserving edits. A decline with depth alone is not an architectural proof; the claim is a controlled behavioral result.

## Experiment 3: public benchmarks and transfer

Run every included public-panel item through every required model under the frozen comparison contract. Save predictions without gold access; join gold only in a separate scorer.

Report per-panel accuracy and paired differences, failures, actual cost, and operational mode. Do not treat one frontier's answers as ground truth or replace new matched calls with historical leaderboard numbers.

To test G03, define a small feature set and selection rule before evaluating its final outputs. Features may include character/token-length estimates, candidate count, explicit connective markers, and prespecified structural indicators.

**Separate explanatory annotations from deployment features.** Oracle graph depth and human difficulty judgments can explain benchmark results, but are not automatically available in a real application. A deployed rule may use them only if their extraction process is validated and its full cost is counted.

Compare the rule against:

- Always Jev, always OpenAI, and always Claude.
- Length-only and task-family lookup rules.
- A relevant established routing method when claiming a routing contribution.
- A hypothetical oracle selector as a diagnostic upper bound, clearly unavailable at deployment.

Fit on permitted development data. Assess unseen templates. For cross-family claims, use a frozen leave-one-family-out procedure with no held-out-family label tuning, document all folds, and compare their performance. A 24-case pilot is not enough training evidence for a general router; price additional disjoint development data before claiming one.

Failure to transfer limits the recommendation to the tested family. Ordinary classifier or deterministic-code baselines are optional separate deployment comparisons; without them, do not claim Jev is optimal among every possible alternative.

## Statistics and deployment conclusions

Define `delta = accuracy(Jev) - accuracy(frontier)`, separately for each provider and panel.

The draft tolerated accuracy loss is **2 percentage points**, to be justified for the intended use and frozen before final outcomes. That is a scientific quality margin, not a spending limit.

| Conclusion | Required quality evidence |
|---|---|
| Jev accuracy win | Adjusted lower bound for delta exceeds zero |
| Jev comparable and cheaper | Adjusted lower bound exceeds -0.02 and measured costs are lower |
| Material frontier advantage | Adjusted upper bound is below -0.02 |
| Inconclusive | Other outcomes, insufficient precision, or unstable comparisons |

Use paired uncertainty at the independent story/question/graph-seed level. The full four-family study has eight primary family/provider comparisons; freeze simultaneous interval and multiplicity procedures. Put controlled interactions in a separate prespecified testing family. Do not narrow the hypothesis family after an unfavorable or incomplete panel.

Before final calls, choose the exact interval implementation and check its coverage on remote simulations, including small samples, rare discordances, and clustered variants. A bootstrap with no observed discordances must not yield a falsely certain replacement claim. Repeats and variants are not extra independent samples.

Power depends on paired discordances and independent-cluster counts. Use development estimates to choose a worthwhile final sample; enlarge it for precision, not because a result nearly becomes significant.

For deployment economics, report error consequences as well as accuracy:

`expected loss = inference cost + error probability × consequence of an error`.

Use class-dependent losses when errors have unequal consequences. When a frontier costs more and gains accuracy, its illustrative break-even error consequence is extra cost divided by accuracy gain. This is established decision analysis, not a novel theorem.

## Cost comparison and flexible scaling

Research-date snapshot, USD per million tokens:

| Model/mode | Input | Billed output, including reasoning where applicable |
|---|---:|---:|
| Official Jev | 0.042 | 0 |
| OpenAI Astra / Claude Fable, standard | 10 | 50 |
| Their batch modes, subject to support | 5 | 25 |

Sources: [Jev pricing](https://docs.typesafe.ai/models), [OpenAI model pricing](https://developers.openai.com/api/docs/models/gpt-6-astra), [OpenAI Batch](https://developers.openai.com/api/docs/guides/batch), and [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing). Recheck at execution.

Illustrative two-frontier batch API totals, assuming 1,500 input tokens and one call per model per task:

| Stage | Paired tasks | At 2,000 billed output tokens/call | At 8,000 |
|---|---:|---:|---:|
| Pilot | 24 | $2.76 | $9.96 |
| Pilot + FOLIO | 228 | $26.22 | $94.62 |
| Above + controlled base panel | 516 | $59.34 | $214.14 |
| Above + JudgeBench | 1,136 | $130.64 | $471.44 |
| Pilot + all public panels + base controls | 5,416 | $622.84 | $2,247.64 |

These are **scenarios, not measured expenses or caps**. They exclude extra control variants, larger development/power samples, prompt sensitivity, Jev, RunPod/storage, retries, human review, and taxes. Banking77 choices and JudgeBench responses may substantially exceed the example input length. Do not force reasoning to the illustrative output count.

Choose scope using actual pilot usage and the evidence the next stage adds. Record spent money, queued commitments, remaining expected expense, and conservative totals. Investigate unexplained billing changes before scaling.

Use a cheap suitable RunPod coordinator; no GPU model weights or training are required. Stop it while API batches process. Include startup, idle time, repeated sessions, downloads, storage, and cleanup.

Report actual API dollars per 1,000 decisions, total study expense, and consistent shared-infrastructure allocation. Separate credits from list-price economic cost. Do not double-count reasoning already included in output totals.

For interactive speed claims, collect synchronous latency with matched client conditions, concurrency one, nonstreaming requests, randomized provider order, and actual synchronous prices. Do not combine discounted batch costs with unrelated synchronous latency.

## Milestones and go/no-go decisions

| Milestone | Deliverable | Continue when |
|---|---|---|
| M0: desk review | Claim matrix against close papers; chosen G01/G03 contribution and optional G02 | A material distinction remains plausible; controls alone are not presented as novelty |
| M1: package | Pinned remote environment, gold-blind adapters, manifests, scorer, billing/cache safeguards | Source semantics, task parity, and failure handling are verified |
| M2: pilot | Usage/failure report and complete-stage cost/power forecasts | Credible frontier configurations and a useful controlled experiment are feasible |
| M3: freeze | Final IDs/seeds, prompts, models, analysis, modes, and scope commitment | Sample size and design can support the intended claim |
| M4: final evaluation | Complete predictions, failure ledger, bills, and public-panel scores | Every registered denominator is retained and comparisons are interpretable |
| M5: explanation/transfer | Controlled effects, proxy baselines, and held-out selection-rule results | Results add knowledge beyond known Jev rankings |
| M6: paper/release | Results-to-claims matrix and reproducibility package | Claims match completed evidence; limitations and negative findings are retained |

Stop or reframe if the closest literature already establishes the proposed insight, the explanation reduces to text length/domain identity, the apparent gain depends on asymmetric prompting, a credible frontier configuration is missing, or transfer/precision does not support replacement.

## Paper evidence and release

The paper should contain:

1. A precise prior-work comparison and the surviving research question.
2. Public benchmark accuracy tables with paired uncertainty and all failures.
3. Controlled depth/context effects and verified changed/unchanged truth tests.
4. Held-out rule performance and limitations, if a transferable rule is claimed.
5. Quality-adjusted costs and separate interactive/offline operating points.
6. Cases where Jev is appropriate, where each frontier is better, and where evidence is inconclusive.

Release permitted prediction files, source IDs/revisions, canonical prompts and wrappers, reference and benchmark scorers, statistical settings, environment locks, sanitized usage/expense ledger, and one-command RunPod reproduction instructions. Where text redistribution is restricted, release retrieval scripts and IDs.

Use the user's [AgentFoundry paper](https://github.com/arghya05/agent-foundry/blob/main/research-paper/AgentFoundry_Paper.pdf) as a rigor reference. Do not manufacture proofs or describe a proposal as an achieved foundational result.

## Claude handoff and supporting files

When you are ready for Claude to execute, give it this instruction:

> Read PLAN.md and CLAUDE_HANDOFF.md, then implement and execute the study in their stated order. Complete the remote package and explicit novelty decision before paid calls. If a material contribution survives, proceed through the RunPod pilot and evidence checkpoints with flexible staged cost forecasts; no fixed dollar ceiling is required. Preserve matched prompts, reasoning-enabled frontier baselines, independent labels, and locked evaluation. Stop before spending if the proposed contribution merely repeats prior work. Report failed hypotheses honestly; do not claim a novel gap or benchmark win before evidence.

Supporting detail:

- [CLAUDE_HANDOFF.md](CLAUDE_HANDOFF.md): implementation stages.
- [RESEARCH_PLAN.md](RESEARCH_PLAN.md): extended research rationale.
- [GAP_INVENTORY.md](research/GAP_INVENTORY.md): 20 identified questions and controls.
- [PUBLIC_BENCHMARK_PROTOCOL.md](research/PUBLIC_BENCHMARK_PROTOCOL.md): dataset and scorer rules.
- [FAIR_COMPARISON_PROTOCOL.md](research/FAIR_COMPARISON_PROTOCOL.md): matched inputs and operations.
- [COST_COMPARISON.md](research/COST_COMPARISON.md): price assumptions and stage scenarios.
- [protocol_draft.json](research/protocol_draft.json): machine-readable draft.

**Current status:** plan prepared; novelty unconfirmed; versions/splits/statistical implementations still require the specified execution freeze; no paid work started.
