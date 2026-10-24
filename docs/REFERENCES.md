# References and attribution

Bibliography for the oracles in `src/agentest/cases/` and the sample agents in
`src/agentest/samples/`. Every entry below was checked against arXiv, doi.org or
the publisher/standards body (October 2026). Each oracle docstring has an
**Attribution / References** section that says whether the check *applies* a
published method or is an **in-house heuristic** that only uses the reference as
background.

> agentest does not depend on any third-party evaluation framework. The papers are
> cited for ideas only. All checks are deterministic, trace-based Python.

## A. Methods directly applied

| Used in | Reference |
|:--|:--|
| T7-004, T7-007, T7-011, T7-014 (metamorphic relations) | Chen, T. Y., Cheung, S. C., Yiu, S. M. (1998). *Metamorphic Testing: A New Approach for Generating Next Test Cases.* Tech. Rep. HKUST-CS98-01. Republished: [arXiv:2002.12543](https://arxiv.org/abs/2002.12543) |
| T7-007 (name swap), T7-004/T7-011 (language swap) | Garg, S., Perot, V., Limtiaco, N., Taly, A., Chi, E. H., Beutel, A. (2019). *Counterfactual Fairness in Text Classification through Robustness.* AIES 2019. [doi:10.1145/3306618.3317950](https://doi.org/10.1145/3306618.3317950) |
| T1-002 (k runs, zero false completions), T1-003 (TSR over k) | Yao, S., Shinn, N., Razavi, P., Narasimhan, K. (2024). *τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains.* [arXiv:2406.12045](https://arxiv.org/abs/2406.12045) (pass^k repeated-trial reliability) |
| T1-009 (all-or-none batch) | Haerder, T., Reuter, A. (1983). *Principles of transaction-oriented database recovery.* ACM Computing Surveys 15(4). [doi:10.1145/289.291](https://doi.org/10.1145/289.291) (atomicity) |

## B. Conceptual background (checks are in-house heuristics)

| Topic / IDs | Reference |
|:--|:--|
| Terminal postconditions (T1-*, T1-018) | Hoare, C. A. R. (1969). *An axiomatic basis for computer programming.* CACM 12(10). [doi:10.1145/363235.363259](https://doi.org/10.1145/363235.363259) |
| Test oracles; golden/broken design | Barr, E. T., Harman, M., McMinn, P., Shahbaz, M., Yoo, S. (2015). *The Oracle Problem in Software Testing: A Survey.* IEEE TSE 41(5). [doi:10.1109/TSE.2014.2372785](https://doi.org/10.1109/TSE.2014.2372785) |
| DEPENDS_ON ordering (T2-001/009/013, T2-005) | Kahn, A. B. (1962). *Topological sorting of large networks.* CACM 5(11). [doi:10.1145/368996.369025](https://doi.org/10.1145/368996.369025) |
| Least privilege, complete mediation (T1-013, T5-012, T3-002/007/008, T5-011) | Saltzer, J. H., Schroeder, M. D. (1975). *The protection of information in computer systems.* Proc. IEEE 63(9). [doi:10.1109/PROC.1975.9939](https://doi.org/10.1109/PROC.1975.9939) |
| Ambient authority (T3-011) | Hardy, N. (1988). *The Confused Deputy.* ACM SIGOPS OSR 22(4). [doi:10.1145/54289.871709](https://doi.org/10.1145/54289.871709) |
| Single-use tokens (T3-010, T2-003) | RFC 6749 *The OAuth 2.0 Authorization Framework*, §4.1.2. [doi:10.17487/RFC6749](https://doi.org/10.17487/RFC6749) |
| Session TTL (T3-014), verify before disclose (T2-005) | NIST SP 800-63B, §7 Session management. <https://pages.nist.gov/800-63-3/sp800-63b.html> |
| PII regex detection (T5-004, T7-014) | McCallister, Grance, Scarfone (2010). NIST SP 800-122 *Guide to Protecting the Confidentiality of PII.* [doi:10.6028/NIST.SP.800-122](https://doi.org/10.6028/NIST.SP.800-122) |
| Consent withdrawal (T6-004), minimisation (T5-004), erasure context (T1-016) | Regulation (EU) 2016/679 (GDPR), Art. 5(1)(c), 7(3), 17. <https://eur-lex.europa.eu/eli/reg/2016/679/oj> |
| Indirect prompt injection (T4-009, T3-001) | Greshake, K. et al. (2023). *Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection.* AISec '23. [doi:10.1145/3605764.3623985](https://doi.org/10.1145/3605764.3623985) · [arXiv:2302.12173](https://arxiv.org/abs/2302.12173) |
| Excessive agency, sensitive info disclosure | OWASP Top 10 for LLM Applications 2025 (LLM01, LLM02, LLM06). <https://genai.owasp.org/llm-top-10/> |
| Human oversight (T2-004) | Regulation (EU) 2024/1689 (EU AI Act), Art. 14. <https://eur-lex.europa.eu/eli/reg/2024/1689/oj> |
| AI management system controls (T3-006, T3-002, T2-004) | ISO/IEC 42001:2023, Annex A. <https://www.iso.org/standard/81230.html> |
| Risk management (T1-003 tiers, T3-006) | NIST AI 100-1 (2023), *AI RMF 1.0.* [doi:10.6028/NIST.AI.100-1](https://doi.org/10.6028/NIST.AI.100-1) |
| Faithfulness of explanations (T1-018, T6-007, T7-009) | Jacovi, A., Goldberg, Y. (2020). *Towards Faithfully Interpretable NLP Systems: How Should We Define and Evaluate Faithfulness?* ACL 2020. [doi:10.18653/v1/2020.acl-main.386](https://doi.org/10.18653/v1/2020.acl-main.386) |
| Rationale evaluation (contrast for T7-009) | DeYoung, J. et al. (2020). *ERASER: A Benchmark to Evaluate Rationalized NLP Models.* ACL 2020. [doi:10.18653/v1/2020.acl-main.408](https://doi.org/10.18653/v1/2020.acl-main.408). We do **not** compute comprehensiveness/sufficiency. |
| Reason code per action (T5-015) | Yao, S. et al. (2023). *ReAct: Synergizing Reasoning and Acting in Language Models.* ICLR 2023. [arXiv:2210.03629](https://arxiv.org/abs/2210.03629) |
| Trajectory-level evaluation (explainability pack) | *Beyond the Final Answer: Evaluating the Reasoning Trajectories of Tool-Augmented Agents* (2025). [arXiv:2510.02837](https://arxiv.org/abs/2510.02837) (called "TRACE" in these docs) |
| Memory provenance (T6-007) | Lewis, P. et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.* NeurIPS 2020. [arXiv:2005.11401](https://arxiv.org/abs/2005.11401) |
| Counterfactual fairness, the idea (T7-007) | Kusner, M. J., Loftus, J., Russell, C., Silva, R. (2017). *Counterfactual Fairness.* NeurIPS 2017. [arXiv:1703.06856](https://arxiv.org/abs/1703.06856). No causal model is fitted. |
| Catalogue (all IDs) | Padmanabhuni, S. (2026). *Agentic AI Assurance Test Taxonomy v1.* Zenodo. [doi:10.5281/zenodo.23587407](https://doi.org/10.5281/zenodo.23587407) · [Hub dataset](https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110) |

## C. Agent patterns imitated by the sample agents

| Agent | Reference |
|:--|:--|
| `planner` | Wang, L. et al. (2023). *Plan-and-Solve Prompting.* ACL 2023. [arXiv:2305.04091](https://arxiv.org/abs/2305.04091) |
| `critic` | Madaan, A. et al. (2023). *Self-Refine: Iterative Refinement with Self-Feedback.* NeurIPS 2023. [arXiv:2303.17651](https://arxiv.org/abs/2303.17651) |
| `reflective`, `critic` | Shinn, N. et al. (2023). *Reflexion: Language Agents with Verbal Reinforcement Learning.* NeurIPS 2023. [arXiv:2303.11366](https://arxiv.org/abs/2303.11366) |
| `reflective`, `hallucinator` (reason before action) | ReAct (above) |

All sample agents are deterministic code. They do not call an LLM.

## D. Considered but NOT implemented (listed for clarity)

The following methods are often asked about. agentest does **not** implement them,
and no oracle claims to:

- LIME: Ribeiro, Singh, Guestrin (2016), KDD. [doi:10.1145/2939672.2939778](https://doi.org/10.1145/2939672.2939778)
- SHAP: Lundberg & Lee (2017), NeurIPS. [arXiv:1705.07874](https://arxiv.org/abs/1705.07874)
- Integrated Gradients: Sundararajan, Taly, Yan (2017), ICML. [arXiv:1703.01365](https://arxiv.org/abs/1703.01365)
- These attribute model inputs and need model internals or many forward passes. Our explainability oracles check trace faithfulness instead.
- Demographic parity / equalized odds: Hardt, Price, Srebro (2016), *Equality of Opportunity in Supervised Learning*, NeurIPS. [arXiv:1610.02413](https://arxiv.org/abs/1610.02413). The four-fifths rule: 29 CFR §1607.4(D) (EEOC Uniform Guidelines, 1978), <https://www.ecfr.gov/current/title-29/subtitle-B/chapter-XIV/part-1607/section-1607.4>. Both are group-rate metrics, and the bias pack uses single counterfactual pairs, so it computes no rates.
- Differential privacy: Dwork (2006), ICALP. [doi:10.1007/11787006_1](https://doi.org/10.1007/11787006_1)
- Training-data extraction: Carlini et al. (2021), USENIX Security. [arXiv:2012.07805](https://arxiv.org/abs/2012.07805)
- The privacy pack tests the agent's runtime behaviour, not the model's training data.
- Self-consistency: Wang, X. et al. (2023), ICLR. [arXiv:2203.11171](https://arxiv.org/abs/2203.11171). T1-002 and T1-003 repeat episodes but do not vote over sampled reasoning paths.
- LLM-as-a-judge: Zheng et al. (2023), NeurIPS Datasets & Benchmarks. [arXiv:2306.05685](https://arxiv.org/abs/2306.05685). Not used, because all oracles are deterministic.

## E. In-house heuristics (explicit list)

These checks are our own design. They are cited only to the catalogue and to background ideas:
T1-001, T1-004, T1-005, T1-007, T1-011, T1-013, T1-015, T1-016, T1-018, T2-001,
T2-003, T2-004, T2-005, T2-009, T2-013, T3-001, T3-002, T3-006, T3-007, T3-008,
T3-010, T3-011, T3-014, T4-009, T5-004 (regex PII), T5-011, T5-012, T5-015, T6-003,
T6-006, T6-007, T6-010, T7-009 (keyword consistency + trace-cited steps), the
T7-014 regex detector, the bias-pack labelers, and the risk-tier thresholds in
`config/thresholds.py`.
