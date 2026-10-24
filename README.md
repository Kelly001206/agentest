# agentest

[![CI](https://github.com/srpadmanabhuni/agentest/actions/workflows/ci.yml/badge.svg)](https://github.com/srpadmanabhuni/agentest/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![HF dataset](https://img.shields.io/badge/Hugging%20Face-checklist%20110-yellow.svg)](https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110)
[![HF downloads](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fhuggingface.co%2Fapi%2Fdatasets%2Fsrinivaspadmanabhuni%2Fagentic-ai-test-checklist-110&query=%24.downloads&label=HF%20downloads&color=yellow)](https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110)
[![Zenodo](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.23587407-blue.svg)](https://doi.org/10.5281/zenodo.23587407)

**Offline open-core runner for the [Agentic AI Test Checklist 110](https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110).**  
Clone → install → run. No Hugging Face account, token, or download required at runtime. ISO 42001–aligned assurance checklist design (not certification).

## Clone and run (30 seconds)

```bash
git clone https://github.com/srpadmanabhuni/agentest.git
cd agentest
python -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[dev]"

agentest samples            # 15 teaching agents (1–15)
agentest run --suite functional --agent golden
agentest matrix             # green ladder must stay 42/42
```


## Prefer the Hub catalogue first?

```python
# pip install datasets — this increments Hub downloads
from datasets import load_dataset
ds = load_dataset("srinivaspadmanabhuni/agentic-ai-test-checklist-110", "p0_smoke")
print(ds["train"][0]["id"], ds["train"][0]["title"])
```

60s notebook on Hub: [`notebooks/load_checklist_60s.ipynb`](https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110/blob/main/notebooks/load_checklist_60s.ipynb) · User guide: [`USER-GUIDE.md`](https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110/blob/main/USER-GUIDE.md)

This repo stays the **offline runner** (packs under `catalog/` — no Hub needed at runtime).

Developer guide (GitHub-only path): [`docs/DEVELOPER-GUIDE.md`](docs/DEVELOPER-GUIDE.md) · Bibliography: [`docs/REFERENCES.md`](docs/REFERENCES.md) · Launch copy: [`docs/launch/`](docs/launch/)

| Surface | Location |
|:--------|:---------|
| **Runner (this repo)** | [`srpadmanabhuni/agentest`](https://github.com/srpadmanabhuni/agentest) |
| Catalogue (source of truth) | [`srinivaspadmanabhuni/agentic-ai-test-checklist-110`](https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110) |
| Hub **User guide** | [`USER-GUIDE.md`](https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110/blob/main/USER-GUIDE.md) |
| Pulse (110 tests) | [Testing Agentic AI](https://www.linkedin.com/pulse/testing-agentic-ai-dr-srinivas-padmanabhuni-5stoc) · `#100daysoftestingagenticai` |
| Zenodo taxonomy | [10.5281/zenodo.23587407](https://doi.org/10.5281/zenodo.23587407) |
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
| M5 | `v0.7.0a0` | **Orchestration** theme (8 Hub IDs) + samples 6–7 ✅ |
| M5b | `v0.8.0a0` | Sample agents **8–10** (`planner`, `critic`, `federation`) ✅ |
| M5c | `v0.9.0a0` | Expected-fail scenarios **11–15** (`leaky`…`flaky_plan`) ✅ |
| M5d | `v0.9.1a0` | Hub↔GitHub sync check (`scripts/check_hub_sync.py`) ✅ |
| M5e | `v0.9.2a0` | Launch hygiene + `docs/launch/` ready copy ✅ |
| M5f | `v0.9.3a0` | HF downloads badge + Hub-first CTA (wave 1 sync) ✅ |
| M6 | `v1.0.0-open` | Actions template + Hub cross-links |

## Suites

```bash
agentest run --suite functional --agent golden         # exit 0
agentest run --suite privacy --agent golden            # exit 0
agentest run --suite explainability --agent golden     # exit 0
agentest run --suite bias_fairness --agent golden      # exit 0 (alias: --suite bias)
agentest run --suite orchestration --agent golden      # exit 0 (alias: --suite orch)
agentest run --suite bias --agent broken               # exit 1

# Single ID
agentest run --suite bias_fairness --ids T7-007 --agent golden

pytest
```

Every implemented ID must **Pass** a golden agent and **Fail** the matching broken behaviour.

## Sample agents

Fifteen teaching agents (`stub` → `flaky_plan`): complexity **1–10** green ladder,
**11–15** expected-fail / teaching-negative scenarios (partial fail profiles).

```bash
agentest samples            # stub…flaky_plan (1–15)
agentest samples --failing  # leaky…flaky_plan only
agentest run --suite orchestration --agent supervisor
agentest run --suite privacy --agent leaky              # expect fails
agentest run --suite explainability --agent hallucinator
agentest run --suite bias_fairness --agent biased
agentest run --suite orchestration --agent overreach
agentest run --suite functional --ids T2-001 --agent flaky_plan
agentest matrix   # exit 0 iff scripted…federation/(golden) all-pass
```

Details: [`docs/SAMPLE-AGENTS.md`](docs/SAMPLE-AGENTS.md), references & attribution: [`docs/REFERENCES.md`](docs/REFERENCES.md), [`docs/SCENARIOS-8-10.md`](docs/SCENARIOS-8-10.md), [`docs/SCENARIOS-EXPECTED-FAIL.md`](docs/SCENARIOS-EXPECTED-FAIL.md).

## Explainability

- Trace-faithful oracles only (fluency does not score): [`docs/EXPLAINABILITY-ORACLE.md`](docs/EXPLAINABILITY-ORACLE.md)
- Research & algorithm map (TRACE [Kim et al. 2025], ReAct, TRAJECT-Bench, AgentDiagnose, RAG-style citations): [`docs/EXPLAINABILITY-RESEARCH.md`](docs/EXPLAINABILITY-RESEARCH.md)

## Bias / fairness

- Suite: `--suite bias_fairness` (alias `--suite bias`)
- Metamorphic, deterministic labels only — illustrative, **not certification**: [`docs/BIAS-RESEARCH.md`](docs/BIAS-RESEARCH.md)
- Proposed Hub v1.2 expansions (not in CSV yet): [`docs/PROPOSED-bias.md`](docs/PROPOSED-bias.md)

## Catalogue pin

See [`catalog/VERSION`](catalog/VERSION) (pinned Hub **v1.1.2**), plus vendored [`catalog/functional.csv`](catalog/functional.csv), [`catalog/privacy.csv`](catalog/privacy.csv), [`catalog/explainability.csv`](catalog/explainability.csv), [`catalog/bias_fairness.csv`](catalog/bias_fairness.csv), and [`catalog/orchestration.csv`](catalog/orchestration.csv).  
Change packs on Hugging Face first, then sync here. Hub visitors: start with [USER-GUIDE.md](https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110/blob/main/USER-GUIDE.md).  
Keep Hub↔GitHub locked: `python scripts/check_hub_sync.py` (CI) · optional `--live`.

## Licence

Apache-2.0 (runner). Checklist data remains **CC BY 4.0** on Hugging Face.
