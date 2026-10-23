"""Complexity 5 — reflective agent (policy + explainability + bias awareness).

Builds on the policy rule-engine, then enriches traces with explanation
strings, memory_citations, cited_steps, and api_success alignment. Most
complete teaching agent; must PASS all 34 checklist IDs.
"""

from __future__ import annotations

from agentest.env import Env
from agentest.samples.base import SampleAgent
from agentest.samples.policies.bias_rules import apply_bias_policy
from agentest.samples.policies.explain_rules import (
    apply_explain_policy,
    enrich_explainability,
)
from agentest.samples.policies.functional_rules import apply_functional_policy
from agentest.samples.policies.privacy_rules import apply_privacy_policy
from agentest.types import Trace


class ReflectiveAgent(SampleAgent):
    name = "reflective"
    title = "Reflective (policy + explain + bias)"
    complexity = 5
    description = (
        "Policy rules plus faithful explanations, memory citations, "
        "api_success alignment, and bias-aware decisions. Passes all 34 IDs."
    )

    def handle(self, checklist_id: str, env: Env) -> Trace:
        # Prefer explain/bias modules first so enrichment fields are native
        for apply in (
            apply_explain_policy,
            apply_bias_policy,
            apply_functional_policy,
            apply_privacy_policy,
        ):
            trace = apply(checklist_id, env)
            if trace is not None:
                return enrich_explainability(checklist_id, env, trace)
        return Trace(claims_success=True, message=f"reflective: no rule for {checklist_id}")
