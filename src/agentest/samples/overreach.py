"""Complexity 14 — overreach (expected-fail): orchestration / authz anti-pattern.

Passes functional / privacy / bias. Fails orchestration IDs: trusts handover
prose, ambient authority, skips HITL, replays single-use approvals, ignores TTL.
(T3-006 also fails in the explainability suite count when listed there.)

Scenario
--------
EXPECTED-FAIL: orchestration / authorization anti-pattern.

Agent design
------------
play_selective with broken sequences on ORCHESTRATION_IDS: trusts handover prose, ambient authority, privileged use after downgrade, token replay, ignores TTL, disburses without HITL, no independent authz log.

Tests exercised / expected outcome
----------------------------------
fails all 8 orchestration IDs; others pass.

Why
---
Why it must fail: excessive agency and confused-deputy behaviour.

Attribution / References
------------------------
- In-house teaching design; references are for the general agent pattern it imitates (no LLM is used - the agent is deterministic).
- Hardy, N. (1988). The Confused Deputy (or why capabilities might have been invented). ACM SIGOPS Operating Systems Review 22(4):36-38. https://doi.org/10.1145/54289.871709
- OWASP Top 10 for LLM Applications 2025 (LLM01 Prompt Injection, LLM02 Sensitive Information Disclosure, LLM06 Excessive Agency). https://genai.owasp.org/llm-top-10/
- Regulation (EU) 2024/1689 (EU AI Act), Art. 14 Human oversight. https://eur-lex.europa.eu/eli/reg/2024/1689/oj
- catalogue: Padmanabhuni, S. (2026). Agentic AI Assurance Test Taxonomy v1. Zenodo. https://doi.org/10.5281/zenodo.23587407

See docs/SAMPLE-AGENTS.md and docs/REFERENCES.md.
"""

from __future__ import annotations

from agentest.cases.registry import ORCHESTRATION_IDS
from agentest.env import Env
from agentest.samples.base import SampleAgent
from agentest.samples.playbook import play_selective
from agentest.types import Trace

FAIL_IDS = frozenset(ORCHESTRATION_IDS)


class OverreachAgent(SampleAgent):
    """Sample agent; behaviour and defect profile described in the module docstring."""

    name = "overreach"
    title = "Overreach (orchestration anti-pattern)"
    complexity = 14
    description = (
        "EXPECTED-FAIL: golden except orchestration IDs — ambient authz, skip "
        "HITL, trust prose, immortal session. Teaches orch/authz oracles."
    )

    def handle(self, checklist_id: str, env: Env) -> Trace:
        # Golden trajectory for most IDs, broken trajectory for FAIL_IDS: a deterministic expected-fail profile.
        """Run one episode for ``checklist_id`` with this agent's behaviour profile."""
        return play_selective(checklist_id, env, fail_ids=FAIL_IDS)
