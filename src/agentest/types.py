"""Core types for the agentest harness."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Outcome(str, Enum):
    """Verdict of one check: pass, fail or unverified."""
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
        """True when the outcome is a pass."""
        return self.outcome is Outcome.PASS


@dataclass
class ToolCall:
    """One tool invocation: name, args and result."""
    name: str
    args: dict[str, Any]
    result: Any = None
    allowed: bool = True
    succeeded: bool = True
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class Trace:
    """Ordered tool calls from one agent run (possibly multi-turn)."""

    calls: list[ToolCall] = field(default_factory=list)
    claims_success: bool = False
    message: str = ""
    # Explainability pack fields
    api_success: bool | None = None
    memory_citations: list[str] = field(default_factory=list)
    explanation: str = ""
    cited_steps: list[str] = field(default_factory=list)  # tool/handover names claimed in explanation

    def record(self, call: ToolCall) -> None:
        """Append one entry."""
        self.calls.append(call)

    def count(self, name: str) -> int:
        """Number of calls to ``name``."""
        return sum(1 for c in self.calls if c.name == name)

    @property
    def tool_names(self) -> set[str]:
        """Ordered tool names called."""
        return {c.name for c in self.calls}

    @property
    def tool_calls(self) -> list[ToolCall]:
        """Ordered ToolCall records."""
        return self.calls
