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
    trace = Trace()
    gw = ToolGateway(env, trace)
    for record_id, status in _ACTIONS:
        gw.call("ledger.set_status", record_id=record_id, status=status)
    trace.claims_success = True
    trace.message = "Approved R1–R3, rejected R4"
    return trace
