# Flexible budget, economical remote execution, and cost comparison

Draft, 4 October 2026. Plan only, no experiments, $0 API/RunPod charges. **The user has chosen a flexible budget with no hard numeric limits.** Earlier $20 and provider caps are withdrawn. Dollar figures are estimates, not ceilings. Paid execution is disabled because the current task is to prepare the plan.

## RunPod execution

RunPod is the user's required remote experiment environment. Hosted Jev/OpenAI/Claude calls need a coordinator, not locally loaded frontier weights. Select an inexpensive suitable available instance and obtain a live quote. Keep active sessions short; count startup, idle, storage, and later collection/scoring.

All experiment workloads run remotely, including dataset preparation, clients, scorers, statistics, and controlled reference checks. Document preparation may be local.

Stop the Pod while API batches wait. Persist the small ledger, request cache, pending batch IDs, and manifests. Resume briefly to collect and score. No weight downloads or training are required. Export artifacts and remove unnecessary paid storage at completion.

Use [RunPod pricing](https://www.runpod.io/pricing) to record the exact live instance/region quote. Do not treat a historical hourly example as current availability.

## Staged spending without an arbitrary cap

1. **Desk review and package preparation:** no model charges. Resolve the empirical novelty candidate before inference.
2. **Telemetry and development pilot:** start with a fixed 24-case pool and two included telemetry cases. Determine actual output/reasoning usage and adapter reliability.
3. **Minimum public evidence:** forecast a complete FOLIO 204-item paired comparison and the prespecified controlled tests needed for the proposed explanation.
4. **Stronger evidence:** price JudgeBench, additional domains, robustness checks, and adequate independent sample sizes. Expand when they materially improve the paper's supported claim.
5. **Stop or narrow:** if the gap is already covered, the hypothesis fails, adapters bias the test, or the next stage adds little information, do not keep buying calls.

There is no mandatory exact-dollar approval gate. At each stage provide expected expense, conservative expense, scientific purpose, and unresolved assumptions. Keep outcome-driven task selection prohibited. Flexible spending permits adequate frontier reasoning; it does not justify unbounded retries, prompt hunting, or idle compute.

## API policy

Use six development cases per family: Banking77 train, ANLI train_r3, FOLIO train with disjoint final stories, and independently authored judge-practice cases. Never tune on public final rows.

Before the first call, estimate expected and configured maximum charge; an average inferred from nonexistent telemetry is insufficient. Use native reasoning-enabled frontier configurations with credible output headroom. Count SDK retries and all in-flight/queued commitments.

Prefer supported batch endpoints for offline accuracy/cost. Reuse unchanged exact-hash responses and reconcile charges after small groups. At most one transient retry; never retry for a wrong answer. Additional controls are a fixed, separately priced list.

Official sources: [OpenAI Batch](https://developers.openai.com/api/docs/guides/batch), [Astra pricing](https://developers.openai.com/api/docs/models/gpt-6-astra), [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing), and [Jev pricing](https://docs.typesafe.ai/models). Recheck exact account/model support and rates before execution.

## Scenario arithmetic

For 1,500 input tokens, one call per item/provider, and batch rates $5/M input and $25/M billed output:

| Matched decisions | Output per frontier call, including paid reasoning | Both frontier models |
|---:|---:|---:|
| 24 | 2,000 | $2.76 |
| 24 | 8,000 | $9.96 |
| 24 | 16,000 | $19.56 |
| 204 | 1,000 | $13.26 |
| 204 | 2,000 | $23.46 |
| 5,104 | 2,000 | $586.96 |
| 5,104 | 8,000 | $2,118.16 |

Formula: `2 * decisions * (1500 * 5 + output * 25) / 1,000,000`.

These are API-only examples, not a promised total budget. Jev, RunPod, storage, retries, controls, development calls, and human work are extra. Actual input length varies; full Banking77 options and JudgeBench pairs may be much longer. Standard synchronous frontier rates in this snapshot double these API-only examples; cache discounts can change actual expense.

The 1,000-output row is an observation scenario, not a recommendation to limit reasoning to 1,000 tokens. The full four-panel design is substantially more expensive than a pilot. Use measured usage and precision to choose the scope, with no enforced $20, $50, or $150 ceiling.

## The paper's actual cost comparison

Report actual billed input, cache writes/reads, total output, internal reasoning when billed, fees, retries, and failures. Do not double-count reasoning included in output. Reconcile provider usage with invoices; disclose uncertainty if only aggregate billing is available.

Report dollars per 1,000 decisions alongside accuracy and uncertainty; marginal API costs; shared coordinator/storage under a consistent allocation; and the complete study outlay. Credits affect out-of-pocket spending and must be separated from list-price economic cost.

Cost savings count as a replacement result only when the allowed quality loss is independently established. The cheaper model may be worse for costly mistakes. Show break-even sensitivity to error consequences.

Keep interactive synchronous latency/prices separate from offline batch fees/queue delay. Never combine batch price with unrelated interactive latency.

The ledger records money spent, queued/in-flight commitments, expected remaining expense, and conservative stage totals. Reconcile frequently and investigate unexpected cost jumps or missing billing before scaling. Unknown rates or unobservable usage pause new paid requests until accounting is resolved; no invented numeric ceiling is needed.

The pilot tests feasibility and usage. It does not establish a two-point noninferiority margin, SOTA, or a general rule for replacing frontier models.
