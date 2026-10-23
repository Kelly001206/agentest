"""Complexity 11 — leaky (expected-fail): privacy anti-pattern.

Passes functional / explain / bias / orch via case goldens.
Fails every privacy ID with the case broken sequence (hard-delete,
disclose-before-verify, cross-tenant write/export, raw PII in tools,
post-revoke share, paraphrase leak).
"""

from __future__ import annotations

from agentest.cases.registry import PRIVACY_IDS
from agentest.env import Env
from agentest.samples.base import SampleAgent
from agentest.samples.playbook import play_selective
from agentest.types import Trace

FAIL_IDS = frozenset(PRIVACY_IDS)


class LeakyAgent(SampleAgent):
    name = "leaky"
    title = "Leaky (privacy anti-pattern)"
    complexity = 11
    description = (
        "EXPECTED-FAIL: golden playbook except privacy IDs — logs/exports PII, "
        "hard-deletes, cross-tenant writes. Teaches privacy oracles."
    )

    def handle(self, checklist_id: str, env: Env) -> Trace:
        return play_selective(checklist_id, env, fail_ids=FAIL_IDS)
