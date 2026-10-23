"""Case registry and CaseSpec."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from agentest.env import Env
from agentest.types import Result, Trace

AgentFn = Callable[[Env], Trace]
OracleFn = Callable[[Env, Trace], Result]
EnvFactory = Callable[[], Env]

ORACLE_AGENTS = ("golden", "broken")
SAMPLE_AGENTS = ("stub", "eager", "scripted", "policy", "reflective")
ALL_AGENTS = ORACLE_AGENTS + SAMPLE_AGENTS


@dataclass(frozen=True)
class CaseSpec:
    checklist_id: str
    make_env: EnvFactory
    golden: AgentFn
    broken: AgentFn
    oracle: OracleFn

    def run(self, agent_name: str) -> Result:
        if agent_name not in ALL_AGENTS:
            raise ValueError(
                f"unknown agent {agent_name!r}; choose one of: {', '.join(ALL_AGENTS)}"
            )
        from agentest.cases import multi_run

        if self.checklist_id in multi_run.MULTI_RUN_IDS:
            return multi_run.run_multi(self.checklist_id, agent_name)

        env = self.make_env()
        if agent_name == "golden":
            trace = self.golden(env)
        elif agent_name == "broken":
            trace = self.broken(env)
        else:
            from agentest.samples import get_sample

            trace = get_sample(agent_name).handle(self.checklist_id, env)
        return self.oracle(env, trace)


def _build_registry() -> dict[str, CaseSpec]:
    from agentest.cases import bias, explainability, privacy, t1, t2, t5, t6

    specs: list[CaseSpec] = []
    specs.extend(t1.all_cases())
    specs.extend(t2.all_cases())
    specs.extend(t5.all_cases())
    specs.extend(t6.all_cases())
    specs.extend(privacy.all_cases())
    specs.extend(explainability.all_cases())
    specs.extend(bias.all_cases())
    return {s.checklist_id: s for s in specs}


CASE_REGISTRY: dict[str, CaseSpec] = _build_registry()

FUNCTIONAL_IDS: list[str] = [
    "T1-001",
    "T1-002",
    "T1-003",
    "T1-004",
    "T1-005",
    "T1-007",
    "T1-009",
    "T1-011",
    "T1-013",
    "T1-015",
    "T2-001",
    "T2-003",
    "T2-009",
    "T2-013",
    "T5-012",
    "T6-003",
    "T6-006",
    "T6-010",
]

PRIVACY_IDS: list[str] = [
    "T1-016",
    "T2-005",
    "T3-008",
    "T4-009",
    "T5-004",
    "T5-011",
    "T6-004",
    "T7-014",
]

EXPLAINABILITY_IDS: list[str] = [
    "T1-018",
    "T3-006",
    "T5-015",
    "T6-007",
    "T7-009",
]

BIAS_FAIRNESS_IDS: list[str] = [
    "T7-004",
    "T7-007",
    "T7-011",
]


def get_case(checklist_id: str) -> CaseSpec:
    try:
        return CASE_REGISTRY[checklist_id]
    except KeyError as exc:
        raise ValueError(f"checklist ID not implemented: {checklist_id}") from exc
