# LinkedIn — ready copy (GitHub-first)

Post from personal profile (`linkedin.com/in/spadmanabhuni`). Lead with clone CTA.

## First line (before “see more”)

```
Clone agentest: offline runner for agentic AI checklist tests (no Hub account needed)
```

## Body

```
Open-source runner is live on GitHub: agentest — clone, pip install -e ., run checklist suites against a mock tool gateway.

If you ship agents that plan, call tools, hand off, and mutate state, transcript review alone leaves blind spots: false completion, wrong tool order, privacy leaks, biased labels, flaky plans.

What’s in the repo (Apache-2.0):
• CLI + deterministic oracles (functional / privacy / explainability / bias / orchestration)
• 15 sample agents — 10 green ladder + 5 expected-fail teaching scenarios
• Offline: no Hugging Face token required at runtime
• Catalogue pin synced from the Hub checklist (CC BY 4.0)

Try it:

  git clone https://github.com/srpadmanabhuni/agentest.git
  cd agentest && python -m pip install -e ".[dev]"
  agentest samples
  agentest run --suite orchestration --agent golden
  agentest matrix

GitHub: https://github.com/srpadmanabhuni/agentest
Developer guide: https://github.com/srpadmanabhuni/agentest/blob/main/docs/DEVELOPER-GUIDE.md

Built from:
• Pulse — Testing Agentic AI: https://www.linkedin.com/pulse/testing-agentic-ai-dr-srinivas-padmanabhuni-5stoc
• #100daysoftestingagenticai
• Zenodo taxonomy: https://doi.org/10.5281/zenodo.23587407
• Hub catalogue: https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110

Not a certification. Not a model leaderboard. Assurance test design you can actually run in CI.

—
Dr Srinivas Padmanabhuni · srinivas AT testAIng.com · testAIng.com / AiEnsured
Personal: https://sites.google.com/view/srinivaspadmanabhuni

#AgenticAI #AITesting #100daysoftestingagenticai #LLMAgents #ISO42001 #OpenSource #pytest
```
