# Systematic literature review before submission (October 2026)

Date of all searches: **2026-10-10**. Reviewer: automated desk review (web search + fetch of abstract/HTML pages). No result was reproduced. "Verified" means the record (title, authors, ID) was confirmed on arXiv, a proceedings page, or the project page; finer claims marked *(abstract)* come from abstracts or search snippets only, and *(full text)* means the HTML body was queried for the specific question. **This document does not certify novelty.** A failed search is not evidence of absence.

Inputs read first: `research-paper/sec_abstract.tex`, `sec_intro.tex`, `sec_related.tex`, `refs.bib`, `numbers.tex`, `research/EMPIRICAL_NOVELTY_DECISION.md` (and the head of `LITERATURE_AUDIT.md`).

Contributions under review (numbering used below):
1. Matched, cost-accounted JEV-9B (one-pass) vs reasoning-enabled GPT-6 Astra / Claude Fable 5.1 (high effort).
2. Same-weights control: backbone with thinking closes most of the gap (computation, not knowledge).
3. Controlled dependency panel (length/rules/distractors fixed): depth did not drive one-pass errors; errors concentrate on "Unknown" and instability under meaning-preserving edits.
4. JEV-H: both-order (position) debiasing + calibrated confidence gate escalating to the same model's reasoning mode; best on RewardBench at 6–35x lower cost.
5. Pre-call feature router vs confidence gate, leave-one-family-out.
6. ProofWriter distribution-level bridge: student diverges from teacher at depth.

## 1. Search log (2026-10-10)

| # | Query family | Query (abridged) | Relevant hits |
|---|---|---|---|
| 1 | Position bias | LLM-as-a-judge position bias swap order debiasing | 4 (survey 2412.05579, FairJudge, Shi et al., Wang et al.) |
| 2 | Position bias | Judging the Judges systematic study position bias | 1 (Shi et al.) |
| 3 | Position bias | Large Language Models are not Fair Evaluators balanced position calibration | 1 (Wang et al.) |
| 4 | Position bias | Judging LLM-as-a-judge MT-Bench swap positions | 1 (Zheng et al. 2023) |
| 5 | Position bias | LLMs Are Not Robust Multiple Choice Selectors PriDe permutation | 1 (Zheng et al. 2024) |
| 6 | Position bias | CalibraEval position bias calibration label-free | 1 |
| 7 | Position bias / escalation | position inconsistency as uncertainty signal, escalate | 2 (2604.15302 conformal sets; 2601.07006) |
| 8 | Small judges / cascades | Trust or Escalate provable guarantees cascaded selective evaluation | 1 (Jung et al. ICLR 2025) |
| 9 | Small judges / cascades | judge cascade small judge escalate large judge confidence cost | 3 (Trust or Escalate, JEV-as-a-Judge, practitioner) |
| 10 | Small judges | Prometheus 2 / JudgeLM / PandaLM fine-tuned judges | 3 |
| 11 | Small judges / cascades | cost-efficient LLM evaluation cascade cheap judge fallback 2026 | 3 (PAJAMA 2607.22561, Xu et al. NeurIPS 2025) |
| 12 | Small judges | Replacing Judges with Juries PoLL cost | 1 |
| 13 | RewardBench | RewardBench generative judges refusal safety | 2 (RewardBench, RewardBench 2) |
| 14 | RewardBench / reasoning judges | reasoning reward model RewardBench JudgeLRM RM-R1 | 3 (RM-R1, ReasonGRM, Think Twice) |
| 15 | Reasoning judges | thinking LLM judge reasoning improves judge JudgeBench | 5 (JudgeBench, 2509.13332, J1, CodeJudgeBench, RACER 2605.10805) |
| 16 | Reasoning judges | thinking budget effect on judge accuracy reasoning effort 2026 | 3 (RACER, proof grading 2608.00004, test-time compute 2604.10739) |
| 17 | Refusal effects | LLM judge refusal safety prompts refuses to evaluate | 0 direct (only moderation-bias work 2505.15365) |
| 18 | Same-model thinking | same model thinking vs non-thinking adaptive thinking | 3 (AdaptThink, 2602.22556, survey 2507.09662) |
| 19 | Same-model thinking | s1 budget forcing | 1 |
| 20 | Same-model thinking | Qwen3 technical report thinking/non-thinking budget | 1 |
| 21 | Same-model thinking | To CoT or not to CoT | 1 |
| 22 | Same-model escalation | self-escalation cascade same model reasoning mode switch confidence | 4 (ThinkSwitcher, 2510.21007, Gold-Switch, ThinkRouter) |
| 23 | Cascades | When does confidence-based cascade deferral suffice | 1 (Jitkrittum et al.) |
| 24 | Cascades | AutoMix self-verification cascade | 1 |
| 25 | Cascades | LLM cascades mixture of thoughts answer consistency | 1 (Yue et al.) |
| 26 | Selective prediction | selective classification Geifman El-Yaniv | 1 |
| 27 | Calibration of judges | calibration of LLM judges confidence 2025 | 4 (2508.06225, 2509.18658, 2511.21140, 2608.17994) |
| 28 | Calibration of judges | Judge, Retrieve, or Abstain | 2 (2608.17994, SCOPE 2602.13110) |
| 29 | Decision models | JEV-9B decision model judge harness thinking escalation 2026 (extended) | 5 (JevOut, Jev in the Wild, AIM-Decision, Jeeves, rubric-judges) |
| 30 | Decision models | JEV-as-a-Judge Li Miao Krishnan Padman | 1 (+ full-text query) |
| 31 | Decision models | General Decision Models 2610.03935 (full-text queries) | 1 |
| 32 | Decision models | Hard-Decisions project page (fetched) | 1 |
| 33 | Depth / length | Unknown label closed-world open-world ProofWriter FOLIO | 2 (LAMBADA reporting, Logical Phase Transitions) |
| 34 | Depth / length | controlled reasoning depth controlling input length confound | 4 (FLenQA, QMFOL, LongReason, AAAI depth framework) |
| 35 | Depth / length | FLenQA Same Task More Tokens | 1 |
| 36 | Depth / length | QMFOL 2606.20227 | 1 |
| 37 | Depth / length | Logical Phase Transitions 2601.02902 | 1 |
| 38 | Depth / thinking | PrOntoQA/FOLIO/ProofWriter same-model thinking toggle | 0 direct (only CoT-prompting comparisons) |
| 39 | Meaning-preserving edits | premise order paraphrase consistency deduction | 1 (Premise Order Matters) |
| 40 | Cost-aware evaluation | Cost-of-Pass economic framework | 1 |
| 41 | Cost-aware evaluation | AI Agents That Matter cost-controlled | 1 |
| 42 | Cost / break-even | small classifier vs LLM break-even analysis | 1 (Pecher et al. EMNLP 2025) |
| 43 | Routing generalization | router unseen tasks leave-one-out confidence baseline | 2 (bandit routing 2510.07429; zero-shot routing 2601.06220) |
| 44 | Distillation fidelity | Does knowledge distillation really work / small models struggle | 2 |
| 45 | Benchmarks | HaluEval | 1 |

## 2. Relevant papers found

Overlap columns: N = none, P = partial, S = strong. "In refs.bib" marks whether the current bibliography already has it.

| Title (short) | Year / venue | URL | One-line finding | 1 | 2 | 3 | 4 | 5 | 6 | In refs? |
|---|---|---|---|---|---|---|---|---|---|---|
| **JEV-as-a-Judge: Accept When Confident, Escalate When Unsure** (Li, Miao, Krishnan, Padman) | arXiv 2609.26550, v4 6 Oct 2026 | https://arxiv.org/abs/2609.26550 | *(full text)* RewardBench (1,500 pairs) + JudgeBench; Jev judged **in both orders with averaged aligned probabilities**; confidence cascade Jev→GPT-6 Astra (low effort) reaches 93.7 vs 92.4 on held-out RewardBench at ~27% of GPT-6 fee; Jev 78.6 vs 93.1 on JudgeBench | S | N | N | **S** | P | N | yes (title/authors incomplete) |
| **Reasoning Is Not Free: RACER, cost-efficient routing for LLM-as-a-Judge** (Zhang, Zhang, Xiang, Cai) | ICML 2026; arXiv 2605.10805 | https://arxiv.org/abs/2605.10805 | *(full text)* Routes between **thinking and non-thinking modes of the same Qwen3 model** (1.7B/4B/8B) on **JudgeBench, RewardBench, RewardBench 2**; reasoning helps on math/code, little or negative elsewhere; matches All-Reasoning at ~half cost. No position-swap, no confidence-gate baseline | P | **S** | N | **S** | P | N | no |
| Explicit Reasoning Makes Better Judges (Jayarao et al.) | NeurIPS 2025 FoRLM workshop; arXiv 2509.13332 | https://arxiv.org/abs/2509.13332 | Same Qwen3 models thinking vs non-thinking on RewardBench: ~10 pts better, <2x FLOPs, more robust to positional and other biases | N | **S** | N | P | N | N | no |
| Can Confidence Estimates Decide When CoT Is Necessary? (Lewis-Lim et al.) | arXiv 2510.21007 (v3 Jan 2026) | https://arxiv.org/abs/2510.21007 | *(full text)* Same-model confidence-gated CoT on Qwen3 thinking toggle, GPT-OSS, GPT-5.1; gating beats random only for some models; AUROC predicts gating success better than ECE | N | P | N | **S** | P | N | no |
| ThinkSwitcher (Liang et al.) | arXiv 2505.14183 | https://arxiv.org/abs/2505.14183 | One model switches short/long reasoning with a learned switcher; 20–30% compute saving | N | P | N | P | P | N | no |
| AdaptThink (Zhang et al.) | EMNLP 2025; arXiv 2505.13417 | https://arxiv.org/abs/2505.13417 | RL teaches a reasoning model when to skip thinking | N | P | N | P | N | N | no |
| Qwen3 Technical Report | arXiv 2505.09388 | https://arxiv.org/abs/2505.09388 | Unified thinking/non-thinking modes and thinking budget in one model | N | P | N | P | N | N | no |
| s1: Simple test-time scaling (Muennighoff et al.) | EMNLP 2025; arXiv 2501.19393 | https://arxiv.org/abs/2501.19393 | Budget forcing; more thinking tokens → higher accuracy | N | P | N | N | N | N | no |
| To CoT or not to CoT (Sprague et al.) | ICLR 2025; arXiv 2409.12183 | https://arxiv.org/abs/2409.12183 | CoT helps mainly on math/symbolic (logic) tasks; selective CoT saves cost | N | P | N | P | N | N | no |
| General Decision Models (Duan et al.) | arXiv 2610.03935 | https://arxiv.org/abs/2610.03935 | *(full text)* Compares distilled readout with **its backbone in thinking mode** (Qwen3.8-27B xhigh); InnerJev-27B trails thinking backbone by ~29 pts on GPQA; option-order shuffling in data | P | **S** | N | N | N | P | yes |
| Trust or Escalate (Jung, Brahman, Choi) | ICLR 2025; arXiv 2407.18370 | https://arxiv.org/abs/2407.18370 | *(full text)* Cascaded selective evaluation Mistral-7B→GPT-3.5→GPT-4 with calibrated thresholds and human-agreement guarantee; different models per stage; no position swap | N | N | N | **S** | P | N | no |
| Ask a Strong LLM Judge when Your RM is Uncertain (Xu et al.) | NeurIPS 2025; arXiv 2510.20369 | https://arxiv.org/abs/2510.20369 | Uncertainty-routed RM→LLM-judge; beats random calling at equal cost on RM benchmarks | N | N | N | **S** | P | N | no |
| Judge, Retrieve, or Abstain (Badshah, Emami, Sajjad) | arXiv 2608.17994 | https://arxiv.org/abs/2608.17994 | Calibrated uncertainty thresholds with risk guarantees; escalate to retrieval mode, then abstain | N | N | N | P | N | N | no |
| PAJAMA / Codifying the Judge | arXiv 2607.22561 | https://arxiv.org/abs/2607.22561 | Program judges with calibrated aggregation, uncertain cases routed to LLM fallback; Pareto cost/accuracy | P | N | N | P | N | N | no |
| Judging LLM-as-a-Judge with MT-Bench (Zheng et al.) | NeurIPS 2023 D&B; arXiv 2306.05685 | https://arxiv.org/abs/2306.05685 | Defines position bias; swap-both-orders, count inconsistent as tie | N | N | N | P | N | N | no |
| LLMs are not Fair Evaluators (Wang et al.) | ACL 2024; arXiv 2305.17926 | https://arxiv.org/abs/2305.17926 | **Balanced Position Calibration**: score both orders and average | N | N | N | **S** (debias part) | N | N | no |
| Judging the Judges: position bias (Shi et al.) | IJCNLP-AACL 2025; arXiv 2406.07791 | https://arxiv.org/abs/2406.07791 | 15 judges, 150k instances; position bias depends on quality gap | N | N | N | P | N | N | no |
| LLMs Are Not Robust Multiple Choice Selectors / PriDe (Zheng et al.) | ICLR 2024; arXiv 2309.03882 | https://arxiv.org/abs/2309.03882 | Option-ID selection bias; permutation-based debiasing | N | N | N | P | N | N | no |
| CalibraEval (Li et al.) | ACL 2025; arXiv 2410.15393 | https://arxiv.org/abs/2410.15393 | Label-free calibration of judge prediction distribution against position bias | N | N | N | P | N | N | no |
| FairJudge | ICML 2026; arXiv 2602.06625 | https://arxiv.org/abs/2602.06625 | Trained debiased/consistent judge | N | N | N | P | N | N | no |
| Prometheus 2 (Kim et al.) | EMNLP 2024; arXiv 2405.01535 | https://arxiv.org/abs/2405.01535 | Open 7B/8x7B evaluator close to GPT-4 | P | N | N | P | N | N | no |
| JudgeLM (Zhu et al.) | ICLR 2025; arXiv 2310.17631 | https://arxiv.org/abs/2310.17631 | Fine-tuned judges; swap augmentation against position bias | P | N | N | P | N | N | no |
| Replacing Judges with Juries / PoLL (Verga et al.) | arXiv 2404.18796 | https://arxiv.org/abs/2404.18796 | Panel of small judges beats GPT-4 judge at 7–8x lower cost | P | N | N | P | N | N | no |
| RewardBench (Lambert et al.) | arXiv 2403.13787 | https://arxiv.org/abs/2403.13787 | The benchmark used; Safety subsets reward refusing *and* reward answering (XSTest-should-respond) | P | N | N | P | N | N | **no (benchmark used but uncited)** |
| RewardBench 2 (Malik et al.) | arXiv 2506.01937 | https://arxiv.org/abs/2506.01937 | Harder successor; generative judges lack granularity | N | N | N | P | N | N | no |
| RM-R1 (Chen et al.) | ICLR 2026; arXiv 2505.02387 | https://arxiv.org/abs/2505.02387 | Reasoning reward models; strong RewardBench | N | P | N | P | N | N | no |
| JudgeBench (Tan et al.) | ICLR 2025; arXiv 2410.12784 | https://arxiv.org/abs/2410.12784 | o3-mini accuracy rises with reasoning effort (70.6→80.9) | P | P | N | N | N | N | yes |
| JEV vs LLMs as Rubric Judges: Cheaper, Faster, Wrong in Same Places | arXiv 2609.29769 | https://arxiv.org/abs/2609.29769 | Correlated errors limit cascades | P | N | N | P | P | N | yes |
| JevOut: Natural Context Can Flip Decision Models (Xu et al.) | arXiv 2609.30243, v2 8 Oct 2026 | https://arxiv.org/abs/2609.30243 | Short natural, answer-preserving context flips 61–73% of correct decisions across 4 decision systems | N | N | **P/S** (instability) | N | N | N | no |
| AIM-Decision: Jev vs Kev vs LLMs (AIMultiple) | web article, 5–9 Oct 2026 | https://aimultiple.com/decision-models | 22 decision models vs GPT-6 Astra (low effort) on classification + browser tasks with per-task cost | P | N | N | N | N | N | no (grey lit.) |
| Jev in the Wild (Ling et al.) | arXiv 2609.30216 | https://arxiv.org/abs/2609.30216 | 2,170 GitHub projects; Jev used for routing/judging | P | N | N | N | P | N | no (in audit) |
| Hard-Decisions (Anthus AI) | project page, results 2026-10-09 | https://hard-decisions.anth.us/ | ProofWriter depth 0–5; official Jev **Unknown recall 74.2%**, Kev-9B 68.1%; length covaries with depth; Luna reasoning off | P | N | **S** (Unknown) | N | N | **S** | yes |
| QMFOL (Zheng et al.) | arXiv 2606.20227 | https://arxiv.org/abs/2606.20227 | Controlled depth/width/label/distractors; **False/Unknown harder than True** | N | N | **S** (Unknown) | N | N | P | yes |
| Reasoning Models Lose their Way with Long Deduction (ProloNg) | ICML 2026 | https://icml.cc/virtual/2026/82459 | Frontier reasoning fails beyond depth ~10; length grows with depth | N | N | P | N | N | N | yes |
| Same Task, More Tokens / FLenQA (Levy, Jacoby, Goldberg) | ACL 2024; arXiv 2402.14848 | https://arxiv.org/abs/2402.14848 | Holds reasoning fixed, varies length via padding (incl. simplified RuleTaker): accuracy falls with length | N | N | **P** (length-matching precedent) | N | N | N | no |
| Logical Phase Transitions (Zhang et al.) | ACL 2026; arXiv 2601.02902 | https://arxiv.org/abs/2601.02902 | Accuracy collapses abruptly past a logical-complexity threshold | N | N | P | N | N | N | no |
| Premise Order Matters (Chen et al.) | ICML 2024; arXiv 2402.08939 | https://arxiv.org/abs/2402.08939 | Meaning-preserving premise reordering drops deduction accuracy >30% | N | N | P | N | N | N | no |
| ProofWriter / RuleTaker / PrOntoQA / LogicBench / Multi-LogiEval / FOLIO / ANLI | 2020–2024 | (in refs.bib) | Depth-stratified deduction; Unknown/OWA labels | N | N | P | N | N | P | yes |
| When Does Confidence-Based Cascade Deferral Suffice? (Jitkrittum et al.) | NeurIPS 2023; arXiv 2307.02764 | https://arxiv.org/abs/2307.02764 | Confidence deferral hard to beat; post-hoc deferral wins under specialists, label noise, **distribution shift** | N | N | N | P | **S** | N | no (claimed in text but uncited) |
| Gatekeeper; token-level cascades; FrugalGPT; RouteLLM; RouterEval/Arena; Rerouting | 2023–2025 | (in refs.bib) | Cascades, routers | P | N | N | P | S | N | yes |
| AutoMix (Aggarwal, Madaan et al.) | NeurIPS 2024; arXiv 2310.12963 | https://arxiv.org/abs/2310.12963 | Small-model self-verification decides escalation | N | N | N | P | P | N | no |
| LLM Cascades with Mixture of Thoughts (Yue et al.) | ICLR 2024; arXiv 2310.03094 | https://arxiv.org/abs/2310.03094 | Answer consistency of weak model as escalation signal (~40% cost) | N | N | N | P | P | N | no |
| Learning to Route LLMs from Bandit Feedback | arXiv 2510.07429 | https://arxiv.org/abs/2510.07429 | Full-information routers fail on held-out tasks | N | N | N | N | P | N | no |
| Selective Classification for DNNs (Geifman, El-Yaniv) | NeurIPS 2017; arXiv 1705.08500 | https://arxiv.org/abs/1705.08500 | Risk–coverage selective prediction with confidence threshold | N | N | N | P | P | N | no |
| Calibration of LLM judges: TH-Score/LLM-as-a-Fuser (2508.06225); conformal judge intervals (2509.18658); How to Correctly Report LLM-as-a-Judge (2511.21140) | 2025 | arXiv | Judge confidence is overconfident; calibration/conformal methods | N | N | N | P | N | N | no |
| Cost-of-Pass (Erol et al.) | ICLR 2026; arXiv 2504.13359 | https://arxiv.org/abs/2504.13359 | Expected $ per correct answer; reasoning models cost-effective on hard tasks | **P** | N | N | P | N | N | no |
| AI Agents That Matter (Kapoor et al.) | TMLR 2025; arXiv 2407.01502 | https://arxiv.org/abs/2407.01502 | Cost-controlled, Pareto evaluation | P | N | N | N | N | N | no |
| Comparing specialised small vs general LLMs: break-even labels (Pecher et al.) | EMNLP 2025; arXiv 2402.12819 | https://arxiv.org/abs/2402.12819 | Break-even in labelled samples, not dollars | P | N | N | N | N | N | no |
| Does Knowledge Distillation Really Work? (Stanton et al.) | NeurIPS 2021; arXiv 2106.05945 | https://arxiv.org/abs/2106.05945 | Students have poor fidelity to teachers even when capacity suffices | N | N | N | N | N | P | no |
| Small Models Struggle to Learn from Strong Reasoners (Li et al.) | Findings ACL 2025; arXiv 2502.12143 | https://arxiv.org/abs/2502.12143 | Learnability gap for reasoning distillation | N | P | N | N | N | P | no |
| HaluEval (Li et al.) | EMNLP 2023; arXiv 2305.11747 | https://arxiv.org/abs/2305.11747 | Benchmark used (HaluEval-QA) | N | N | N | N | N | N | **no (benchmark used but uncited)** |

## 3. Per-contribution novelty assessment

### C1. Matched, cost-accounted one-pass DM vs high-effort reasoning frontiers
- **Established:** decision models trail on reasoning (jevbench2026, jevjudge2026, gdm2026); cost-aware evaluation frameworks exist (Cost-of-Pass, AI Agents That Matter); JEV-as-a-Judge and AIM-Decision already report per-decision cost against GPT-6 Astra, but at **low** effort.
- **Plausibly new:** the high-effort frontier configuration, paired/clustered intervals, preregistration, byte-identical inputs, and failures kept in denominators. This is a *methodological rigor* contribution, not a new finding.
- **Soften/cite:** do not present "cheap model is worse on reasoning" as a result. Cite Cost-of-Pass for the cost-per-correct framing. Say "to our knowledge, we did not find prior comparisons at high effort" rather than implying none exist. A reviewer may say: "matched cost comparison with GPT-6 already in JEV-as-a-Judge; only the effort setting changes."

### C2. Same-weights thinking control
- **Established (strong):** same model with thinking vs without (Qwen3 toggle) is a standard comparison: Jayarao et al. (~10 pts on RewardBench, same Qwen3 weights), RACER (Qwen3 modes on RewardBench/JudgeBench), Sprague et al. (CoT helps on logic), JudgeBench (reasoning effort helps judges), and **GDM 2610.03935 already compares a distilled decision readout against its own backbone in thinking mode** (InnerJev-27B vs Qwen3.8-27B xhigh).
- **Plausibly new (narrow):** the triad *distilled one-pass head + its frozen backbone's thinking mode + high-effort frontier* on matched deduction items, with FOLIO numbers. That is an incremental data point.
- **Soften:** "the deficit is computational rather than a lack of knowledge" is an interpretation. The thinking arm differs in more than computation: it lacks the LoRA/decision head, reads out in a different way and decodes from text. Phrase it as "consistent with a computation account". Cite GDM as the closest precedent and say explicitly that GDM made a similar comparison on GPQA. Reviewer risk: "GDM already showed the backbone's thinking mode beats the distilled readout."

### C3. Controlled depth panel; null depth effect; Unknown and edit instability
- **Established:** depth control (ProofWriter, PrOntoQA, QMFOL, ProloNg); length-held-fixed precedents (**FLenQA** varies length with reasoning fixed, which is the converse design and should be cited); **Unknown/False labels being harder (QMFOL)** and **official Jev's weak Unknown recall (Hard-Decisions: 74.2%; Kev-9B 68.1%)**; sensitivity to meaning-preserving edits (Premise Order Matters for LLMs; **JevOut** for decision models specifically: answer-preserving context flips 61–73%).
- **Plausibly new:** holding length, rule count and distractors *jointly* fixed while varying depth for a one-pass DM, and the *null* depth result under that control (a negative result that partly reconciles Hard-Decisions' confounded slope). This is the most defensible empirical novelty, but it rests on a small panel; the paper should report power and its minimum detectable effect.
- **Must cite/soften:** the "Unknown" concentration is *consistent with* QMFOL and Hard-Decisions, not a discovery. The edit-instability finding must cite JevOut and Premise Order Matters. Frontier models score 100% on the panel, so the panel cannot show a depth × model interaction. Say so.

### C4. JEV-H (both-order debiasing + confidence-gated escalation to own reasoning mode)
- **Established (strong, highest reviewer risk):**
  - Both-order averaging is Balanced Position Calibration (Wang et al. 2023/ACL 2024) and is standard (Zheng et al. 2023, PriDe, CalibraEval).
  - **JEV-as-a-Judge (2609.26550) already queries the decision model in both orders, averages aligned probabilities, and escalates low-confidence items on RewardBench and JudgeBench**, beating GPT-6 on held-out RewardBench (93.7 vs 92.4) at ~27% of its fee. The current sec_related.tex mentions confidence escalation but not that it already includes both-order averaging on RewardBench.
  - Calibrated confidence cascades for judges: Trust or Escalate (ICLR 2025), Xu et al. (NeurIPS 2025), Judge-Retrieve-Abstain.
  - **Escalating from non-thinking to thinking mode of the same model:** RACER routes Qwen3 non-thinking↔thinking judges on RewardBench/JudgeBench (ICML 2026); Lewis-Lim et al. gate CoT on the same model's direct-answer confidence; ThinkSwitcher/AdaptThink learn this switch.
- **Plausibly new (narrow):** the specific composition of a distilled *one-pass decision head* gate with escalation to the *frozen backbone's* thinking mode on the same GPU, so that no paid API is needed, evaluated against *high-effort* frontier judges with measured cost. Describe this as an engineering combination of known components ("we combine…"), not a new method. "Parameter-free" holds only if the threshold is not counted; it is calibrated on data, so call it "training-free with one calibrated threshold".
- **Soften:** "the highest accuracy we measured" on RewardBench is statistically tied with Astra, and its margin over Fable comes from refusals. Add RACER and JEV-as-a-Judge cascade numbers as context: JEV-as-a-Judge's Jev→GPT-6 cascade (93.7) is in the same range as JEV-H (94.4) on a different subset. Add a confidence-gated *random-escalation* and an *all-thinking* baseline in the style of RACER, if they are not already present.

### C5. Pre-call feature router vs confidence gate, leave-one-family-out
- **Established:** confidence deferral is hard to beat (Jitkrittum et al. 2023, which is asserted in sec_related.tex but **not cited**); Jitkrittum shows post-hoc rules win only under distribution shift, which is exactly the leave-one-family-out regime. Routers failing on held-out tasks is reported in 2510.07429.
- **Novelty:** low. The negative result is useful as a replication, but the paper should present it as confirming known behaviour.

### C6. ProofWriter student–teacher bridge
- **Established:** students diverge from teachers (Stanton et al. 2021); the JEV-9B card itself reports higher OOD KL and "mirrors the teacher's mistakes on multi-hop"; Hard-Decisions gives official-Jev and Kev-9B depth curves (Kev-9B 89.3→41.2% open-world).
- **Plausibly new:** item-level agreement of a *specific* community student with official Jev, stratified by depth, on Hard-Decisions items. This is a small but useful validity check, not a headline contribution. Credit Hard-Decisions for the teacher answers.

## 4. Items a reviewer could call "already done"
1. **JEV-H ≈ JEV-as-a-Judge cascade + RACER.** The both-order averaging + confidence cascade on RewardBench is in 2609.26550; same-model thinking routing on RewardBench is in 2605.10805. This is the single biggest risk.
2. **Same-weights thinking control** is in GDM (2610.03935), Jayarao et al. (2509.13332) and RACER.
3. **Unknown-label difficulty** is in QMFOL and Hard-Decisions (Jev Unknown recall 74.2%).
4. **Instability under meaning-preserving edits** for decision models is in JevOut (2609.30243).
5. **Confidence gate beats routers** is in Jitkrittum et al. 2023 and the routing literature.
6. **RewardBench and HaluEval are used but not cited** (refs.bib has no entry for either), and the RewardBench Safety refusal effect should cite the RewardBench Safety design (should-refuse vs should-respond subsets). No prior work directly measuring *judge refusals* on RewardBench was found (query 17). That analysis may be a minor novel observation, but it is unverified as such.

## 5. Recommended wording changes
- Abstract/Intro: replace "JEV-H, a parameter-free harness" with "JEV-H, a training-free harness that combines established both-order debiasing~[Wang et al.] with confidence-gated escalation~[Jung et al.; JEV-as-a-Judge] to the model's own reasoning mode~[RACER; Lewis-Lim et al.]".
- Replace "reaches 94.4%, the highest accuracy we measured" with "statistically tied with GPT-6 Astra (and with Fable on answered items)". Keep the refusal caveat in the same sentence.
- C2: replace "the deficit is computational rather than a lack of knowledge" with "consistent with a computational rather than knowledge deficit: the same frozen backbone, reading out through generation with thinking, …"; cite GDM's thinking-backbone comparison.
- C3: "its failures concentrate on items whose answer is that nothing follows, consistent with prior reports for official Jev~[Hard-Decisions] and for reasoning LLMs~[QMFOL]"; "unstable under meaning-preserving edits, as reported for decision models under natural context additions~[JevOut] and for LLMs under premise reordering~[Chen et al.]".
- Related work: add a "LLM-as-a-judge bias, cascades and reasoning judges" paragraph (Zheng 2023, Wang 2023, Shi 2024, Trust or Escalate, Xu 2025, Jayarao 2025, RACER 2026, Lewis-Lim 2025). Update Table 1 with a RACER row (DM ---, RF ---, SW ✓) and an expanded JEV-as-a-Judge row (both-order ✓, cascade ✓, RewardBench ✓).
- Correct the jevjudge2026 entry to the full title "JEV-as-a-Judge: Accept When Confident, Escalate When Unsure" (Li, Miao, Krishnan, Padman), and cite the version used (v4, 6 Oct 2026). The cited numbers have changed across versions.
- Cite Jitkrittum et al. where the text says confidence deferral is "a notoriously strong baseline".

## 6. Limitations of this review
Most 2026 items were checked only at the abstract level or with targeted full-text questions. Hard-Decisions, JEV-as-a-Judge (v4) and JevOut were all revised within the past week and may change again. Grey literature (AIM-Decision) is listed for awareness and should not be cited as peer-reviewed evidence. Searches for "judge refusal effects" and "same-model thinking toggle on FOLIO/ProofWriter" returned no direct prior work, which is not proof that none exists.
