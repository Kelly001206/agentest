"""Complexity 12 — hallucinator (expected-fail): explainability anti-pattern.

Passes most suites via goldens. Fails every explainability ID: claims API
success without db.write, fake citations, missing tool reasons, silent
memory use, invented tools in explanations.
"""

from __future__ import annotations

from agentest.cases.registry import EXPLAINABILITY_IDS
from agentest.env import Env
from agentest.samples.base import SampleAgent
from agentest.samples.playbook import play_selective
from agentest.types import Trace

FAIL_IDS = frozenset(EXPLAINABILITY_IDS)


class HallucinatorAgent(SampleAgent):
    name = "hallucinator"
    title = "Hallucinator (explainability anti-pattern)"
    complexity = 12
    description = (
        "EXPECTED-FAIL: golden except explainability IDs — fake citations, "
        "api_success without tools, silent memory. Teaches faithfulness oracles."
    )

    def handle(self, checklist_id: str, env: Env) -> Trace:
        return play_selective(checklist_id, env, fail_ids=FAIL_IDS)
