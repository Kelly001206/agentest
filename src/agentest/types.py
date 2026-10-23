"""Core types for the agentest harness."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Outcome(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    UNVERIFIED = "unverified"


@dataclass
class Result:
    """Oracle outcome for one checklist ID."""

    checklist_id: str
    outcome: Outcome
    reason: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.outcome is Outcome.PASS


@dataclass
class ToolCall:
    name: str
    args: dict[str, Any]
    result: Any = None
    allowed: bool = True


@dataclass
class Trace:
    """Ordered tool calls from one agent run."""

    calls: list[ToolCall] = field(default_factory=list)
    claims_success: bool = False
    message: str = ""

    def record(self, call: ToolCall) -> None:
        self.calls.append(call)
