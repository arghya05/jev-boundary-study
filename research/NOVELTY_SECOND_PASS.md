# Second-pass arXiv novelty audit

Reviewed 4 October 2026. This is a targeted method-level review, not an assertion that every relevant publication was found. No experiments were run or reproduced. The conclusions below are our assessment of overlap, not endorsements of source results or proofs.

**Current scope update:** this file records the rejected/conditional solver proposal. Its implementation and fixed-budget requirements are historical and superseded by the empirical boundary study in [RESEARCH_PLAN.md](../RESEARCH_PLAN.md). The user now allows a flexible budget without hard numeric limits. Read [EMPIRICAL_NOVELTY_AUDIT.md](EMPIRICAL_NOVELTY_AUDIT.md) for the active contribution gate. Do not execute a solver study on the basis of this older audit.

## Decision

**The broad original proposal does not yet satisfy the user's novelty requirement. Do not spend on it as a foundational paper project.** The plan retains it as a conditional implementation hypothesis. Adding Jev to semantic parsing, a solver, active questions, and conformal prediction is insufficient.

A remaining candidate question is end-to-end false acceptance under **both missing semantic candidates and dependent neural checks**, using an answer-directed audit at a bounded cost. No claim that this setting is absent from all literature has been established. Its novelty must survive comparison with the methods below, including their reasonable adaptations.

## Main Jev paper re-read

[Evaluating and Benchmarking the System One Model Jev, arXiv:2609.37647v1](https://arxiv.org/html/2609.37647v1): inspected the main methodology, benchmark/request construction, metrics, open-model protocol, results, cost, contamination probes, and limitations (§§3–5).

Its baseline protocol disables thinking and scores answer-token probabilities; proprietary generative models are excluded. Its limitations explicitly acknowledge that reasoning could improve those baselines. Thus this paper does not establish superiority to reasoning-enabled Claude/OpenAI APIs. Filling that comparison alone is an empirical extension, not a foundational method. Its own question-perturbation follow-up also cannot be claimed as an original idea from this project.

## Closest methods and rejected claims

| Source and inspected material | Existing mechanism | Decision for this plan |
|---|---|---|
| [JEV-as-a-Judge, 2609.26550v1](https://arxiv.org/html/2609.26550v1), method/results/limitations sections | Confidence-based acceptance and escalation; frontier judge comparisons. | Reject a generic cheap cascade as the main contribution. |
| [Cheaper, Faster, and Wrong in the Same Places, 2609.29769v1](https://arxiv.org/html/2609.29769v1), cascade analysis and related results | Measures shared rubric errors and the limits of fallback routing. | Error dependence itself is not a new discovery. |
| [Code Owns the Simulation, Jev Owns the Evaluation, 2610.01834v1](https://arxiv.org/html/2610.01834v1), task definitions and lookahead sections | Executable consequences and decision evaluation; predicted-consequence variants. | Reject broad Jev-plus-code or atomic chaining novelty. |
| [LINC, 2310.15164v1](https://arxiv.org/html/2310.15164v1), §§2–3 and error-analysis context | Natural language to FOL, theorem proving, and sampled majority decisions. | Translation plus deduction and semantic fidelity concerns are established. |
| [Grammars of Formal Uncertainty, 2505.20047v1](https://arxiv.org/html/2505.20047v1), methodology, theorem, experiments | Samples formal programs, estimates grammar uncertainty, studies verification confidence on closely related datasets. | Reject retaining multiple formalizations or uncertainty-aware verification as new by itself. |
| [DeepProbLog, 1805.10872](https://arxiv.org/html/1805.10872), neural predicates and §4 inference | Neural finite choices, grounded query formulas, knowledge compilation. | Reject finite neural alternatives followed by exact inference as a new foundation. |
| [NeurASP, 2307.07700](https://arxiv.org/html/2307.07700), probability/stable-model definitions and inference material | Neural atom scores coupled to answer-set constraints. | Selector variables and constrained interpretations have close precedents. |
| [DeepStochLog, 2106.12574](https://arxiv.org/html/2106.12574), §§2–4 and evaluation framing | Neural grammar alternatives and shared tabulated inference. | Avoid claiming packed inference or neural grammar composition is new. |
| [EC², 1010.3091](https://arxiv.org/abs/1010.3091), original formulation material; [ECED](https://yuxinchen.org/files/papers/chen17eced-long.pdf), formulation/theory sections | Cost-sensitive tests to resolve target equivalence classes, with noisy-test extensions under assumptions. | Answer-relevant query selection is established; compare executable algorithms. |
| [LogicTrack, 2609.21492v1](https://arxiv.org/html/2609.21492v1), §§2.1–2.3 and results | Step formalization, solver checking, premise fidelity, adaptive backtracking. | Reject semantic grounding plus formal verification plus correction as a new combination. |
| [Beyond Gold Standards, 2506.10903v1](https://arxiv.org/html/2506.10903v1), §2 and ensemble definition | Distinguishes logical preservation from formal validity and combines atomic judges with prover evidence. | Semantic evaluation of formal statements is already a judge research area. |
| [Roundtrip Verification and Repair, 2604.25031v1](https://arxiv.org/html/2604.25031v1), §§3–4, semantic-alignment results, residual failures | Re-formalization equivalence, stage diagnosis/repair, and explicit acknowledgment of stable but wrong semantics. | Reject discovering that self-consistency can validate a wrong meaning. |
| [The Faithfulness Gap, 2606.16541v1](https://arxiv.org/html/2606.16541v1), §§3–8 and §§11–12 | Bidirectional consequence fingerprints, counterfactual probes, adaptive budgets, controlled drift benchmark, and conditional guarantees. | This is a mandatory close baseline. Probe-driven semantic auditing and budget allocation cannot be presented as untouched. |
| [Conformal Early Stopping in Mixed Integer Optimization, 2602.01476v1](https://arxiv.org/html/2602.01476v1), §§3–4 | Calibrates a learned solver stopping rule with probabilistic solution-quality guarantees. | Generic conformal early stopping is already studied. |

Inspection of a theorem statement does not validate its proof. In particular, model-generated probe coverage and formal-program agreement must not be equated with correct human-intended semantics. The faithfulness paper itself limits what its certificate establishes. Our comparison must respect those limits rather than argue against a stronger claim it does not make.

## Additional Jev records discovered

These extend the earlier inventory. Their discovery shows why the original 17-paper list could not support an exhaustive novelty claim.

| Original record | Inspection | Implication |
|---|---|---|
| [Beyond Calibration, 2609.33209v1](https://arxiv.org/html/2609.33209v1) | Method and protocol sections | Cross-question probability coherence and format consistency already have controlled audits. |
| [Type-Safe Is Not Error-Free, 2609.26758v1](https://arxiv.org/html/2609.26758v1) | Readout definitions, label–rubric intervention, controls, results | Option names and definitions are already separated experimentally. |
| [JevAdvBench, 2609.31142v1](https://arxiv.org/html/2609.31142v1) | Introduction, benchmark/interface framing; remaining detailed methods not fully inspected | Typed-model adversarial robustness and repeat-noise-aware decision flips are covered. |
| [Decision Hijacking, 2609.28613](https://arxiv.org/abs/2609.28613) | Original abstract | Prompt-injection manipulation of Jev probabilities is covered. |
| [System One Agent Security, 2609.33401](https://arxiv.org/abs/2609.33401) | Record inspected; full method pending | Security reliability/selective automation is a close topic requiring full comparison if pursued. |
| [Just Ask Jev, 2609.29429](https://arxiv.org/abs/2609.29429) | Record inspected; full method pending | Alignment-failure detection is also a populated topic. |

[Awesome Jev Robustness](https://github.com/Yifan-Lan/awesome-jev-robustness) was used only as a discovery catalogue. Original records above control the claims. Its listing counts are not independently verified studies or an exhaustive bibliography.

## Why the proposed solver encoding alone is insufficient

Our analysis: choosing one semantic alternative per slot and minimizing the sum of its costs under logical constraints is a weighted constraint-optimization problem. Obtaining one minimum-cost witness per answer adds an answer condition to the same problem. Finite Horn closure can be encoded using standard bounded derivation variables. These reductions can be useful engineering, but they do not alone establish a new inference principle.

Likewise, a solver returns correctness relative to the supplied interpretation. Agreement among retained interpretations cannot establish that the intended interpretation was retained. An `OTHER` option identifies a possible failure route; it does not measure the probability of every omitted meaning. Returning all labels on incomplete search is conservative handling, not a new theorem.

## Candidate contribution Claude must substantiate

The candidate is **budgeted answer-directed semantic checking with final-decision error control when candidate omission and shared oracle mistakes coexist**. A defensible contribution would need at least one of:

1. A distinct algorithm with a nontrivial computational advantage over strong packed neural-logic and active-testing adaptations.
2. A useful guarantee under clearly stated dependence/omission assumptions that the closest methods do not already provide. A union bound or ordinary split-conformal coverage is insufficient.
3. A substantial, independently labelled empirical mechanism and public benchmark result that persists against the close baselines and frontier systems.

Before a paid pilot, produce an overlap matrix covering assumptions, algorithm, objective, guarantees, dataset conditions, and costs. If an applicable prior method already supplies the proposed advance, stop or redesign. Do not spend money to rediscover its result with Jev.

This audit rejects duplicate claims; it does not prove that a surviving contribution exists, that Jev wins, or that a conference will accept the paper.
