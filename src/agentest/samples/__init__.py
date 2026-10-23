"""Teaching sample agents (complexity 1–10) for the checklist harness."""

from __future__ import annotations

from agentest.samples.base import SampleAgent, SampleAgentInfo
from agentest.samples.critic import CriticAgent
from agentest.samples.eager import EagerAgent
from agentest.samples.federation import FederationAgent
from agentest.samples.handoff import HandoffAgent
from agentest.samples.planner import PlannerAgent
from agentest.samples.policy import PolicyAgent
from agentest.samples.reflective import ReflectiveAgent
from agentest.samples.scripted import ScriptedAgent
from agentest.samples.stub import StubAgent
from agentest.samples.supervisor import SupervisorAgent

SAMPLE_AGENT_NAMES: tuple[str, ...] = (
    "stub",
    "eager",
    "scripted",
    "policy",
    "reflective",
    "supervisor",
    "handoff",
    "planner",
    "critic",
    "federation",
)

# Agents expected to pass the full matrix (oracle reference + teaching).
MATRIX_MUST_PASS: frozenset[str] = frozenset(
    {
        "scripted",
        "policy",
        "reflective",
        "supervisor",
        "handoff",
        "planner",
        "critic",
        "federation",
        "golden",
    }
)

_REGISTRY: dict[str, SampleAgent] | None = None


def _build() -> dict[str, SampleAgent]:
    agents: list[SampleAgent] = [
        StubAgent(),
        EagerAgent(),
        ScriptedAgent(),
        PolicyAgent(),
        ReflectiveAgent(),
        SupervisorAgent(),
        HandoffAgent(),
        PlannerAgent(),
        CriticAgent(),
        FederationAgent(),
    ]
    return {a.name: a for a in agents}


def get_sample(name: str) -> SampleAgent:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _build()
    try:
        return _REGISTRY[name]
    except KeyError as exc:
        known = ", ".join(SAMPLE_AGENT_NAMES)
        raise ValueError(f"unknown sample agent {name!r}; choose one of: {known}") from exc


def list_samples() -> list[SampleAgentInfo]:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _build()
    return [get_sample(n).info() for n in SAMPLE_AGENT_NAMES]


def is_sample_agent(name: str) -> bool:
    return name in SAMPLE_AGENT_NAMES


__all__ = [
    "MATRIX_MUST_PASS",
    "SAMPLE_AGENT_NAMES",
    "SampleAgent",
    "SampleAgentInfo",
    "get_sample",
    "is_sample_agent",
    "list_samples",
]
