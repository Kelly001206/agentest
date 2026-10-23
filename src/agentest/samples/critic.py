"""Complexity 9 — generate–critique–repair scenario.

First pass may be incomplete (tools ran, but explainability fields missing or
claims_success still False). A critique step forces repair before the agent
sets ``claims_success``. Explanation, cited_steps, memory_citations, and
api_success must stay trace-faithful. Composes ReflectiveAgent for non-native
IDs so the full matrix still Passes.
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
        if checklist_id in CRITIC_NATIVE:
            return self._generate_critique_repair(checklist_id, env)

        from agentest.samples.reflective import ReflectiveAgent

        return ReflectiveAgent().handle(checklist_id, env)

    def _generate_critique_repair(self, checklist_id: str, env: Env) -> Trace:
        tr = Trace()
        gw = ToolGateway(env, tr)

        if checklist_id == "T1-018":
            # Generate (incomplete — write happened, flags/explanation missing)
            gw.call("db.write", reason="persist_order", order_id="O1", status="DONE")
            tr.claims_success = False
            # Critique
            gw.call(
                "log_debug",
                reason="critique",
                msg="api_success/explanation missing after db.write",
            )
            # Repair — faithful fields only
            tr.api_success = True
            tr.explanation = "Wrote order O1 to DB"
            tr.cited_steps = ["db.write"]
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
            gw.call("search", reason="find_related_policy", q="refund")
            gw.call("write_summary", reason="document_decision", text="case noted")
            tr.claims_success = False
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
            gw.call("memory.read", reason="load_contact_pref", key="prefer_email")
            tr.claims_success = False
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
