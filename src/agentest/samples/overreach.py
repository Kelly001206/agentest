"""Complexity 14 — overreach (expected-fail): orchestration / authz anti-pattern.

Passes functional / privacy / bias. Fails orchestration IDs: trusts handover
prose, ambient authority, skips HITL, replays single-use approvals, ignores TTL.
(T3-006 also fails in the explainability suite count when listed there.)
"""

from __future__ import annotations

from agentest.cases.registry import ORCHESTRATION_IDS
from agentest.env import Env
from agentest.samples.base import SampleAgent
from agentest.samples.playbook import play_selective
from agentest.types import Trace

FAIL_IDS = frozenset(ORCHESTRATION_IDS)


class OverreachAgent(SampleAgent):
    name = "overreach"
    title = "Overreach (orchestration anti-pattern)"
    complexity = 14
    description = (
        "EXPECTED-FAIL: golden except orchestration IDs — ambient authz, skip "
        "HITL, trust prose, immortal session. Teaches orch/authz oracles."
    )

    def handle(self, checklist_id: str, env: Env) -> Trace:
        return play_selective(checklist_id, env, fail_ids=FAIL_IDS)
