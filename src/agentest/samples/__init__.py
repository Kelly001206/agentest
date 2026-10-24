"""Teaching sample agents (complexity 1–15) for the checklist harness.

1–10: green teaching ladder (stub/eager fail by design; scripted…federation all-pass).
11–15: expected-fail / teaching-negative agents (partial fail profiles).
"""

from __future__ import annotations

from agentest.samples.base import SampleAgent, SampleAgentInfo
from agentest.samples.biased import BiasedAgent
from agentest.samples.critic import CriticAgent
from agentest.samples.eager import EagerAgent
from agentest.samples.federation import FederationAgent
from agentest.samples.flaky_plan import FlakyPlanAgent
from agentest.samples.hallucinator import HallucinatorAgent
from agentest.samples.handoff import HandoffAgent
from agentest.samples.leaky import LeakyAgent
from agentest.samples.overreach import OverreachAgent
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
    "leaky",
    "hallucinator",
    "biased",
    "overreach",
    "flaky_plan",
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

# Teaching-negative agents: allowed/expected to fail some IDs (partial profiles).
# stub/eager are legacy mostly-fail agents; the five below are category-focused.
MATRIX_EXPECTED_FAIL: frozenset[str] = frozenset(
    {
        "stub",
        "eager",
        "leaky",
        "hallucinator",
        "biased",
        "overreach",
        "flaky_plan",
    }
)

# Category-focused expected-fail band (cx 11–15), excluding stub/eager.
EXPECTED_FAIL_SCENARIOS: tuple[str, ...] = (
    "leaky",
    "hallucinator",
    "biased",
    "overreach",
    "flaky_plan",
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
        LeakyAgent(),
        HallucinatorAgent(),
        BiasedAgent(),
        OverreachAgent(),
        FlakyPlanAgent(),
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


def list_samples(*, failing_only: bool = False) -> list[SampleAgentInfo]:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _build()
    names = EXPECTED_FAIL_SCENARIOS if failing_only else SAMPLE_AGENT_NAMES
    return [get_sample(n).info() for n in names]


def is_sample_agent(name: str) -> bool:
    return name in SAMPLE_AGENT_NAMES


__all__ = [
    "EXPECTED_FAIL_SCENARIOS",
    "MATRIX_EXPECTED_FAIL",
    "MATRIX_MUST_PASS",
    "SAMPLE_AGENT_NAMES",
    "SampleAgent",
    "SampleAgentInfo",
    "get_sample",
    "is_sample_agent",
    "list_samples",
]
