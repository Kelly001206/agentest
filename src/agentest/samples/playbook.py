"""Shared golden / broken playbook helpers for teaching sample agents."""

from __future__ import annotations

from agentest.env import APPROVED, Env
from agentest.gateway import ToolGateway
from agentest.samples.base import MULTI_RUN_EPISODE_IDS
from agentest.types import Trace


def play_golden(checklist_id: str, env: Env) -> Trace:
    """Run the case golden (or the multi-run high-risk episode)."""
    if checklist_id in MULTI_RUN_EPISODE_IDS:
        tr = Trace()
        gw = ToolGateway(env, tr)
        gw.call("ledger.set_status", record_id="R1", status=APPROVED)
        tr.claims_success = True
        tr.message = "high-risk task complete"
        return tr
    from agentest.cases.registry import get_case

    return get_case(checklist_id).golden(env)


def play_broken(checklist_id: str, env: Env) -> Trace:
    """Run the case broken sequence (guaranteed oracle Fail)."""
    from agentest.cases.registry import get_case

    return get_case(checklist_id).broken(env)


def play_selective(
    checklist_id: str,
    env: Env,
    *,
    fail_ids: frozenset[str],
) -> Trace:
    """Golden everywhere except ``fail_ids`` (those use broken)."""
    if checklist_id in fail_ids:
        return play_broken(checklist_id, env)
    return play_golden(checklist_id, env)
