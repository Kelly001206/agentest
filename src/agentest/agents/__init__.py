"""Reference agents: golden (must Pass) and broken (must Fail)."""

from __future__ import annotations

from collections.abc import Callable

from agentest.agents import broken as broken_mod
from agentest.agents import golden as golden_mod
from agentest.env import Env
from agentest.types import Trace

AgentFn = Callable[[Env], Trace]

AGENTS: dict[str, AgentFn] = {
    "golden": golden_mod.run,
    "broken": broken_mod.run,
}


def get_agent(name: str) -> AgentFn:
    try:
        return AGENTS[name]
    except KeyError as exc:
        known = ", ".join(sorted(AGENTS))
        raise ValueError(f"unknown agent {name!r}; choose one of: {known}") from exc
