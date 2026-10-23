# DEV.to — ready copy (GitHub-first)

Title and tags for a short how-to. Link GitHub above the fold.

## Title

```
Clone agentest: run agentic AI checklist tests offline in CI
```

## Tags

`ai`, `testing`, `opensource`, `python`, `agents`

## Body (markdown)

```markdown
# Clone agentest: run agentic AI checklist tests offline in CI

Shipping agents that **plan → call tools → hand off → mutate state**? Chat review and LLM-as-judge miss a lot of failures: false completion, wrong tool order, privacy leaks, biased labels, flaky plans.

**[agentest](https://github.com/srpadmanabhuni/agentest)** is an Apache-2.0 open-core runner for the [Agentic AI Test Checklist 110](https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110). Clone it and run — **no Hugging Face account** required at runtime.

## Quick start

\`\`\`bash
git clone https://github.com/srpadmanabhuni/agentest.git
cd agentest
python -m pip install -e ".[dev]"
agentest samples
agentest run --suite functional --agent golden
agentest run --suite orchestration --agent golden
agentest matrix
\`\`\`

## What you get

- Suites: functional, privacy, explainability, bias_fairness, orchestration
- 15 sample agents (10 green ladder + 5 expected-fail teaching scenarios)
- Deterministic oracles against a mock tool gateway
- ISO 42001 / assurance-taxonomy aligned checklist design (not certification)

## Context

- Pulse: [Testing Agentic AI](https://www.linkedin.com/pulse/testing-agentic-ai-dr-srinivas-padmanabhuni-5stoc)
- Zenodo taxonomy: https://doi.org/10.5281/zenodo.23587407
- Developer guide: https://github.com/srpadmanabhuni/agentest/blob/main/docs/DEVELOPER-GUIDE.md

Author: Dr Srinivas Padmanabhuni · srinivas AT testAIng.com
```
