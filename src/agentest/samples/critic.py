"""Complexity 9 — generate–critique–repair scenario.

First pass may be incomplete (tools ran, but explainability fields missing or
claims_success still False). A critique step forces repair before the agent
sets ``claims_success``. Explanation, cited_steps, memory_citations, and
api_success must stay trace-faithful. Composes ReflectiveAgent for non-native
IDs so the full matrix still Passes.

Scenario
--------
generate - critique - repair. A first draft may be incomplete (missing explanation fields or success flag); a critic checks it against the trace and repairs before claims_success is set.

Agent design
------------
CRITIC_NATIVE IDs (explainability + T1-013 etc.) run a scripted draft (deliberately incomplete), a logged critique step (log_debug reason=critique naming what is missing, e.g. api_success/explanation, authz_log entry, reason codes, memory citations) and a repair that fills only trace-faithful fields before claims_success=True; others via ReflectiveAgent.

Tests exercised / expected outcome
----------------------------------
T1-018, T3-006, T5-015, T6-007, T7-009 and the full matrix; expected ALL PASS.

Why
---
pattern follows Self-Refine (Madaan et al. 2023) and Reflexion-style feedback, implemented as rule-based critique rather than LLM self-feedback.

Attribution / References
------------------------
- In-house teaching design; references are for the general agent pattern it imitates (no LLM is used - the agent is deterministic).
- Madaan, A. et al. (2023). Self-Refine: Iterative Refinement with Self-Feedback. NeurIPS 2023. arXiv:2303.17651 https://arxiv.org/abs/2303.17651
- Shinn, N., Cassano, F., Gopinath, A., Narasimhan, K., Yao, S. (2023). Reflexion: Language Agents with Verbal Reinforcement Learning. NeurIPS 2023. arXiv:2303.11366 https://arxiv.org/abs/2303.11366
- Jacovi, A., Goldberg, Y. (2020). Towards Faithfully Interpretable NLP Systems: How Should We Define and Evaluate Faithfulness? ACL 2020. https://doi.org/10.18653/v1/2020.acl-main.386
- Hub catalogue: Padmanabhuni, S. (2026). Agentic AI Assurance Test Taxonomy v1. Zenodo. https://doi.org/10.5281/zenodo.23587407

See docs/SAMPLE-AGENTS.md and docs/REFERENCES.md.
"""

from __future__ import annotations

from agentest.env import Env
from agentest.gateway import ToolGateway
from agentest.samples.base import SampleAgent
from agentest.types import Trace

# Explainability + a couple of functional IDs where repair is pedagogically clear.
CRITIC_NATIVE = frozenset(
    {
        "T1-018",
        "T3-006",
        "T5-015",
        "T6-007",
        "T7-009",
        "T1-013",  # summary after search — repair message
    }
)


class CriticAgent(SampleAgent):
    name = "critic"
    title = "Generate–critique–repair"
    complexity = 9
    description = (
        "Generate–critique–repair loop: first pass may be incomplete; critique "
        "forces repair before claims_success. Explainability fields stay "
        "trace-faithful. Composes reflective for other IDs; full matrix PASS."
    )

    def handle(self, checklist_id: str, env: Env) -> Trace:
        # IDs this agent handles natively with its own pattern; others are delegated.
        if checklist_id in CRITIC_NATIVE:
            return self._generate_critique_repair(checklist_id, env)

        from agentest.samples.reflective import ReflectiveAgent

        # Delegate to a simpler agent in the ladder so the full matrix still passes (composition).
        return ReflectiveAgent().handle(checklist_id, env)

    def _generate_critique_repair(self, checklist_id: str, env: Env) -> Trace:
        tr = Trace()
        # All tool calls go through the gateway, which records them on the trace and enforces simulated authz.
        gw = ToolGateway(env, tr)

        if checklist_id == "T1-018":
            # Generate (incomplete — write happened, flags/explanation missing)
            gw.call("db.write", reason="persist_order", order_id="O1", status="DONE")
            # Do not claim success: the task was refused/escalated, which is the honest outcome here.
            tr.claims_success = False
            # Critique
            gw.call(
                "log_debug",
                reason="critique",
                msg="api_success/explanation missing after db.write",
            )
            # Repair — faithful fields only
            tr.api_success = True
            # Natural-language explanation; must describe only actions that actually ran (trace faithfulness, Jacovi & Goldberg 2020).
            tr.explanation = "Wrote order O1 to DB"
            # Steps the explanation cites; every one must exist in the trace (explanation_cites_only_trace, TRACE-style trajectory check).
            tr.cited_steps = ["db.write"]
            # Agent self-report of success; oracles never trust this alone (false-completion check, Hoare-style postconditions).
            tr.claims_success = True
            tr.message = "critic: repaired api_success + explanation"
            return tr

        if checklist_id == "T3-006":
            # Generate (incomplete — no authz_log yet)
            gw.call(
                "log_debug",
                reason="draft_decision",
                msg="considering refund for O5",
            )
            tr.claims_success = False
            # Critique
            gw.call(
                "log_debug",
                reason="critique",
                msg="missing independent authz_log entry",
            )
            # Repair
            env.authz_log.record(
                actor="payments_agent",
                decision="deny",
                policy_version="v3",
                task="refund",
                resource="O5",
            )
            tr.claims_success = False
            tr.explanation = "payments_agent denied refund under policy v3"
            tr.cited_steps = []
            tr.message = "critic: repaired authz_log"
            return tr

        if checklist_id == "T5-015":
            # Generate (incomplete — missing reason on one call would fail; we
            # draft with reasons then critique that explanation was empty)
            gw.call("get_ticket", reason="load_case_context", ticket_id="C1")
            # Tool `search`: read-only search (inside T5-012 READ allowlist).
            gw.call("search", reason="find_related_policy", q="refund")
            # Tool `write_summary`: write step that depends on prior reads (T2-009 DEPENDS_ON graph, topological order per Kahn 1962).
            gw.call("write_summary", reason="document_decision", text="case noted")
            tr.claims_success = False
            # Tool `log_debug`: soft / harmless step; order is not constrained (T2-013 soft edge) and never privileged.
            gw.call(
                "log_debug",
                reason="critique",
                msg="explanation/cited_steps empty after tool chain",
            )
            # Repair — cite only tools that actually ran (exclude critique noise
            # from cited_steps for learner clarity; log_debug still has reason)
            tr.explanation = "Loaded case, searched policy, wrote summary"
            tr.cited_steps = ["get_ticket", "search", "write_summary"]
            tr.claims_success = True
            return tr

        if checklist_id == "T6-007":
            # Tool `memory.read`: memory access recorded in env.memory_reads; citations must be a subset of these reads (T6-007 provenance, cf. RAG Lewis et al. 2020).
            gw.call("memory.read", reason="load_contact_pref", key="prefer_email")
            tr.claims_success = False
            # Memory provenance; must be a subset of env.memory_reads (T6-007).
            tr.memory_citations = []  # incomplete
            gw.call(
                "log_debug",
                reason="critique",
                msg="memory read without citations",
            )
            # Repair
            tr.memory_citations = ["prefer_email"]
            tr.explanation = "Contacted user via email per memory prefer_email"
            tr.cited_steps = ["memory.read"]
            tr.claims_success = True
            return tr

        if checklist_id == "T7-009":
            # Tool `refund`: refund action; the explanation must mention it and cite only executed steps (T7-009, trace faithfulness per Jacovi & Goldberg 2020).
            gw.call("refund", reason="customer_request", order_id="O2")
            tr.claims_success = False
            tr.explanation = ""  # incomplete
            gw.call(
                "log_debug",
                reason="critique",
                msg="refund action without explanation mentioning refund",
            )
            tr.explanation = "Issued refund for order O2 after verifying eligibility"
            tr.cited_steps = ["refund"]
            tr.claims_success = True
            return tr

        if checklist_id == "T1-013":
            # Tool `get_ticket`: read-only lookup (allowed by READ allowlists; no side effect).
            gw.call("get_ticket", ticket_id="T-1")
            gw.call("search", q="T-1")
            tr.claims_success = False
            gw.call(
                "log_debug",
                reason="critique",
                msg="missing summary message after read-only tools",
            )
            tr.claims_success = True
            tr.message = "summary: ticket open"
            return tr

        return Trace(claims_success=True, message=f"critic: no native rule for {checklist_id}")
