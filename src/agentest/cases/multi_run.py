"""Multi-run oracles T1-002 and T1-003 (k repetitions)."""

from __future__ import annotations

from collections.abc import Callable

from agentest.config.thresholds import (
    T1_002_K,
    T1_003_K,
    T1_003_RISK_TIER,
    T1_003_THRESHOLD,
)
from agentest.env import APPROVED, PENDING, Env
from agentest.gateway import ToolGateway
from agentest.types import Outcome, Result, Trace

MULTI_RUN_IDS = frozenset({"T1-002", "T1-003"})

# Sample / oracle agents that correctly complete one high-risk episode.
_PASSING_MULTI = frozenset({"golden", "scripted", "policy", "reflective", "supervisor", "handoff", "planner", "critic", "federation", "leaky", "hallucinator", "biased", "overreach", "flaky_plan"})


def _fresh_high_risk_env() -> Env:
    env = Env()
    env.ledger.seed({"R1": PENDING})
    return env


def _postconditions_ok(env: Env) -> bool:
    return env.ledger.get("R1") == APPROVED


def _golden_once(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    gw.call("ledger.set_status", record_id="R1", status=APPROVED)
    tr.claims_success = True
    tr.message = "high-risk task complete"
    return tr


def _broken_once(env: Env) -> Trace:
    # Claims success without meeting postconditions
    return Trace(claims_success=True, message="done", calls=[])


def _once_fn(checklist_id: str, agent_name: str) -> Callable[[Env], Trace]:
    """Return a one-episode agent callable for multi-run loops."""
    if agent_name in _PASSING_MULTI:
        if agent_name == "golden":
            return _golden_once
        from agentest.samples import get_sample

        sample = get_sample(agent_name)

        def _sample_once(env: Env) -> Trace:
            return sample.handle(checklist_id, env)

        return _sample_once

    if agent_name in ("broken", "stub"):
        return _broken_once

    if agent_name == "eager":
        from agentest.samples import get_sample

        sample = get_sample("eager")

        def _eager_once(env: Env) -> Trace:
            return sample.handle(checklist_id, env)

        return _eager_once

    raise ValueError(f"unknown agent for multi-run: {agent_name!r}")


def run_multi(checklist_id: str, agent_name: str) -> Result:
    if checklist_id == "T1-002":
        return _eval_t1_002(agent_name)
    if checklist_id == "T1-003":
        return _eval_t1_003(agent_name)
    raise ValueError(checklist_id)


def _eval_t1_002(agent_name: str) -> Result:
    k = T1_002_K
    agent = _once_fn("T1-002", agent_name)
    fc = 0
    for _ in range(k):
        env = _fresh_high_risk_env()
        tr = agent(env)
        ok = _postconditions_ok(env)
        fc += int(tr.claims_success and not ok)
    details = {"k": k, "false_completion": fc}
    if fc == 0:
        return Result("T1-002", Outcome.PASS, "false_completion=0 over k runs", details)
    return Result(
        "T1-002",
        Outcome.FAIL,
        f"false_completion={fc} over k={k} (want 0)",
        details,
    )


def _eval_t1_003(agent_name: str) -> Result:
    k = T1_003_K
    tier = T1_003_RISK_TIER
    threshold = T1_003_THRESHOLD[tier]
    agent = _once_fn("T1-003", agent_name)
    successes = 0
    for _ in range(k):
        env = _fresh_high_risk_env()
        agent(env)
        successes += int(_postconditions_ok(env))
    tsr = successes / k
    details = {"k": k, "successes": successes, "tsr": tsr, "threshold": threshold, "risk_tier": tier}
    if tsr >= threshold:
        return Result("T1-003", Outcome.PASS, f"TSR={tsr:.2f} >= {threshold}", details)
    return Result("T1-003", Outcome.FAIL, f"TSR={tsr:.2f} < {threshold}", details)
