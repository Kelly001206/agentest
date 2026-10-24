# Show HN — ready copy (GitHub-first)

Post **once**. Prefer US daytime. Link the GitHub repo (not only Hub).

## Title

```
Show HN: agentest – offline checklist runner for testing agentic AI (clone and run)
```

## URL

https://github.com/srpadmanabhuni/agentest

## First comment

```
agentest is a thin open-core harness that turns checklist IDs into Pass/Fail against a mock tool gateway — no DeepEval/Ragas/Promptfoo stack, no API keys required to try it.

Why it exists: chat transcripts and LLM-as-judge miss a lot of agent failures (false “done”, tool order, allowlist misses, privacy fences, flaky plans). The companion Hub catalogue is 110 design rows (CC BY 4.0); this repo is the runnable Apache-2.0 core.

Clone and run:

  git clone https://github.com/srpadmanabhuni/agentest.git
  cd agentest && python -m pip install -e ".[dev]"
  agentest samples
  agentest run --suite functional --agent golden
  agentest matrix

Fifteen teaching agents (10 green ladder + 5 expected-fail). Suites today: functional, privacy, explainability, bias_fairness, orchestration. Checklist design informed by the assurance taxonomy and ISO 42001 themes — not a certification and not a model leaderboard. Status: early — the oracles are stub/reference implementations run against scripted mock agents; real-agent adapters and more packs are being added incrementally.

Catalogue + taxonomy:
  HF: https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110
  Pulse: https://www.linkedin.com/pulse/testing-agentic-ai-dr-srinivas-padmanabhuni-5stoc
  Zenodo: https://doi.org/10.5281/zenodo.23587407

Happy to answer questions about oracles, bring-your-own-agent, or the expected-fail teaching agents.
```

## Do not

- Claim stars, downloads, or “trending”
- Paste company sales CTAs
- Repost the same day if it misses
