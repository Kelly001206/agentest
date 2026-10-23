# golden_agent

Reference agent that **must Pass** implemented IDs.

For **T1-001**: writes APPROVED for R1–R3 and REJECTED for R4 via `ledger.set_status`, leaves R5 PENDING, then claims success.

Implementation: `agentest.agents.golden` (invoked by `agentest run --agent golden`).
