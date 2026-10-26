"""Complexity 5 — reflective agent (policy + explainability + bias awareness).

Builds on the policy rule-engine, then enriches traces with explanation
strings, memory_citations, cited_steps, and api_success alignment. Most
complete teaching agent; must PASS all checklist IDs including orchestration.

Scenario
--------
policy agent plus a reflection step that writes faithful explanations, reason codes, memory citations and consistent bias labels.

Agent design
------------
applies the policies/* rule modules, then enrich_explainability() post-processes the trace and fills explanation / cited_steps / memory_citations only from steps that actually ran.

Tests exercised / expected outcome
----------------------------------
all IDs, notably explainability (T1-018, T3-006, T5-015, T6-007, T7-009) and bias (T7-004/007/011); expected ALL PASS.

Why
---
explanation fields derived from the trace are faithful by construction (Jacovi & Goldberg 2020). The post-hoc self-inspection loosely mirrors Reflexion-style self-reflection, without any learning or LLM.

Attribution / References
------------------------
- In-house teaching design; references are for the general agent pattern it imitates (no LLM is used - the agent is deterministic).
- Jacovi, A., Goldberg, Y. (2020). Towards Faithfully Interpretable NLP Systems: How Should We Define and Evaluate Faithfulness? ACL 2020. https://doi.org/10.18653/v1/2020.acl-main.386
- Shinn, N., Cassano, F., Gopinath, A., Narasimhan, K., Yao, S. (2023). Reflexion: Language Agents with Verbal Reinforcement Learning. NeurIPS 2023. arXiv:2303.11366 https://arxiv.org/abs/2303.11366
- Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., Cao, Y. (2023). ReAct: Synergizing Reasoning and Acting in Language Models. ICLR 2023. arXiv:2210.03629 https://arxiv.org/abs/2210.03629
- catalogue: Padmanabhuni, S. (2026). Agentic AI Assurance Test Taxonomy v1. Zenodo. https://doi.org/10.5281/zenodo.23587407

See docs/SAMPLE-AGENTS.md and docs/REFERENCES.md.
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
from agentest.samples.policies.orchestration_rules import apply_orchestration_policy
from agentest.samples.policies.privacy_rules import apply_privacy_policy
from agentest.types import Trace


class ReflectiveAgent(SampleAgent):
    """Sample agent; behaviour and defect profile described in the module docstring."""

    name = "reflective"
    title = "Reflective (policy + explain + bias)"
    complexity = 5
    description = (
        "Policy rules plus faithful explanations, memory citations, "
        "api_success alignment, and bias-aware decisions. Passes all IDs including orchestration."
    )

    def handle(self, checklist_id: str, env: Env) -> Trace:
        # Same rule engine as PolicyAgent, but explain/bias modules first so their native fields are produced.
        """Run one episode for ``checklist_id`` with this agent's behaviour profile."""
        for apply in (
            apply_orchestration_policy,
            apply_explain_policy,
            apply_bias_policy,
            apply_functional_policy,
            apply_privacy_policy,
        ):
            trace = apply(checklist_id, env)
            if trace is not None:
                # Reflection step: derive explanation/cited_steps/memory_citations from the executed trace only (faithful by construction; loosely Reflexion-style self-inspection, Shinn et al. 2023).
                return enrich_explainability(checklist_id, env, trace)
        # Fallback: unknown ID - oracles will FAIL this claim.
        return Trace(claims_success=True, message=f"reflective: no rule for {checklist_id}")
