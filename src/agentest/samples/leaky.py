"""Complexity 11 — leaky (expected-fail): privacy anti-pattern.

Passes functional / explain / bias / orch via case goldens.
Fails every privacy ID with the case broken sequence (hard-delete,
disclose-before-verify, cross-tenant write/export, raw PII in tools,
post-revoke share, paraphrase leak).

Scenario
--------
EXPECTED-FAIL: privacy anti-pattern.

Agent design
------------
play_selective - golden sequence for every ID except PRIVACY_IDS, where the case's broken sequence runs (hard delete, disclose before verify, cross-tenant write/export, raw SSN in tool args, injected exfiltration email, post-revoke share, paraphrase leak).

Tests exercised / expected outcome
----------------------------------
fails all 8 privacy IDs (T1-016, T2-005, T3-008, T4-009, T5-004, T5-011, T6-004, T7-014); other suites pass.

Why
---
Why it must fail: proves privacy oracles fire independently of functional success.

Attribution / References
------------------------
- In-house teaching design; references are for the general agent pattern it imitates (no LLM is used - the agent is deterministic).
- Greshake, K., Abdelnabi, S., Mishra, S., Endres, C., Holz, T., Fritz, M. (2023). Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection. AISec '23 (ACM CCS workshop). https://doi.org/10.1145/3605764.3623985 / arXiv:2302.12173
- McCallister, E., Grance, T., Scarfone, K. (2010). NIST SP 800-122: Guide to Protecting the Confidentiality of PII. https://doi.org/10.6028/NIST.SP.800-122
- Regulation (EU) 2016/679 (GDPR). https://eur-lex.europa.eu/eli/reg/2016/679/oj
- Hub catalogue: Padmanabhuni, S. (2026). Agentic AI Assurance Test Taxonomy v1. Zenodo. https://doi.org/10.5281/zenodo.23587407

See docs/SAMPLE-AGENTS.md and docs/REFERENCES.md.
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
        # Golden trajectory for most IDs, broken trajectory for FAIL_IDS: a deterministic expected-fail profile.
        return play_selective(checklist_id, env, fail_ids=FAIL_IDS)
