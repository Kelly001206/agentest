# Reddit — ready copy (GitHub-first)

Pick **one** fitting subreddit per day. Prefer intent subs (`r/MachineLearning`, `r/LocalLLaMA`, `r/QualityAssurance`, `r/LLMDevs` if allowed). No spam / cross-post storms.

## Title options

```
[P] agentest: offline open-core runner for testing agentic AI (checklist → Pass/Fail)
```

```
Clone-and-run harness for agentic AI assurance tests (functional, privacy, explainability, bias, orchestration)
```

## Body

```
I open-sourced agentest — a thin CLI + mock tool gateway that executes checklist IDs as deterministic Pass/Fail tests. No eval-framework lock-in (not DeepEval/Ragas/Promptfoo). No API key needed to try the samples.

Why: LLM-as-judge and chat review miss agent failures I kept hitting — false “done”, tool ordering, allowlist misses, privacy fences, flaky multi-step plans.

Quick start:

    git clone https://github.com/srpadmanabhuni/agentest.git
    cd agentest && python -m pip install -e ".[dev]"
    agentest samples
    agentest run --suite functional --agent golden
    agentest matrix

15 teaching agents (10 all-pass ladder + 5 expected-fail). Catalogue lives on Hugging Face (CC BY 4.0); this repo is the Apache-2.0 runnable core and works fully offline.

Repo: https://github.com/srpadmanabhuni/agentest
Hub: https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110
Pulse / taxonomy: https://www.linkedin.com/pulse/testing-agentic-ai-dr-srinivas-padmanabhuni-5stoc · https://doi.org/10.5281/zenodo.23587407

Happy to take critique on oracle design or missing suites.
```

## Subreddit notes

- Follow each sub’s self-promo rules; disclose you are the author.
- Prefer a short comment linking the repo under a relevant discussion over a cold top-level spam post.
