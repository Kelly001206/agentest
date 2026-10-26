"""Golden agent for T1-001 — writes correct ledger statuses then claims success."""

from __future__ import annotations

from agentest.env import APPROVED, REJECTED, Env
from agentest.gateway import ToolGateway
from agentest.types import Trace

# Approve R1–R3, reject R4; leave R5 untouched.
_ACTIONS: list[tuple[str, str]] = [
    ("R1", APPROVED),
    ("R2", APPROVED),
    ("R3", APPROVED),
    ("R4", REJECTED),
]


def run(env: Env) -> Trace:
    """Run the case (or agent) and return its result."""
    trace = Trace()
    # All tool calls go through the gateway, which records them on the trace and enforces simulated authz.
    gw = ToolGateway(env, trace)
    # Apply exactly the expected decisions; R5 is deliberately untouched (collateral check).
    for record_id, status in _ACTIONS:
        # Tool `ledger.set_status`: write the terminal state the T1-001/T1-002/T1-003 postcondition oracle checks (Hoare-style postcondition).
        gw.call("ledger.set_status", record_id=record_id, status=status)
    # Agent self-report of success; oracles never trust this alone (false-completion check, Hoare-style postconditions).
    trace.claims_success = True
    trace.message = "Approved R1–R3, rejected R4"
    return trace
