# Architecture

## Dual-repo

1. **catalogue** — stable IDs, acceptance criteria, fixtures notes (CC BY 4.0).
2. **This runner** — CLI, mock gateway, oracles, CI (Apache-2.0).

## Core types

- `Env` / `Ledger` — ledger, contacts, counters, users, orders, inventory, tickets, notify, multi-turn `AgentState`
- `Env.snapshot` / `Env.diff` — side-effect fence
- `Trace` / `ToolCall` — ordered tool calls + `claims_success` + `succeeded`
- `ToolGateway` — mock tools; `WRITE_TOOLS` / `READ_TOOLS` / orchestration tools
- `ApprovalsStore` / `env.role` / `env.clock` — handoff + HITL + TTL
- `agentest.policy.permits` / `HIGH_PRIV` — authz oracles
- `Result` — `pass` | `fail` | `unverified`

## Cases

Each catalogue ID is a `CaseSpec` (`make_env`, `golden`, `broken`, `oracle`) in `agentest.cases`.  
`FUNCTIONAL_IDS` lists the 18-pack order; `PRIVACY_IDS` the 8-pack; `EXPLAINABILITY_IDS` the 5-pack; `BIAS_FAIRNESS_IDS` the 3-pack (`--suite bias_fairness`, alias `bias`); `ORCHESTRATION_IDS` the 8-ID theme pack (`--suite orchestration`, alias `orch`) — catalogue pack `packs/orchestration.csv`; T3-006 CaseSpec reused from explainability. Multi-run IDs (T1-002, T1-003) use `cases.multi_run`.  
Privacy extends Env with profiles, multi-tenant stores, consent, exports/emails, and mask oracles.

## Constraints

- No third-party eval frameworks
- Deterministic scripted agents (no LLM in the harness loop)
- Broken-agent contract on every ID before merge

## Sample agents (teaching)

Fifteen complexity-graded agents under `agentest.samples` (`noop` → `flaky_plan`).  
Green ladder 1–10; expected-fail band 11–15 (`leaky`…`flaky_plan`).  
See [`docs/SAMPLE-AGENTS.md`](SAMPLE-AGENTS.md), [`SCENARIOS-EXPECTED-FAIL.md`](SCENARIOS-EXPECTED-FAIL.md).  
CLI: `agentest samples [--failing]`, `agentest matrix`,  
`agentest run --agent noop|…|federation|leaky|hallucinator|biased|overreach|flaky_plan`.  
`golden`/`broken` remain the oracle Pass/Fail fixtures.  
`MATRIX_MUST_PASS` ignores expected-fail agents for matrix exit status.

## Real-check layer (`src/agentest/real/`)

```
ids.py        130 IDs: REAL_IDS (41 pack IDs) + BATCH1/2/3 (69) = CATALOGUE_IDS (110) + X_IDS (20); what(id)
samples.py    15 sample agents -> {id: R}: pack CaseSpecs for REAL_IDS, synth.run for the rest
synth.py      deterministic mini-worlds (World: calls/state/audit/clock/gateway) per new ID; defect PROFILES per sample agent
probes.py     AGENT_DIRS + canon/adversarial PROBES per reference agent
probes2.py    extra probe sets b1 (metamorphic, translation, quoting) and b2 (hidden text, slots, secrets, twin resume)
live.py       records episodes from reference agents against the local model (not used in CI)
checks.py     Eps accessor, @check registry, helpers, checks for the first 41 IDs; evaluate(agent, eps)
checks2.py    checks for the 69 newer catalogue IDs and X-001..X-020 on reference agents
report.py     build() -> {agent: {id: R}}; markdown/JSON writers
```

Flow: `live.py` → `fixtures/real/episodes/*.jsonl` → `checks.evaluate` → `report.build` → `RESULTS.md` / `results.json`.
A missing `(id, agent)` check yields `n/a`; missing episodes yield `not-run`. Translation fidelity for Hindi/Tamil
probes is gated in `checks2._GATE`: required keywords must survive the back-translation (a keyword heuristic).
