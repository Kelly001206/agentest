"""Complexity 4 — policy / rule-engine agent.

Consults shared policy modules (DEPENDS_ON graphs, WRITE fences, soft_delete,
verify-before-disclose, single-shot, PII masking, bias labelers) rather than
blindly copying golden function bodies. Passes all suites when rules cover
functional + privacy + explainability + bias.

Scenario
--------
a rule-engine agent driven by samples/policies/* (functional, privacy, explainability, bias, orchestration rules).

Agent design
------------
dispatches each checklist ID to the matching apply_*_policy function, which encodes the rule (e.g. verify before disclose, tenant fence, approvals store) rather than replaying goldens.

Tests exercised / expected outcome
----------------------------------
every ID; expected ALL PASS.

Why
---
shows that explicit, auditable policy rules satisfy the catalogue - least privilege and complete mediation in code.

Attribution / References
------------------------
- In-house teaching design; references are for the general agent pattern it imitates (no LLM is used - the agent is deterministic).
- Saltzer, J. H., Schroeder, M. D. (1975). The protection of information in computer systems. Proceedings of the IEEE 63(9):1278-1308. https://doi.org/10.1109/PROC.1975.9939 (least privilege, complete mediation, fail-safe defaults)
- ISO/IEC 42001:2023 Information technology - Artificial intelligence - Management system (Annex A controls). https://www.iso.org/standard/81230.html
- Hub catalogue: Padmanabhuni, S. (2026). Agentic AI Assurance Test Taxonomy v1. Zenodo. https://doi.org/10.5281/zenodo.23587407

See docs/SAMPLE-AGENTS.md and docs/REFERENCES.md.
"""

from __future__ import annotations

from agentest.env import Env
from agentest.samples.base import SampleAgent
from agentest.samples.policies.bias_rules import apply_bias_policy
from agentest.samples.policies.explain_rules import apply_explain_policy
from agentest.samples.policies.functional_rules import apply_functional_policy
from agentest.samples.policies.orchestration_rules import apply_orchestration_policy
from agentest.samples.policies.privacy_rules import apply_privacy_policy
from agentest.types import Trace


class PolicyAgent(SampleAgent):
    name = "policy"
    title = "Policy rule-engine"
    complexity = 4
    description = (
        "Rule-engine: consults DEPENDS_ON graphs, write fences, soft-delete, "
        "verify-before-disclose, single-shot, PII mask, bias, and orchestration policies."
    )

    def handle(self, checklist_id: str, env: Env) -> Trace:
        # Rule engine: try each policy module in priority order; the first module that owns this ID returns a trace.
        for apply in (
            apply_orchestration_policy,
            apply_functional_policy,
            apply_privacy_policy,
            apply_explain_policy,
            apply_bias_policy,
        ):
            trace = apply(checklist_id, env)
            # A rule fired; return its trace unchanged (no explanation enrichment at this level).
            if trace is not None:
                return trace
        # Fallback for unknown IDs: claim without acting, so oracles will correctly FAIL it.
        return Trace(claims_success=True, message=f"policy: no rule for {checklist_id}")
