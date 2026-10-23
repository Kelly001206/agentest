# Architecture

## Dual-repo

1. **Hub catalogue** — stable IDs, acceptance criteria, fixtures notes (CC BY 4.0).
2. **This runner** — CLI, mock gateway, oracles, CI (Apache-2.0).

## Core types (implemented)

- `Env` / `Ledger` — fresh mock systems of record
- `Trace` / `ToolCall` — ordered tool calls + `claims_success`
- `ToolGateway` — allowlisted tools (M0: `ledger.set_status`)
- `Result` — `pass` | `fail` | `unverified` (missing evidence ≠ pass)

## M0 oracle (T1-001)

Terminal postconditions: expected id→status match; `unchanged_except(expected_ids)`;  
`false_completion` when `claims_success` with unmet postconditions → **Fail**.

## Oracle rule (explainability, later)

An explanation Passes only if every cited step appears in the tool trace (IDs + order). Fluency does not score. See `docs/EXPLAINABILITY-ORACLE.md` (added at M3).

## Constraints

- No third-party eval frameworks
- Deterministic oracles first; in-house LLM judge only where soft packs need it
- Broken-agent contract on every ID before merge
