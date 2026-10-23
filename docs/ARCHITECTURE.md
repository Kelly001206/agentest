# Architecture

## Dual-repo

1. **Hub catalogue** — stable IDs, acceptance criteria, fixtures notes (CC BY 4.0).
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

Each Hub ID is a `CaseSpec` (`make_env`, `golden`, `broken`, `oracle`) in `agentest.cases`.  
`FUNCTIONAL_IDS` lists the 18-pack order; `PRIVACY_IDS` the 8-pack; `EXPLAINABILITY_IDS` the 5-pack; `BIAS_FAIRNESS_IDS` the 3-pack (`--suite bias_fairness`, alias `bias`); `ORCHESTRATION_IDS` the 8-ID theme pack (`--suite orchestration`, alias `orch`) — Hub pack [`packs/orchestration.csv`](https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110/blob/main/packs/orchestration.csv); T3-006 CaseSpec reused from explainability. Multi-run IDs (T1-002, T1-003) use `cases.multi_run`.  
Privacy extends Env with profiles, multi-tenant stores, consent, exports/emails, and mask oracles.

## Constraints

- No third-party eval frameworks
- Deterministic scripted agents (no LLM in the harness loop)
- Broken-agent contract on every ID before merge

## Sample agents (teaching)

Seven complexity-graded agents under `agentest.samples` (`stub` → `handoff`).  
See [`docs/SAMPLE-AGENTS.md`](SAMPLE-AGENTS.md). CLI: `agentest samples`, `agentest matrix`,  
`agentest run --agent stub|eager|scripted|policy|reflective|supervisor|handoff|planner|critic|federation`.  
`golden`/`broken` remain the oracle Pass/Fail fixtures.
