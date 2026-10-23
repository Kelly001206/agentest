"""Complexity 15 — flaky_plan (expected-fail): incomplete planning / handoff.

Passes most IDs via golden. Fails a planning-focused subset: DEPENDS_ON /
order mistakes (T2-*), half-done todo plan (T6-006), and HITL-before-act /
side-effect without plan (T3-010, T2-004). Deterministic “half-done” profile
— not random flake.
"""

from __future__ import annotations

from agentest.env import Env
from agentest.samples.base import SampleAgent
from agentest.samples.playbook import play_selective
from agentest.types import Trace

# Planning / handoff half-done — mix of functional + orchestration.
FAIL_IDS = frozenset(
    {
        "T2-001",
        "T2-003",
        "T2-009",
        "T2-013",
        "T6-006",
        "T2-004",
        "T3-010",
    }
)


class FlakyPlanAgent(SampleAgent):
    name = "flaky_plan"
    title = "Flaky plan (planning anti-pattern)"
    complexity = 15
    description = (
        "EXPECTED-FAIL: golden except plan/DEPENDS_ON/HITL subset — skips "
        "todo.plan, wrong order, half-done repair. Teaches T2 + orch plan oracles."
    )

    def handle(self, checklist_id: str, env: Env) -> Trace:
        return play_selective(checklist_id, env, fail_ids=FAIL_IDS)
