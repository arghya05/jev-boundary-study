# Cost comparison and flexible spending scenarios

Prepared 4 October 2026. No measured model costs or accuracy results exist. **Budget is flexible; no hard dollar limit applies.** These estimates help choose stages, not constrain reasoning or promise a final bill.

## Model prices and one-decision illustration

| Model/configuration | Input per million | Billed output per million | Example API cost per decision |
|---|---:|---:|---:|
| Official Jev | $0.042 | $0 | $0.000063 |
| OpenAI Astra, standard | $10 | $50 | $0.115 |
| Claude Fable 5.1, standard | $10 | $50 | $0.115 |
| OpenAI Astra, batch if supported | $5 | $25 | $0.0575 |
| Claude Fable 5.1, batch | $5 | $25 | $0.0575 |

Example assumptions: 1,500 actual input tokens for each service, one request, and 2,000 billed frontier output tokens **including internal reasoning**. Jev is input-billed; no additional batch discount is assumed. Actual token counts differ across providers and task formats.

Sources: [official Jev models](https://docs.typesafe.ai/models), [Astra model pricing](https://developers.openai.com/api/docs/models/gpt-6-astra), [OpenAI Batch](https://developers.openai.com/api/docs/guides/batch), and [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing). Recheck prices, cache categories, account access, and exact model/batch support when executing.

## Stages: both frontier APIs combined

Assume batch rates above, 1,500 input tokens, and one call per task/model:

| Proposed scope | Paired tasks | If billed output averages 2,000 | If it averages 8,000 | What it supports |
|---|---:|---:|---:|---|
| Development pilot | 24 | $2.76 | $9.96 | Feasibility, not a replacement claim |
| Pilot + full FOLIO | 228 | $26.22 | $94.62 | A complete public logical-reasoning comparison |
| Above + 288 controlled base conditions | 516 | $59.34 | $214.14 | A candidate mechanism test, subject to power |
| Above + full JudgeBench | 1,136 | $130.64 | $471.44 | Adds difficult judging evidence |
| Pilot + all four public panels + 288 controls | 5,416 | $622.84 | $2,247.64 | Broader coverage, if the contribution warrants it |

These rows are **frontier API-only scenarios**. They exclude additional counterfactual/invariance and G02 evidence-removal control calls, prompt/effort sensitivity, Jev, RunPod/storage, retries, human validation, taxes, and any extra development required for a credible predictive rule. Explicitly price these before execution. The 288 base conditions may be too small for the intended interaction or transfer claim; count independent graphs, not rows, in power calculations.

At the same illustrative Jev input length, 516 decisions cost about $0.033 and 5,416 cost about $0.341 in marginal Jev API fees. Provider-specific billing must replace these estimates. RunPod costs are the actual hourly quote times billed session time plus storage; use a cheap coordinator and stop it while batch jobs wait.

Standard synchronous frontier rates in the current snapshot double these batch API-only totals. Caching may reduce some charges but also introduces writes and eligibility conditions. Do not assume every long input has 1,500 tokens or every answer uses exactly 2,000 reasoning tokens.

## How the paper decides whether cheaper is better

Report, for every funded panel and each frontier comparator:

| Evidence | Cost comparison that follows |
|---|---|
| Jev accuracy is demonstrably higher | Compare actual API and end-to-end operating cost at that achieved quality |
| Jev passes the frozen noninferiority margin | Report savings at the explicitly permitted quality loss |
| Frontier accuracy is materially higher | Report its extra dollars and the break-even consequence of an error |
| Precision or prompt stability is inadequate | Report costs and uncertainty without a replacement recommendation |

If frontier accuracy improves by 0.10 and costs $0.057437 more per decision in the illustrative batch scenario, the average-error break-even consequence is about **$0.574 per error**. This is arithmetic under hypothetical accuracy, not a finding about the models. Use real paired accuracy and an appropriate loss matrix later.

The final release includes actual token/fee categories, failures/retries, invoices or aggregate reconciliation, marginal dollars per 1,000 decisions, shared infrastructure allocation, total study expense, and separate credit-adjusted cash outlay. Keep offline batch and interactive synchronous operating points distinct.
