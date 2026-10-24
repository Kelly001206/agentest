"""Shared golden / broken playbook helpers for teaching sample agents."""

from __future__ import annotations

from agentest.env import APPROVED, Env
from agentest.gateway import ToolGateway
from agentest.samples.base import MULTI_RUN_EPISODE_IDS
from agentest.types import Trace


def play_golden(checklist_id: str, env: Env) -> Trace:
    """Run the case golden (or the multi-run high-risk episode)."""
    # Multi-run IDs (T1-002/T1-003) use one high-risk episode per run instead of a CaseSpec golden.
    if checklist_id in MULTI_RUN_EPISODE_IDS:
        tr = Trace()
        # All tool calls go through the gateway, which records them on the trace and enforces simulated authz.
        gw = ToolGateway(env, tr)
        # Tool `ledger.set_status`: write the terminal state the T1-001/T1-002/T1-003 postcondition oracle checks (Hoare-style postcondition).
        gw.call("ledger.set_status", record_id="R1", status=APPROVED)
        # Agent self-report of success; oracles never trust this alone (false-completion check, Hoare-style postconditions).
        tr.claims_success = True
        tr.message = "high-risk task complete"
        return tr
    from agentest.cases.registry import get_case

    # Look up the case spec to replay its reference trajectory.
    return get_case(checklist_id).golden(env)


def play_broken(checklist_id: str, env: Env) -> Trace:
    """Run the case broken sequence (guaranteed oracle Fail)."""
    from agentest.cases.registry import get_case

    # Look up the case spec and replay its seeded-defect (broken) trajectory.
    return get_case(checklist_id).broken(env)


def play_selective(
    checklist_id: str,
    env: Env,
    *,
    fail_ids: frozenset[str],
) -> Trace:
    """Golden everywhere except ``fail_ids`` (those use broken)."""
    # Expected-fail band: run the seeded-defect sequence for the targeted IDs only.
    if checklist_id in fail_ids:
        return play_broken(checklist_id, env)
    # All other IDs: correct reference trajectory, so failures stay isolated to the taught category.
    return play_golden(checklist_id, env)
