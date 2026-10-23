"""Mock tool gateway — allowlisted writes into Env."""

from __future__ import annotations

from typing import Any

from agentest.env import Env
from agentest.types import ToolCall, Trace


class ToolGateway:
    """Minimal tool surface for T1-001 (ledger.set_status)."""

    ALLOWED = frozenset({"ledger.set_status"})

    def __init__(self, env: Env, trace: Trace | None = None) -> None:
        self.env = env
        self.trace = trace if trace is not None else Trace()

    def call(self, name: str, **args: Any) -> Any:
        allowed = name in self.ALLOWED
        if not allowed:
            tc = ToolCall(name=name, args=args, result={"error": "denied"}, allowed=False)
            self.trace.record(tc)
            raise PermissionError(f"tool not allowlisted: {name}")

        if name == "ledger.set_status":
            record_id = args["record_id"]
            status = args["status"]
            self.env.ledger.set_status(record_id, status)
            result = {"record_id": record_id, "status": status}
        else:  # pragma: no cover — guarded by ALLOWED
            result = None

        tc = ToolCall(name=name, args=args, result=result, allowed=True)
        self.trace.record(tc)
        return result
