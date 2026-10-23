"""Run checklist IDs against a chosen agent."""

from __future__ import annotations

from agentest.agents import get_agent
from agentest.env import Env
from agentest.fixtures.ledger import T1_001_EXPECTED, fresh_env_t1_001
from agentest.oracles.t1_001 import evaluate_t1_001
from agentest.types import Outcome, Result


def _run_t1_001(agent_name: str) -> Result:
    env: Env = fresh_env_t1_001()
    agent = get_agent(agent_name)
    trace = agent(env)
    return evaluate_t1_001(env, trace, expected=T1_001_EXPECTED)


REGISTRY = {
    "T1-001": _run_t1_001,
}


def run_ids(
    ids: list[str],
    *,
    suite: str = "functional",
    agent: str = "golden",
) -> list[Result]:
    _ = suite  # reserved for pack filtering later
    results: list[Result] = []
    for checklist_id in ids:
        fn = REGISTRY.get(checklist_id)
        if fn is None:
            results.append(
                Result(
                    checklist_id=checklist_id,
                    outcome=Outcome.UNVERIFIED,
                    reason="ID not implemented in this runner yet",
                )
            )
            continue
        results.append(fn(agent))
    return results


def all_passed(results: list[Result]) -> bool:
    return bool(results) and all(r.ok for r in results)
