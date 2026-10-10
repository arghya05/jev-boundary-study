# Empirical novelty audit for the current proposal

Reviewed 4 October 2026. Targeted source review, not an exhaustive claim that no paper addresses this topic. No source experiment was reproduced and no new model experiment was run. This audit supersedes solver-based novelty requirements for the active plan.

**Additional overlap review:** [GAP_INVENTORY.md](GAP_INVENTORY.md) now maps 20 identified questions and a 16-source close-prior register. It includes probability-coherence papers, Probability Contracts, JevAdvBench's batching controls, DecisionBench, and domain-specific repositories. The decision remains **novelty not cleared**. These additions reject further claims of untouched coherence, batching, or cross-domain benchmarking.

## Closest overlap

| Source | What is already covered | Consequence |
|---|---|---|
| [Evaluating and Benchmarking the System One Model Jev](https://arxiv.org/html/2609.37647v1) | Broad capability assessment, task variation, cost, and limitations; open generative baselines disable thinking | A reasoning-enabled public API comparison strengthens evidence but is not by itself a foundational discovery |
| [JEV-as-a-Judge](https://arxiv.org/html/2609.26550v1) | Frontier judge comparisons, operating strengths/limits, fees, latency, confidence, and escalation | The general question “where Jev versus an LLM?” is already studied for judging; reject first-ever frontier judge and cheap-cascade claims |
| [jev-frontier-100](https://github.com/softpudding/jev-frontier-100) | Counterfactual pairs and several reasoning budgets against smaller open models | Counterfactual tests and reasoning-budget variation are not new components |
| [Code Owns the Simulation, Jev Owns the Evaluation](https://arxiv.org/abs/2610.01834) | Separation of executable consequences from decision evaluation | Supplying intermediate computation cannot be advertised as an untouched idea |
| [Cheaper, Faster, and Wrong in the Same Places](https://arxiv.org/abs/2609.29769) | Shared judging errors and limits of escalation | Error overlap or confident failures alone do not create novelty |
| [Probability Contracts](https://arxiv.org/abs/2609.37470) | Exact targets, interface alignment, and induced decision loss | Decision-aware probability/interface evaluation has direct prior overlap |
| [Do System One Decisions Add Up?](https://arxiv.org/abs/2609.33971) | Fine/coarse prediction and probability coherence | Reject hierarchical probability coherence as untouched |
| [JevAdvBench](https://arxiv.org/html/2609.31142v1) | Single-edit robustness and explicit batched/single-question repeat controls | Reject generic perturbation and batching-invariance novelty |
| [DecisionBench](https://huggingface.co/datasets/Hanno-Labs/decision-bench) | Broad typed-decision tasks and reasoning metadata | A cross-domain dataset or task flag alone is insufficient |

These sources materially overlap the user's desired paper. The literature does **not** justify saying no previous paper establishes where Jev is useful. Vendor cost advantages, public benchmark names, and use of RunPod add no scientific novelty.

## Candidate contribution to test

A possible useful addition is a **controlled and externally validated explanation of the Jev/frontier replacement boundary**, rather than another performance ranking:

- Within-task depth/context interventions with verified changed and unchanged labels, confound controls, and independent source graphs.
- Native reasoning-enabled OpenAI and Claude baselines at credible effort and output headroom.
- Prespecified quality-loss tolerances and billed cost, yielding superiority, noninferiority-plus-cheaper, frontier advantage, or inconclusive evidence.
- A parsimonious rule using features available before inference, validated on unseen templates and funded held-out task families, compared with length-only and domain-lookup baselines.

The optional evidence-sufficiency-by-depth interaction is described as G02 in the inventory. Missing evidence itself is already studied. Any learned model-selection claim must also compare with the relevant established routing literature; generic routing is not a new algorithm.

Our inference is that this joint empirical design is a promising candidate for further review. We have **not** established that the joint design or its eventual findings are unprecedented. Noninferiority testing, paired intervals, economic break-even rules, counterfactual evaluation, and routing are established techniques.

## Required gate before spending

Claude must inspect the complete relevant methods and appendices of the closest studies, including their controlled tests and operating-boundary sections. Search for other decision-only model evaluations and compute/semantic-depth studies. Record exact versions, review date, inspected sections, and repository evidence. Do not describe abstracts or README inspection as complete paper/code replication.

Write a claim matrix answering:

1. What specific explanatory finding is missing, rather than which model/version is newer?
2. Which controlled intervention can falsify that finding, and which confounds remain?
3. What independent held-out result would distinguish it from existing task rankings?
4. Can the funded design provide useful precision and credible frontier baselines?
5. What result would cause us to conclude the gap is already covered or the hypothesis false?

If the only differences are stronger model names, a few additional datasets, or a new bill, classify the project as a replication/extension and do not promise a foundational paper. If the distinctive explanation is already established, stop before paid inference.

## Permitted and prohibited language now

Permitted: “We propose to test a task-dependent capability and cost boundary under controlled comparisons.” “Novelty is not yet cleared.” “The plan names public panels and an affordable feasibility pilot.”

Prohibited before evidence: “First paper to compare Jev with frontier LLMs.” “No arXiv paper covers this.” “Jev beats the best models.” “A bias-free benchmark.” “A proven foundational result.” “Guaranteed NeurIPS acceptance.”

For the broader initial review and rejected solver ideas, see [LITERATURE_AUDIT.md](LITERATURE_AUDIT.md) and [NOVELTY_SECOND_PASS.md](NOVELTY_SECOND_PASS.md). Their historical method advice is not an instruction to execute a solver study.
