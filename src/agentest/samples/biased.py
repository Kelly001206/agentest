"""Complexity 13 — biased (expected-fail): bias / fairness anti-pattern.

Passes functional / privacy / explain / orch. Fails all bias_fairness IDs
with skewed metamorphic labels (Hinglish/ES asymmetry, demographic flip).
"""

from __future__ import annotations

from agentest.cases.registry import BIAS_FAIRNESS_IDS
from agentest.env import Env
from agentest.samples.base import SampleAgent
from agentest.samples.playbook import play_selective
from agentest.types import Trace

FAIL_IDS = frozenset(BIAS_FAIRNESS_IDS)


class BiasedAgent(SampleAgent):
    name = "biased"
    title = "Biased (fairness anti-pattern)"
    complexity = 13
    description = (
        "EXPECTED-FAIL: golden except bias_fairness IDs — skewed labels by "
        "locale/demographic. Teaches metamorphic fairness oracles."
    )

    def handle(self, checklist_id: str, env: Env) -> Trace:
        return play_selective(checklist_id, env, fail_ids=FAIL_IDS)
