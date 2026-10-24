"""Complexity 3 — scripted playbook agent.

For each known checklist_id, plays the case's golden sequence via
``get_case(id).golden(env)``. This is the honest "hardcoded playbook"
teaching step before building a rule engine (policy) or reflective layer.

Multi-run IDs (T1-002/T1-003): case golden is a noop stub; we play the
canonical high-risk episode (approve R1) so multi_run can loop k times.

Scenario
--------
a hard-coded playbook that replays each case's golden sequence.

Agent design
------------
handle() looks up CASE_REGISTRY[id].golden(env) (see playbook.py).

Tests exercised / expected outcome
----------------------------------
every ID; expected ALL PASS (in MATRIX_MUST_PASS).

Why
---
baseline proving the oracles accept a correct trajectory.

Attribution / References
------------------------
- In-house teaching design; references are for the general agent pattern it imitates (no LLM is used - the agent is deterministic).

- Hub catalogue: Padmanabhuni, S. (2026). Agentic AI Assurance Test Taxonomy v1. Zenodo. https://doi.org/10.5281/zenodo.23587407

See docs/SAMPLE-AGENTS.md and docs/REFERENCES.md.
"""

from __future__ import annotations

from agentest.env import APPROVED, Env
from agentest.gateway import ToolGateway
from agentest.samples.base import MULTI_RUN_EPISODE_IDS, SampleAgent
from agentest.types import Trace


class ScriptedAgent(SampleAgent):
    name = "scripted"
    title = "Scripted playbook"
    complexity = 3
    description = (
        "Dispatch table: for each checklist ID, run the case golden sequence "
        "(reference playbook). Passes all checklist IDs (incl. orchestration via golden) — teaching step before policy."
    )

    def handle(self, checklist_id: str, env: Env) -> Trace:
        if checklist_id in MULTI_RUN_EPISODE_IDS:
            tr = Trace()
            gw = ToolGateway(env, tr)
            gw.call("ledger.set_status", record_id="R1", status=APPROVED)
            tr.claims_success = True
            tr.message = "high-risk task complete"
            return tr

        from agentest.cases.registry import get_case

        case = get_case(checklist_id)
        return case.golden(env)
