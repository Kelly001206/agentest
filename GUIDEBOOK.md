# agentest guidebook

agentest is an offline test runner for agentic AI systems. It checks **what an agent actually did**
(tool calls, rows written, messages sent, state left behind), not just what it said. It has
130 real checks: the 110 IDs of the *Agentic AI Test Checklist 110* catalogue plus 20 repo
extensions `X-001..X-020`. Every check is deterministic or metamorphic. A few read free text with regex
heuristics. Those are marked **uncalibrated heuristic** in their per-test doc. No third-party eval
framework, no API key, no network at test time.

Contents: [Install](#1-install) · [Concepts](#2-concepts) · [Running packs](#3-running-packs) ·
[Reading reports](#4-reading-reports) · [Writing an adapter](#5-writing-an-adapter-for-your-agent) ·
[Recording reference agents](#6-recording-live-episodes) · [CI](#7-ci) · [Extending](#8-extending-the-tests) · [FAQ](#9-faq)

## 1. Install

```bash
git clone https://github.com/srpadmanabhuni/agentest.git && cd agentest
python -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest -q                # unit tests + offline replay of all recorded episodes
agentest real            # full 130 x 27 matrix, offline (about 1 s)
```

You need Python 3.11 or newer. You need no GPU, model or account. Only re-recording the reference agents needs the
optional local model (section 6).

## 2. Concepts

| Term | Meaning |
|:--|:--|
| **ID** | One check. `T1-001`…`T7-0xx` are catalogue IDs (vendored in `catalog/checklist-110.jsonl`); `X-001`…`X-020` are repo extensions. |
| **Sample agent** | One of 15 scripted teaching agents (`agentest samples`). `noop` does nothing. 8 "ladder" agents are correct. `eager` breaks everything. `leaky`, `hallucinator`, `biased`, `overreach` and `flaky_plan` each carry one defect class. They show that each oracle can both pass and fail. |
| **Reference agent** | One of 12 real agents in `reference_agents/` (a01…a12), built on common frameworks (LangGraph, LlamaIndex, AutoGen, CrewAI, n8n, …) and driven by a local open model. |
| **Episode** | One recorded run: `{agent, probe, rep, input, output, trace, extra, error}` in `fixtures/real/episodes/<agent>[.<set>].jsonl`. |
| **Probe** | A named input sent to an agent: `canon` is the normal task, and the others are adversarial or metamorphic variants (paraphrase, quoted injection, Hindi/Tamil, duplicate, ambiguity, …). |
| **Oracle / check** | A pure function from episodes to `pass` / `fail` / `n/a`, with a `detail` string naming the evidence. |
| **Mock gateway** | `agentest.gateway.ToolGateway`: the in-memory tools and ledger the catalogue packs run against. |

There are two layers:
1. **Catalogue packs** (`agentest run --suite …`): CaseSpec scenarios in `src/agentest/cases/` for the 41 IDs vendored in `catalog/*.csv`, under the mock gateway.
2. **Real matrix** (`agentest real`): all 130 IDs for 15 sample agents (cases for the first 41, plus deterministic mini-worlds in `real/synth.py` for the other 89), and for 12 reference agents via recorded episodes (`real/checks.py`, `real/checks2.py`).

## 3. Running packs

```bash
agentest samples                                  # list sample agents
agentest run --suite functional --agent golden    # one pack, one agent
agentest matrix                                   # 41 pack IDs x sample agents
agentest real                                     # 130 IDs x 27 agents (markdown to stdout)
agentest real --agents reference --md out.md --json out.json
agentest real --ids T4-005,X-009                  # just these cells
```

## 4. Reading reports

`fixtures/real/RESULTS.md` is the committed matrix, and `results.json` holds the same data with a `detail` for every cell.

- `pass`: the oracle held on every recorded episode.
- `fail`: at least one episode violated it. `detail` quotes the evidence (for example `request_refund called without lookup`).
- `n/a`: the agent has no surface for this check, or a translation-fidelity gate tripped.
- `not-run`: there are no episodes for a reference agent. `agentest real` exits 1.

A failure on a reference agent is a **finding** about that agent, not a test-suite failure. CI fails only when the
replay differs from the committed results or a unit test breaks. Each ID's doc (`docs/tests/<ID>.md`) explains how to read it.

## 5. Writing an adapter for your agent

**Option A: mock gateway (fastest).** Subclass `agentest.samples.base.SampleAgent` and implement
`handle(checklist_id, env) -> Trace`. Inside it, call tools through `ToolGateway(env)` and record a `Trace`.
Register the class in `agentest/samples/__init__.py`, then run `agentest run --agent yours`.

**Option B: your real agent (recorded episodes).**
1. Write a runner that sends each probe to your agent and writes one JSON line per run:
   ```json
   {"agent": "mine", "probe": "canon", "rep": 0, "input": "...", "output": {...},
    "trace": [{"tool": "lookup_order", "args": {...}}], "extra": {"db_sha_before": "...", "db_sha_after": "..."}, "error": null}
   ```
   Put observable side effects in `output` or `extra` (rows written, emails sent, DB hashes). Oracles trust evidence, not claims.
2. Register checks:
   ```python
   from agentest.real.checks import check, ok
   @check("T1-001", "mine")
   def _(E):
       o = E.out("canon")
       return ok(o["rows_written"] == ["R1"], f"rows={o['rows_written']}")
   ```
   `E.out(probe)`, `E.get(probe)` and `E.all` give access to episodes.
3. Add `"mine"` to `REF_AGENTS` and run `agentest real --agents reference`.

## 6. Recording live episodes

The reference agents need `reference_agents/requirements-reference.txt` (a separate venv), n8n via Node 22 for a08,
and a Qwen2.5-7B-Instruct Q4_K_M GGUF file (any source; set `REF_GGUF` to its path). Then:

```bash
cd reference_agents
REF_GGUF=/path/model.gguf PYTHONPATH=. python common/gguf_llm_server.py &   # OpenAI-compatible, :8008, temperature 0
PYTHONPATH=../src python -m agentest.real.live --agent a05             # canon + adversarial set
PYTHONPATH=../src python -m agentest.real.live --agent a05 --set b1    # extra probe sets (b1, b2)
python ../scripts/translate_probes.py                                  # regenerate Hindi/Tamil probes (local model)
```

Run one agent at a time, because the 7B model uses about 5 GB of RAM. Then regenerate the matrix and commit the episodes so CI can replay them.

## 7. CI

`.github/workflows/ci.yml` runs ruff, `scripts/check_catalog_pins.py` (sha256 pins of the vendored CSVs), `pytest`
(which includes the offline replay and an exact match against `fixtures/real/results.json`) and `agentest real`.
CI never calls a model.

## 8. Extending the tests

- **New catalogue-style check:** add the ID and description to `real/ids.py`, a mini-world scenario to `real/synth.py`
  (the ladder agents must pass and `eager` must fail), reference checks to `real/checks2.py`, and probes to `real/probes2.py` if needed.
  Then run `python scripts/gen_test_docs.py`.
- **Contract:** every ID must have at least one passing and one failing agent (`tests/real/test_replay_matrix.py` enforces this).
- **Heuristics:** if a check reads free text, say so in its doc and keep it a regex or keyword rule. Do not add a model judge
  unless it is documented as uncalibrated.

## 9. FAQ

**Is this a benchmark or a certification?** No. It is a test harness. The catalogue is informed by ISO/IEC 42001 themes; this is not certification.

**Why recorded episodes instead of calling the model in CI?** CI should be deterministic, free and offline. Re-record when an agent changes.

**k is small. Can I trust a pass?** A pass is evidence, not proof. Increase `rep` in the probes for flakiness work.

**Why are some cells n/a?** The agent has no such surface (for example no memory store), or the Hindi/Tamil back-translation failed the fidelity gate.

**How good are the Hindi/Tamil probes?** They are machine-translated by the same local 7B model and back-translated, which makes them a heuristic. The Tamil quality is poor, so the fidelity gate marks those cells n/a.

**Does it need a network?** Not at test time. It never needs an account or token.

**Contact:** srinivas AT testAIng.com
