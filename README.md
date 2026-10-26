# agentest

[![CI](https://github.com/srpadmanabhuni/agentest/actions/workflows/ci.yml/badge.svg)](https://github.com/srpadmanabhuni/agentest/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.23614376-blue.svg)](https://doi.org/10.5281/zenodo.23614376)
[![HF dataset](https://img.shields.io/badge/%F0%9F%A4%97%20dataset-agentic--ai--test--checklist--110-yellow)](https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110)

**Offline test runner for agentic AI, covering the Agentic AI Test Checklist 110.**  
Clone → install → run. No account, token, network or model is needed at test time. The checklist design is informed by ISO 42001 themes; this is not certification.

> **Status: 130 of 130 checks are real; there are 0 placeholder checks.** The 130 are the 110 catalogue IDs plus 20 repo
> extensions (`X-001`…`X-020`, kept separate from catalogue IDs). Every check is a deterministic or metamorphic oracle
> over what an agent actually did. They run against **15 scripted sample agents** and **12 runnable reference agents**
> (`reference_agents/`, driven by a local open 7B model, with episodes recorded and replayed offline in CI). Every ID has at least
> one passing and one failing agent. **Caveats:** many IDs have no surface on a given reference agent and report `n/a` there.
> Some checks read free text with regex heuristics (marked as **uncalibrated heuristics**). The Hindi/Tamil probes are
> machine-translated by the local model, which is a heuristic. Samples are small (k = 1–3). These are not production-grade evaluators.
> Results: [`fixtures/real/RESULTS.md`](fixtures/real/RESULTS.md).

## Clone and run (30 seconds)

```bash
git clone https://github.com/srpadmanabhuni/agentest.git
cd agentest
python -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[dev]"

agentest samples            # 15 teaching agents
agentest real               # 130 checks x 27 agents, offline replay
agentest real --ids T4-005  # one check across all agents
```

**Docs:** [`GUIDEBOOK.md`](GUIDEBOOK.md) (install, concepts, adapters, reports, CI, extending, FAQ) ·
per-test reference [`docs/tests/`](docs/tests/README.md) · [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) ·
[`docs/DEVELOPER-GUIDE.md`](docs/DEVELOPER-GUIDE.md) · [`docs/REFERENCES.md`](docs/REFERENCES.md)

**Author:** Dr Srinivas Padmanabhuni · srinivas AT testAIng.com · [testAIng.com](https://testaing.com) / [AiEnsured](https://aiensured.com)

**Browse the checklist:**

```bash
atc list --class T3      # or: agentest list --class T3
atc run --suite functional
```

**Related:** checklist dataset on [Hugging Face](https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110) ·
DOI [10.5281/zenodo.23614376](https://doi.org/10.5281/zenodo.23614376) ·
article [Testing Agentic AI: 110 Tests for Safer AI Agents](https://www.linkedin.com/pulse/testing-agentic-ai-dr-srinivas-padmanabhuni-5stoc/) ·
framework crosswalk (NIST AI RMF, EU AI Act, OWASP LLM Top 10, ISO/IEC 42001 themes; indicative only) [`docs/FRAMEWORK-MAPPING.md`](docs/FRAMEWORK-MAPPING.md)

**Scope, honestly:** the checks are small deterministic oracles over scripted and recorded agents. Treat them as starter scaffolds to adapt to your own agent, not turnkey certification tests.

## Cite

```bibtex
@software{padmanabhuni_agentic_ai_test_checklist_110,
  author = {Padmanabhuni, Srinivas},
  title  = {Agentic AI Test Checklist 110 and agentest runner},
  doi    = {10.5281/zenodo.23614376},
  url    = {https://github.com/srpadmanabhuni/agentest}
}
```

See also [`CITATION.cff`](CITATION.cff).

## Non-goals

- No DeepEval, Giskard, Langfuse, Promptfoo, Ragas, or similar eval frameworks
- No model judge in the pass/fail path
- Not a model leaderboard, and not certification

## Real checks (130)

```bash
agentest real --md fixtures/real/RESULTS.md --json fixtures/real/results.json
```

* **Sample agents:** the 41 pack IDs use the scenario oracles in `src/agentest/cases/`. The other 89 IDs use deterministic
  mini-worlds in `src/agentest/real/synth.py`. Each sample agent's defect profile decides what it does.
* **Reference agents:** probes live in `src/agentest/real/probes.py` and `probes2.py`. They cover canonical tasks, refusal and approval bypass,
  prompt-injection canaries (quoted, hidden HTML, JSON breakout, base64), PII pairs, paraphrase, unit and negation variants,
  Hindi/Tamil translate-and-back, multi-turn slots, constraints and secrets, and concurrent twin resume. The oracles are in
  `src/agentest/real/checks.py` and `checks2.py`.
* **Thresholds** are fixed in code and documented per test in `docs/tests/<ID>.md`.
* **Agent failures are findings, not CI failures.** CI checks that the replay is complete and matches `fixtures/real/results.json`.

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

Fifteen teaching agents (`noop` → `flaky_plan`): complexity **1–10** green ladder,
**11–15** expected-fail / teaching-negative scenarios (partial fail profiles).

```bash
agentest samples            # noop…flaky_plan (1–15)
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
- Proposed catalogue v1.2 expansions (not in CSV yet): [`docs/PROPOSED-bias.md`](docs/PROPOSED-bias.md)

## Catalogue pin

See [`catalog/VERSION`](catalog/VERSION) (pinned catalogue **v1.2.1**; full 110-row catalogue vendored as [`catalog/checklist-110.jsonl`](catalog/checklist-110.jsonl)), plus vendored [`catalog/functional.csv`](catalog/functional.csv), [`catalog/privacy.csv`](catalog/privacy.csv), [`catalog/explainability.csv`](catalog/explainability.csv), [`catalog/bias_fairness.csv`](catalog/bias_fairness.csv), and [`catalog/orchestration.csv`](catalog/orchestration.csv).  
Pack CSVs are pinned by sha256: `python scripts/check_catalog_pins.py` (offline, runs in CI).

## Licence

Apache-2.0 (runner). Checklist data: **CC BY 4.0**.
