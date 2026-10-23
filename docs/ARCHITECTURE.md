# Architecture

## Dual-repo

1. **Hub catalogue** — stable IDs, acceptance criteria, fixtures notes (CC BY 4.0).
2. **This runner** — CLI, mock gateway, oracles, CI (Apache-2.0).

## Core types

- `Env` — fresh mock systems of record (ledger, tickets, …)
- `Trace` — ordered tool calls + handover events
- `ToolCall` — name, args, result, allowed?
- `Result` — `pass` | `fail` | `unverified` (missing evidence ≠ pass)

## Oracle rule (explainability, later)

An explanation Passes only if every cited step appears in the tool trace (IDs + order). Fluency does not score. See `docs/EXPLAINABILITY-ORACLE.md` (added at M3).

## Constraints

- No third-party eval frameworks
- Deterministic oracles first; in-house LLM judge only where soft packs need it
- Broken-agent contract on every ID before merge
