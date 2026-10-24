"""Complexity 15 — flaky_plan (expected-fail): incomplete planning / handoff.

Passes most IDs via golden. Fails a planning-focused subset: DEPENDS_ON /
order mistakes (T2-*), half-done todo plan (T6-006), and HITL-before-act /
side-effect without plan (T3-010, T2-004). Deterministic “half-done” profile
— not random flake.

Scenario
--------
EXPECTED-FAIL: half-done planning / handoff (deterministic, not random).

Agent design
------------
play_selective with broken sequences on T2-001/003/009/013, T6-006, T2-004, T3-010.

Tests exercised / expected outcome
----------------------------------
fails that 7-ID planning subset; others pass.

Why
---
Why it must fail: plan ordering, monotonic progress and HITL-before-act are checked independently of final success.

Attribution / References
------------------------
- In-house teaching design; references are for the general agent pattern it imitates (no LLM is used - the agent is deterministic).
- Wang, L., Xu, W., Lan, Y., Hu, Z., Lan, Y., Lee, R. K.-W., Lim, E.-P. (2023). Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models. ACL 2023. arXiv:2305.04091
- Kahn, A. B. (1962). Topological sorting of large networks. Communications of the ACM 5(11):558-562. https://doi.org/10.1145/368996.369025
- Hardt, D. (Ed.) (2012). RFC 6749: The OAuth 2.0 Authorization Framework, sec. 4.1.2 (authorization code MUST NOT be used more than once). https://doi.org/10.17487/RFC6749
- Hub catalogue: Padmanabhuni, S. (2026). Agentic AI Assurance Test Taxonomy v1. Zenodo. https://doi.org/10.5281/zenodo.23587407

See docs/SAMPLE-AGENTS.md and docs/REFERENCES.md.
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
        # Golden trajectory for most IDs, broken trajectory for FAIL_IDS: a deterministic expected-fail profile.
        return play_selective(checklist_id, env, fail_ids=FAIL_IDS)
