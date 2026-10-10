# Literature and artifact audit

Research cutoff: 4 October 2026. Companion to [the research plan](../RESEARCH_PLAN.md).

**Current scope update:** the active plan is now an empirical capability/cost-boundary study of official Jev versus reasoning-enabled OpenAI and Claude APIs. Read [EMPIRICAL_NOVELTY_AUDIT.md](EMPIRICAL_NOVELTY_AUDIT.md) for its claim review. Solver-method and fixed-budget recommendations below are historical and superseded; the user now allows a flexible budget without hard numeric limits. The source inventory remains useful.

**Second-pass update:** additional Jev and autoformalization papers were found after this inventory was drafted. Read [NOVELTY_SECOND_PASS.md](NOVELTY_SECOND_PASS.md) for the additions and the stricter decision: the broad proposed pipeline is not cleared as a novel contribution. The count below describes the initial inventory only.

This is a targeted review of discoverable Jev work and its closest methodological precedents. It is not an exhaustive systematic review. “Full-text sections” means the available HTML/paper was inspected for methods, results, and limitations; it does not mean every appendix, bibliography item, or line of a linked repository was read. “Abstract” means only the paper record/abstract was checked. Repository inspection concerns documentation and selected relevant files, not a completed code audit or successful execution.

No benchmark result in these sources has been independently reproduced during this planning session. Model-card numbers are author reports. Links were consulted through browser tools; not every linked download was accessible. The full experiment, exact artifact revisions, and final novelty check remain future work.

## 1. Search scope and credibility rules

Searches covered arXiv Jev/System One papers; official TypeSafe documentation; GitHub paper catalogues and evaluation repositories; Hugging Face decision-model cards and Spaces; Jev judging, calibration, semantic parsing, symbolic reasoning, uncertainty over formalizations, and answer-equivalence active learning. Representative queries included `Jev model arxiv benchmark`, `Jev as a judge confidence`, `Open-Jev Hugging Face`, `Jev calibration composition`, `semantic parsing solver uncertainty`, and `Equivalence Class Determination`.

Primary papers, author repositories, official provider documentation, and actual model cards carry the evidence. Medium articles are context. Search snippets, reseller pages, SEO mirrors, and leaderboard rows with unmatched conditions do not establish performance or novelty. The [awesome-jev-papers catalogue](https://github.com/linggm3/awesome-jev-papers) aided discovery but had a dated cutoff and is not a complete bibliography.

## 2. Jev-specific papers found

Titles below are shortened for readability where necessary; the linked arXiv record controls exact bibliographic metadata.

| Record | Inspection | Finding relevant to the plan |
|---|---|---|
| [Evaluating and Benchmarking the System One Model Jev — 2609.37647](https://arxiv.org/abs/2609.37647) | Full-text sections | Broad multi-dataset low-cost evaluation. The work reports 37 datasets and 346,009 requests, but comparison conditions and contamination limits do not establish universal frontier superiority. |
| [JEV-as-a-Judge: Accept When Confident, Escalate When Unsure — 2609.26550](https://arxiv.org/abs/2609.26550) | Full-text sections | Confidence escalation is already tested across judge tasks. Retaining nearly all a comparator's accuracy is different from near-perfect absolute accuracy. |
| [Jev vs LLMs as Rubric Judges: Cheaper, Faster, and Wrong in the Same Places — 2609.29769](https://arxiv.org/abs/2609.29769) | Full-text sections | Confident correlated errors undermine simple cascade optimism. Error overlap must be measured with gold labels, not agreement alone. |
| [Same Scores, Different Decisions: Legal Document Understanding — 2609.27678](https://arxiv.org/abs/2609.27678) | Full-text sections | Similar aggregate scores can mask different decisions and stability. Cheap inference does not imply best accuracy on ContractNLI. |
| [Code Owns the Simulation, Jev Owns the Evaluation — 2610.01834](https://arxiv.org/abs/2610.01834) | Full-text sections | Explicitly separates executable simulation from semantic evaluation. Broad “Jev plus code” novelty is unavailable. |
| [NumericJev — 2609.28587](https://arxiv.org/abs/2609.28587) | Full-text sections | Numeric values can be reconstructed through finite choices without model training. Range-choice decoding is already a research direction. |
| [Jev in the Wild — 2609.30216](https://arxiv.org/abs/2609.30216) | Full-text sections | GitHub ecosystem study; adoption counts do not establish benchmark quality or correctness. |
| [JevSpawn — 2610.00437](https://arxiv.org/abs/2610.00437) | Full-text sections | Compositional action proposals and feedback-driven execution are already explored. |
| [Jev for Scientific Decisions — 2609.24965](https://arxiv.org/abs/2609.24965) | Full-text sections, revised record | Small structured scientific-decision study. Intermediate semantic errors can cancel in final outcomes; decomposition needs direct inspection. |
| [Decision Models for Text Annotation in Computational Social Science — 2609.24574](https://arxiv.org/abs/2609.24574) | Full-text sections, revised record | Substantial cost savings coexist with task-dependent quality deficits and unreliable confidence on some tasks. Cheapest does not mean strongest. |
| [this-that-model-1.0 — 2609.23886](https://arxiv.org/abs/2609.23886) | Abstract | Typed small-model, one-pass decisions; a relevant open-model precedent requiring a deeper implementation comparison. |
| [JEVQA — 2609.24395](https://arxiv.org/abs/2609.24395) | Abstract | Video-question-answering application based on textual/metadata representation; not a main reasoning baseline. |
| [Crash-narrative structured assessment — 2609.24052](https://arxiv.org/abs/2609.24052) | Abstract | Structured extraction application. Does not by itself establish a new uncertainty-composition method. |
| [Jev-Mem — 2609.23986](https://arxiv.org/abs/2609.23986) | Abstract | Memory-control use of decision models; avoid presenting Jev memory routing as untouched. |
| [Open-Jev on CallScreenBench — 2609.23959](https://arxiv.org/abs/2609.23959) | Abstract | Independent open decision-model evaluation; licensing and architecture remain separate from hosted Jev. |
| [Fast intent-driven service orchestration — 2609.23136](https://arxiv.org/abs/2609.23136) | Abstract | Networking/orchestration application. Relevance is contextual, not evidence for the proposed method. |
| [Replacing LLMs with Jev in edge orchestration — 2609.22753](https://arxiv.org/abs/2609.22753) | Abstract | Edge decision/orchestration application; cheaper orchestration is already explored. |

Ten records received full-text-section inspection and seven were screened at abstract level. The seven abstract-only papers must be read in full if they become close prior work for a final claim. Version changes and later publications can invalidate this inventory.

Selected author artifacts: [broad benchmarking code](https://github.com/AppliedMachineLearning-Lab/jev-benchmarking), [benchmarking data archive](https://doi.org/10.5281/zenodo.23039006), [legal evaluation repository](https://github.com/ZF-Utokyo/Jev-Benchmark), [NumericJev code](https://github.com/Bring-AI/jev-numeric), and [Jev-as-a-judge repository](https://github.com/danielgshea/jev-as-a-judge). Documentation/artifact availability was checked; experiments were not run.

## 3. GitHub and engineering evidence

| Source | Inspection and implication |
|---|---|
| [Deferred crispification / BSF-S1](https://github.com/dnakhoa/jev-deferred-crispification) | README and relevant position-paper text inspected. Vagueness, noncompositional calibration, and deferred discrete decisions are already explicit Jev critiques. |
| [Jev does not play dice](https://github.com/KantaHayashiAI/jev-does-not-play-dice) | README and methods inspected. Probability elicitation and overconfidence experiments already exist; Choice output is not automatically a faithful probability. |
| [Typed evals](https://github.com/TrustifAI/typed_evals) | Framework documentation inspected. Typed evaluation infrastructure and calibration are not new by themselves. |
| [Reward-model evaluation](https://github.com/goya4140/jev-reward-model-evaluation) | README and phase-two plan inspected. Reports large inexpensive runs across several reward/judge benchmarks. Historical leaderboard comparisons need paired reruns under matching prompts, scorers, and versions. |
| [Laya](https://github.com/NandhaKishorM/laya) | Repository documentation inspected. Independent non-generative decision infrastructure, not the official hosted model's implementation. |
| [LangChain Jev evaluation article](https://www.langchain.com/blog/jev-agent-evals-langsmith) | Engineering study inspected. Its repeated small example set supports a narrow repeatability analysis; repeated decisions are not hundreds of independent evaluation items. |

## 4. Closest methodological precedents

| Source | Inspection | Why it constrains novelty |
|---|---|---|
| [Logic-LM — 2305.12295](https://arxiv.org/abs/2305.12295) | Full-text sections and [repository documentation](https://github.com/teacherpeterpan/Logic-LLM) | Generated formalizations, symbolic solving, and refinement already exist. Public fixed evaluation panels provide practical paired benchmarks. |
| [LINC — 2310.15164](https://arxiv.org/abs/2310.15164) | Full-text sections and [repository](https://github.com/benlipkin/linc) | Semantic parsing plus theorem proving; parsing remains a failure source. Its reported filtering/sampling must not be mistaken for full official evaluation. |
| [Logic-LM++ — 2407.02514](https://arxiv.org/abs/2407.02514) | Paper record | Refinement of generated formalizations is prior work; deeper inspection required if refinement is claimed as new. |
| [Grammars of Formal Uncertainty — 2505.20047](https://arxiv.org/abs/2505.20047) | Full-text sections | Distributions over formal translations and uncertainty for selective verification are directly adjacent. Non-generative finite choices must show a distinct benefit. |
| [FSLI — 2502.08415](https://arxiv.org/abs/2502.08415) | Paper record | Deterministic semantic systems can solve ordering tasks. A small model beating a frontier on easily parsed templates may be a trivial result. |
| [DeepProbLog — NeurIPS 2018](https://proceedings.neurips.cc/paper/2018/hash/dc5d637ed5e62c36ecb73b654b05ba2a-Abstract.html) | Original proceedings abstract | Neural predicates within probabilistic logic already combine finite perception decisions and symbolic inference. |
| [NeurASP — IJCAI 2020](https://www.ijcai.org/proceedings/2020/243) | Original proceedings abstract | Neural outputs over atomic facts plus answer-set constraints are close precedents for scoring semantic alternatives. |
| [DeepStochLog — AAAI 2022](https://ojs.aaai.org/index.php/AAAI/article/view/21248) | Original proceedings abstract | Neural stochastic grammars and efficient logic inference constrain claims about packed non-generative semantic reasoning. |
| [Near-Optimal Bayesian Active Learning / EC² — 1010.3091](https://arxiv.org/abs/1010.3091) | Abstract and original-paper material | Equivalence-class identification and cost-aware query selection are established. “Only ask questions that change the answer” is not a new theoretical principle. |
| [Correlated and noisy tests / ECED](https://yuxinchen.org/files/papers/chen17eced-long.pdf) | Abstract and formulation/theory sections | Classical analysis already handles important noisy-test dependencies under stated assumptions. Unknown shared neural-model errors are not automatically covered by those assumptions. |
| [Selectively Answering Ambiguous Questions](https://aclanthology.org/2023.emnlp-main.35/) | Paper record | Ambiguity-aware selective answering already exists beyond formal-program pipelines. |
| [Reasoning about Intent for Ambiguous Requests — 2511.10453](https://arxiv.org/abs/2511.10453) | Abstract | Multiple interpretations paired with different answers are already a research direction. |
| [Conformal prediction introduction — 2107.07511](https://arxiv.org/abs/2107.07511) | Paper record; established methodology | Marginal prediction-set coverage is an established tool, not a new theorem for this paper. |
| [Learn Then Test — 2110.01052](https://arxiv.org/abs/2110.01052) | Full-text sections | Valid policy/risk certification must account for selection; do not tune thresholds on the certification sample. |

The proposed method must outperform strong adaptations of the closest applicable precedents. A simple product of slot scores, a solver, and EC² is not sufficient novelty. The credible open question concerns practical finite decision interfaces, packed answer distinctions, candidate/search failure accounting, and whether those choices produce a reproducible improvement on real language.

## 5. Additional judging/reliability work screened

These sources informed rejection of a generic judge-cascade project. Not every appendix was inspected.

| Source | Relevant established direction |
|---|---|
| [Multi-expert conformal pairwise judging — 2608.26529](https://arxiv.org/abs/2608.26529) | Conformal risk control with heterogeneous judges. Full-text sections inspected. |
| [LLM-as-a-Judge on a Budget — 2602.15481](https://arxiv.org/abs/2602.15481) | Adaptive allocation of evaluation effort. Full-text sections inspected. |
| [Efficient inference with noisy judges — 2601.05420](https://arxiv.org/abs/2601.05420) | Statistical inference under judge measurement errors. Full-text sections inspected. |
| [Rubric artifacts in judging — 2609.02942](https://arxiv.org/abs/2609.02942) | Rubric/response manipulations expose judge failures. Paper screened. |
| [Rethinking atomic decomposition — 2603.28005](https://arxiv.org/abs/2603.28005) | Decomposition is not uniformly superior to a strong holistic prompt. Paper screened. |
| [TrustJudge — 2509.21117](https://arxiv.org/abs/2509.21117) | Probability scores and consistency constraints. Paper screened. |
| [Aligning with Logic — 2410.02205](https://arxiv.org/abs/2410.02205) | Logical consistency repairs for judges. Paper screened. |
| [Correlated judge consensus — 2609.22512](https://arxiv.org/abs/2609.22512) | Agreement can coexist with shared failures. Paper screened. |
| [Dependence-aware label aggregation — 2601.22336](https://arxiv.org/abs/2601.22336) | Accounting for dependence in label combination. Paper screened. |
| [Correlated Errors in Large Language Models — ICML 2025](https://proceedings.mlr.press/v267/kim25e.html) | Independent model names do not imply independent mistakes. Primary conference source screened. |
| [Incoherent probability judgments — 2401.16646](https://arxiv.org/abs/2401.16646) | Probability coherence is already a known issue. Paper screened. |
| [MiniCheck — 2404.10774](https://arxiv.org/abs/2404.10774) | Small specialized evaluators can match expensive judges at much lower cost; the broad cheap-evaluator claim is old. Primary paper screened. |

## 6. Model cards, documentation, and budget sources

| Source | Verified fact and remaining uncertainty |
|---|---|
| [TypeSafe introduction](https://docs.typesafe.ai/introduction) | Native typed decisions and compositional application interface. Vendor descriptions are not independent calibration evidence. |
| [TypeSafe models](https://docs.typesafe.ai/models) | Current versioned ID and token pricing were checked. Pin the resolved ID; aliases and service limits can change. No official checkpoint download was established. |
| [TypeSafe jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13) | Vendor acknowledges task-specific weaknesses. Test numeric/scope/order behavior directly. |
| [TypeSafe quickstart](https://docs.typesafe.ai/introduction/quickstart) | Official account/playground route. Universal free credits were not established. |
| [AutoTrust JEV-9B](https://huggingface.co/autotrust/JEV-9B) | Independent teacher-distilled decision checkpoint, Apache 2.0 card, custom head/runtime. Teacher agreement does not prove gold-task accuracy. |
| [AutoTrust JEV-27B](https://huggingface.co/autotrust/JEV-27B) | Larger open-family option; unnecessary first-pilot expense. |
| [Open-Jev-9B](https://huggingface.co/ZefanCai/Open-Jev-9B) | Adapter/head implementation requiring the declared base revision and loader. Separate from official weights. |
| [Open-Jev-27B-v1.1](https://huggingface.co/ZefanCai/Open-Jev-27B-v1.1) | Larger implementation; model-card evaluation and data provenance require contamination review. |
| [Plumb-4B](https://huggingface.co/crh225/plumb-4b) | Finite-option model with independent training/evaluation recipe. Raw logits versus benchmark-specific probability transforms must be separated. |
| [Plumb GGUF](https://huggingface.co/crh225/plumb-4b-GGUF) | Quantized local variant. Smaller files do not establish unchanged calibration. |
| [Plumb MLX conversion](https://huggingface.co/CogniSoft/Plumb-4B-MLX-8bit) | Apple-silicon conversion option. Verify your device's memory/runtime; the card is not a frontier comparison. |
| [OpenAI model catalogue](https://developers.openai.com/api/docs/models) | Current capability comparator selected from official documentation, not assumed from an old benchmark. |
| [OpenAI pricing](https://developers.openai.com/api/docs/pricing) | Standard versus batch/other modes differ. Recheck rates and actual billable usage before paid execution. |
| [Claude model catalogue](https://platform.claude.com/docs/en/models/overview) | Current demanding-reasoning comparator and published pricing checked; exact account availability/snapshot must be confirmed. |
| [RunPod pricing](https://www.runpod.io/pricing) | Dedicated Pod prices and storage are separate from Serverless prices. Listed prices are not guarantees of available capacity. |

## 7. Benchmark sources

| Source | Protocol requirement |
|---|---|
| [FOLIO original paper](https://arxiv.org/abs/2209.00840), [repository](https://github.com/Yale-LILY/FOLIO), [dataset](https://huggingface.co/datasets/yale-nlp/FOLIO) | Versioned data can differ. Gold logical forms, labels, and proof metadata are forbidden inference inputs. Call the 204-item public split by its actual upstream identity. |
| [ProofWriter](https://arxiv.org/abs/2012.13048) | Preserve open-world and explicit-negation semantics. The 600-item published panel is not the full test set. The original landing-page download was inaccessible during this review. |
| [PrOntoQA](https://github.com/asaparov/prontoqa) | Original generator and OOD data support controlled tests. A deterministic grammar parser is mandatory because the language is templated. |
| [JudgeBench paper](https://arxiv.org/abs/2410.12784), [code](https://github.com/ScalerLab/JudgeBench), [data](https://huggingface.co/datasets/ScalerLab/JudgeBench) | Keep original panels, labels, and ordering protocol. Only a complete matched run supports a full-panel claim. |
| [LLM-AggreFact](https://huggingface.co/datasets/lytang/LLM-AggreFact) | Potential later evaluation domain, already used by specialized cheap evaluators; not selected for the first study. |

## 8. Medium and reference-paper inspection

[Who Evaluates the Evaluator?](https://medium.com/gradient-growth/who-evaluates-the-evaluator-be5d96a74522) was accessible and read for its evaluation/calibration context. It is an author blog, not the main evidence for novelty or superiority. A search-surfaced Medium Jev-versus-judge article could not be verified in full and was not treated as read or relied on for a technical claim. Medium coverage is therefore partial, explicitly so.

The user-provided [AgentFoundry PDF](https://github.com/arghya05/agent-foundry/blob/main/research-paper/AgentFoundry_Paper.pdf) was inspected using the available local copy at `/Users/arghyamukherjee/Documents/agents_framework/agent-foundry/research-paper/AgentFoundry_Paper.pdf`. All 27 pages were text-extracted, with the main formal/method/evaluation and evidence sections inspected. Its SHA-256 is `a005aa5ed018b8cd245e3a648bf0b25f22c20d8063416871c5bc6c36b5d0b457`. The extraction is [agentfoundry-reference.txt](agentfoundry-reference.txt).

The current remote PDF download did not succeed in this environment, so the local copy's identity with current GitHub bytes was not verified. No results from that paper are transferred into this proposal. Its careful baselines, scope limits, evidence manifests, and cost records are the relevant quality model.

## 9. Final novelty verdict and work still needed

**Updated verdict: novelty gate not passed; no paid pilot yet.** The second-pass review adds semantic-fidelity auditing and probe-budget methods that overlap further components. The proposal may be an application of existing semantic uncertainty, neural logic, fingerprint checking, and EC²-style decision resolution. Resolve the claim matrix before a pilot. The final paper needs a material algorithmic/statistical advance or substantial independently validated empirical contribution beyond those adaptations.

Before making a first/novel/foundational claim: read the closest formal-uncertainty, neural-logic, and active-testing papers completely; trace their references and citing papers; check newly posted Jev work; compare executable algorithms rather than abstracts; and write a claim-by-claim overlap table against each closest work. Have another researcher review that table if available. This final check is a scientific task, not an approval gate imposed by a tool.

Nothing in this audit establishes that the proposed system beats Claude/OpenAI, that a public leaderboard will accept its configuration, or that NeurIPS will accept the paper. Those require results and conference review.
