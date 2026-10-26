"""Reference agents for T1-001 (legacy) and re-exports.

Per-ID golden/broken behaviours live under agentest.cases.*.
"""

from __future__ import annotations

from collections.abc import Callable

from agentest.agents import broken as broken_mod
from agentest.agents import golden as golden_mod
from agentest.env import Env
from agentest.types import Trace

AgentFn = Callable[[Env], Trace]

# T1-001 defaults (used by examples/ and legacy tests)
AGENTS: dict[str, AgentFn] = {
    "golden": golden_mod.run,
    "broken": broken_mod.run,
}


def get_agent(name: str) -> AgentFn:
    """Return a golden/broken fixture agent by name."""
    try:
        return AGENTS[name]
    except KeyError as exc:
        known = ", ".join(sorted(AGENTS))
        raise ValueError(f"unknown agent {name!r}; choose one of: {known}") from exc
