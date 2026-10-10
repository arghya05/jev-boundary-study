# Fairness and cost protocol: official Jev versus frontier APIs

Draft, 4 October 2026. The aim is to control avoidable comparison bias, not to claim a bias-free experiment. No calls have been made.

## Same task prompt

Create a canonical task object containing task instructions, evidence, question, answer choices and descriptions, order, and examples. Render one text and hash its exact UTF-8 bytes. All models receive the same semantic information. Primary evaluation is zero-shot, with all tools and retrieval disabled.

A generic contract is:

```text
Task: [frozen task-specific definition and answer semantics]
Evidence: [all permitted source text]
Question: [the decision to make]
Choices: [the same ordered labels and descriptions]
Select the correct choice using the supplied information and task definition.
Return the final choice identifier.
```

Freeze task-specific exceptions, such as a judging question that permits relevant knowledge or an inference task restricted to premises. Do not imply that every family has closed-world semantics.

Use native typed choice for Jev and supported structured final-label output for frontiers. The transport schemas differ. Release the complete state/question/instructions/criteria or system/user/schema wrappers and review them for added or omitted evidence, hints, duplicated semantic instructions, and asymmetric output demands. A canonical hash alone does not prove an adapter is fair.

Answer choices in output schemas may duplicate their identifiers, but descriptive information cannot be supplied to one model alone. Request no visible long rationale from one system. Do not discard a frontier answer simply because it used internal reasoning.

## Reasoning and budgets

Use vendor-supported reasoning-enabled frontier settings, proposed high/recommended effort. Freeze output headroom based on development fixtures and telemetry. Record termination reasons; report truncations as operational failures. Do not retune after viewing final test answers.

Equal prompt text is the primary control. Equal generated tokens or monetary budgets are different questions and belong to a separate named comparison. Frontiers and Jev have different interfaces and compute paths; identical effort names or input text do not establish equal FLOPs.

A funded prompt-sensitivity track must give each model the same number of development candidates and comparable selection effort. The common-prompt primary result remains separately reported. A recommendation that reverses under ordinary prompt variants must disclose that instability.

## Same client environment

All clients, scoring, and analysis run from RunPod. Pin container, operating system, SDKs, adapter versions, region, clock, and client concurrency. Use a short shared experiment window, record dates, and monitor resolved model IDs.

For synchronous latency: concurrency one, streaming disabled, total wall time from request dispatch to complete response, warmup policy fixed and charged, provider order randomized/interleaved within matched blocks. Record whether each response came from cache, its route/tier if exposed, and failures. Share connection setup policy.

Repeat measurements on a small **prespecified** subset only if funded. Repeats characterize variability and are not additional independent accuracy examples. Report median and tail uncertainty; a tiny subset does not support a stable p95 claim.

Provider-side hardware, hidden prompting, tokenization, batching, geography, and internal scheduling are unobserved. This is a matched client/API comparison with those explicit limits, not a same-hardware model evaluation.

## Same examples and scoring

Freeze row IDs and source cluster IDs before outcomes. All systems see the same task rows and the same candidate-order schedule. Retain official label distributions in full-panel scores. JudgeBench primary scoring uses its published presentation; reversal is a separate robustness condition shared across models.

No gold labels, proof fields, explanations, trusted answers, or source-generator identity enter inference unless the benchmark explicitly requires such information for every model.

A single scorer with frozen mappings evaluates all systems. Invalid outputs, refusals, truncations, API failures, and abstentions remain failures in the primary denominator. Distinguish logical Unknown from operational abstention.

Human adjudication, if used, must be blinded to model identity and outcome and retain official-label results separately. Do not use Claude/OpenAI as gold while evaluating the same models.

## Requests, retries, cache, and stopping

At most one transient retry under the same transport policy. Disable uncontrolled SDK retries. No retry based on low confidence, wrong answers, disagreements, or a favorable partial result.

Cache by exact task/prompt/model/version/effort/output/schema/protocol hashes. Reusing a response saves expenditure but does not yield a new current latency observation. A synchronous output and a batch output cannot be assumed identical without verification.

Stopping is based on predeclared cost reservations or technical failure, not success rate. Reserve all queued and in-flight charges. Report length-dependent incompleteness; do not silently publish only completed easy examples.

## Cost views that may be compared

1. **Interactive operating point:** synchronous accuracy/configuration, synchronous end-to-end latency, actual synchronous bill.
2. **Offline operating point:** verified batch or ordinary offline API configuration, accuracy, actual discounted fees, and queue/completion delay if reported.
3. **Standardized uncached price view:** observed token categories repriced at a dated common operating mode, clearly labeled a derived economic estimate.
4. **Total experiment outlay:** every provider call, failed attempt, development variant, RunPod session, storage, and cleanup charge.

Do not pair batch prices with synchronous latency and call it a measured operating point. Jev may have no documented batch discount; report its actual eligible mode rather than inventing a discount. Cache features may differ: show actual cached expense and an uncached view, including cache-write charges.

Per-call API cost is the sum of all reported billable categories times their applicable rates. Check whether reasoning tokens are already included in billed output totals before adding them. Short visible output does not imply little paid reasoning.

Use actual provider-specific token counts, not a shared tokenizer estimate. Add retries and billed failures. Reconcile against usage/invoices; if a provider does not expose item-level billing, release the aggregate reconciliation and uncertainty rather than fabricating exact per-item charges.

Report marginal API cost per 1,000 decisions separately from shared client costs. Allocate common RunPod/storage costs using one disclosed policy across systems. Credits and free quota affect out-of-pocket spending; list-price cost should be reported separately. Disclose taxes and human labor treatment.

## Replacement claims

Freeze the accuracy margin and testing family before outcomes. A nonsignificant accuracy gap is inconclusive, not noninferiority. Cost savings justify replacement only with demonstrated permitted quality loss and suitable failure/latency behavior.

Use paired uncertainty on source-independent units. Preserve model/provider distinctions: a Jev win against one frontier does not imply a win against the other. State the evaluated domain, versions, effort, task prompt, operating mode, and observation period with each recommendation.
