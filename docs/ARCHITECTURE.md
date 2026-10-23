# Architecture

## Dual-repo

1. **Hub catalogue** — stable IDs, acceptance criteria, fixtures notes (CC BY 4.0).
2. **This runner** — CLI, mock gateway, oracles, CI (Apache-2.0).

## Core types

- `Env` / `Ledger` — ledger, contacts, counters, users, orders, inventory, tickets, notify, multi-turn `AgentState`
- `Env.snapshot` / `Env.diff` — side-effect fence
- `Trace` / `ToolCall` — ordered tool calls + `claims_success` + `succeeded`
- `ToolGateway` — mock tools; `WRITE_TOOLS` / `READ_TOOLS` classifiers
- `Result` — `pass` | `fail` | `unverified`

## Cases

Each Hub ID is a `CaseSpec` (`make_env`, `golden`, `broken`, `oracle`) in `agentest.cases`.  
`FUNCTIONAL_IDS` lists the 18-pack order; `PRIVACY_IDS` the 8-pack; `EXPLAINABILITY_IDS` the 5-pack; `BIAS_FAIRNESS_IDS` the 3-pack (`--suite bias_fairness`, alias `bias`). Multi-run IDs (T1-002, T1-003) use `cases.multi_run`.  
Privacy extends Env with profiles, multi-tenant stores, consent, exports/emails, and mask oracles.

## Constraints

- No third-party eval frameworks
- Deterministic scripted agents (no LLM in the harness loop)
- Broken-agent contract on every ID before merge
