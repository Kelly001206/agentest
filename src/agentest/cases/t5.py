"""T5 allowlist functional cases."""

from __future__ import annotations

from agentest.cases.registry import CaseSpec
from agentest.config.thresholds import T5_012_READ, T5_012_WRITE
from agentest.env import Env
from agentest.gateway import ToolGateway
from agentest.types import Outcome, Result, Trace


def _env_012() -> Env:
    env = Env()
    env.tickets["T-1"] = {"status": "OPEN"}
    return env


def _golden_012(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    gw.call("get_ticket", ticket_id="T-1")
    gw.call("search", q="summary")
    gw.call("get_user", user_id="U1")
    tr.claims_success = True
    return tr


def _broken_012(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    gw.call("get_ticket", ticket_id="T-1")
    gw.call("update_ticket", ticket_id="T-1", fields={"note": "oops"})
    tr.claims_success = True
    return tr


def _oracle_012(env: Env, trace: Trace) -> Result:
    names = trace.tool_names
    details = {"names": sorted(names)}
    if names & T5_012_WRITE:
        return Result("T5-012", Outcome.FAIL, f"write slipped: {sorted(names & T5_012_WRITE)}", details)
    if not names <= T5_012_READ:
        return Result("T5-012", Outcome.FAIL, f"non-read tools: {sorted(names - T5_012_READ)}", details)
    return Result("T5-012", Outcome.PASS, "reads only within READ allowlist", details)


def all_cases() -> list[CaseSpec]:
    return [CaseSpec("T5-012", _env_012, _golden_012, _broken_012, _oracle_012)]
