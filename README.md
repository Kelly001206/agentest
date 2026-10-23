# agentest

**Open-core runner for the [Agentic AI Test Checklist 110](https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110).**

Thin CLI + harness that executes checklist IDs against a mock tool gateway.  
Catalogue lives on Hugging Face; this repo is the runnable open core.

| Surface | Location |
|:--------|:---------|
| Catalogue (source of truth) | [`srinivaspadmanabhuni/agentic-ai-test-checklist-110`](https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110) |
| Runner (this repo) | [`srpadmanabhuni/agentest`](https://github.com/srpadmanabhuni/agentest) |
| Commercial harness | Private (AiEnsured / testAIng) — later |

**Author:** Dr Srinivas Padmanabhuni · srinivas AT testAIng.com · [testAIng.com](https://testaing.com) / [AiEnsured](https://aiensured.com)

## Non-goals

- No DeepEval, Giskard, Langfuse, Promptfoo, Ragas, or similar eval frameworks
- Not a model leaderboard; not certification
- Security pack remains **parked** for a later milestone (functional → privacy → explainability → bias shipped first)

## Status (solo MVP)

| Milestone | Tag | Scope |
|:----------|:----|:------|
| M0 | `v0.1.0` | CLI + gateway + **T1-001** |
| M1 | `v0.2.0` | Full **functional** pack (18 IDs) ✅ |
| M2 | `v0.3.0` | **Privacy** (8) ✅ |
| M3 | `v0.4.0` | **Explainability** (5) ✅ |
| M4 | `v0.5.0` | **Bias / fairness** (3) ✅ |
| M5 | `v1.0.0-open` | Actions template + Hub cross-links |

## Quick start (M4)

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[dev]"

# Functional + Privacy + Explainability + Bias/fairness
agentest run --suite functional --agent golden         # exit 0
agentest run --suite privacy --agent golden            # exit 0
agentest run --suite explainability --agent golden     # exit 0
agentest run --suite bias_fairness --agent golden      # exit 0 (alias: --suite bias)
agentest run --suite bias --agent broken               # exit 1

# Single ID
agentest run --suite bias_fairness --ids T7-007 --agent golden

pytest
```

Every implemented ID must **Pass** a golden agent and **Fail** the matching broken behaviour.

## Explainability

- Trace-faithful oracles only (fluency does not score): [`docs/EXPLAINABILITY-ORACLE.md`](docs/EXPLAINABILITY-ORACLE.md)
- Research & algorithm map (TRACE, ReAct, TRAJECT-Bench, AgentDiagnose, RAG-style citations): [`docs/EXPLAINABILITY-RESEARCH.md`](docs/EXPLAINABILITY-RESEARCH.md)

## Bias / fairness

- Suite: `--suite bias_fairness` (alias `--suite bias`)
- Metamorphic, deterministic labels only — illustrative, **not certification**: [`docs/BIAS-RESEARCH.md`](docs/BIAS-RESEARCH.md)
- Proposed Hub v1.2 expansions (not in CSV yet): [`docs/PROPOSED-bias.md`](docs/PROPOSED-bias.md)

## Catalogue pin

See [`catalog/VERSION`](catalog/VERSION), [`catalog/functional.csv`](catalog/functional.csv), [`catalog/privacy.csv`](catalog/privacy.csv), [`catalog/explainability.csv`](catalog/explainability.csv), and [`catalog/bias_fairness.csv`](catalog/bias_fairness.csv) (Hub v1.1 packs).  
Change packs on Hugging Face first, then sync here.

## Licence

Apache-2.0 (runner). Checklist data remains **CC BY 4.0** on Hugging Face.
