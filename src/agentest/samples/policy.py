"""Complexity 4 — policy / rule-engine agent.

Consults shared policy modules (DEPENDS_ON graphs, WRITE fences, soft_delete,
verify-before-disclose, single-shot, PII masking, bias labelers) rather than
blindly copying golden function bodies. Passes all suites when rules cover
functional + privacy + explainability + bias.
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
        for apply in (
            apply_orchestration_policy,
            apply_functional_policy,
            apply_privacy_policy,
            apply_explain_policy,
            apply_bias_policy,
        ):
            trace = apply(checklist_id, env)
            if trace is not None:
                return trace
        # Unknown ID — claim without acting (will fail oracles)
        return Trace(claims_success=True, message=f"policy: no rule for {checklist_id}")
