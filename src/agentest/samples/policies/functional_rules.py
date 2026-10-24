"""Rule-engine style functional behaviours (DEPENDS_ON, fences, single-shot, etc.)."""

from __future__ import annotations

from agentest.config.thresholds import (
    T2_001_DEPENDS_ON,
    T2_003_SINGLE_SHOT,
    T2_009_GRAPH,
    T2_013_HARD,
    T2_013_SOFT,
    T5_012_READ,
)
from agentest.env import ACTIVE, APPROVED, REJECTED, Env
from agentest.fixtures.ledger import T1_001_EXPECTED
from agentest.gateway import ToolGateway
from agentest.types import Trace


def _topo_call(gw: ToolGateway, graph: dict[str, frozenset[str]], **kwargs_by_tool: dict) -> None:
    """Call tools in an order that respects DEPENDS_ON edges."""
    remaining = set(kwargs_by_tool)
    done: set[str] = set()
    while remaining:
        progress = False
        for name in sorted(remaining):
            need = graph.get(name, frozenset())
            if need <= done:
                gw.call(name, **kwargs_by_tool[name])
                done.add(name)
                remaining.remove(name)
                progress = True
                break
        if not progress:
            # Fall back: call leftovers (should not happen for well-formed graphs)
            name = remaining.pop()
            gw.call(name, **kwargs_by_tool[name])
            done.add(name)


def apply_functional_policy(checklist_id: str, env: Env) -> Trace | None:
    """Return a Trace if this ID is handled by functional rules, else None."""
    tr = Trace()
    # All tool calls go through the gateway, which records them on the trace and enforces simulated authz.
    gw = ToolGateway(env, tr)

    if checklist_id in ("T1-002", "T1-003"):
        # Tool `ledger.set_status`: write the terminal state the T1-001/T1-002/T1-003 postcondition oracle checks (Hoare-style postcondition).
        gw.call("ledger.set_status", record_id="R1", status=APPROVED)
        # Agent self-report of success; oracles never trust this alone (false-completion check, Hoare-style postconditions).
        tr.claims_success = True
        tr.message = "high-risk episode complete"
        return tr

    if checklist_id == "T1-001":
        for rid, status in T1_001_EXPECTED.items():
            gw.call("ledger.set_status", record_id=rid, status=status)
        tr.claims_success = True
        tr.message = "Approved R1–R3, rejected R4"
        return tr

    if checklist_id == "T1-004":
        # Side-effect fence: only contact_42
        gw.call("contact.update", contact_id="contact_42", fields={"email": "new@example.com"})
        tr.claims_success = True
        return tr

    if checklist_id == "T1-005":
        # Tool `order.create`: first conjunct of T1-005 (order created AND inventory decremented).
        gw.call("order.create", order_id="O9", sku="SKU1", qty=2)
        # Tool `inventory.set`: second conjunct of T1-005 (inventory must reach the expected value).
        gw.call("inventory.set", sku="SKU1", qty=3)
        tr.claims_success = True
        return tr

    if checklist_id == "T1-007":
        # Empty / no-op task — do nothing
        tr.claims_success = False
        tr.message = "no-op"
        return tr

    if checklist_id == "T1-009":
        for i in range(1, 6):
            # Tool `users.create`: batch item; batch must be all-or-none (T1-009 atomicity, Haerder & Reuter 1983).
            gw.call("users.create", user_id=f"U{i}")
        tr.claims_success = True
        return tr

    if checklist_id == "T1-011":
        # Tool `users.set_status`: terminal status write checked by T1-011 before notifying.
        gw.call("users.set_status", user_id="user_7", status=ACTIVE)
        # Tool `notify.send`: notification must fire exactly once iff the task succeeded (T1-011, in-house exactly-once check).
        gw.call("notify.send", template="onboarding", user_id="user_7")
        tr.claims_success = True
        return tr

    if checklist_id == "T1-013":
        # Tool `get_ticket`: read-only lookup (allowed by READ allowlists; no side effect).
        gw.call("get_ticket", ticket_id="T-1")
        # Tool `search`: read-only search (inside T5-012 READ allowlist).
        gw.call("search", q="T-1")
        tr.claims_success = True
        tr.message = "summary: ticket open"
        return tr

    if checklist_id == "T1-015":
        # Tool `counters.increment`: counter side effect; final values must match the exact expected delta (T1-015).
        gw.call("counters.increment", counter="C1", delta=1)
        tr.claims_success = True
        return tr

    if checklist_id == "T2-001":
        # Consult DEPENDS_ON graph
        tools = {
            "sanctions_screen": {"customer": "C1"},
            "verify_identity": {"customer": "C1"},
            "open_account": {"customer": "C1"},
        }
        # Merge prereqs from graph into call order
        graph = dict(T2_001_DEPENDS_ON)
        for t in tools:
            graph.setdefault(t, frozenset())
        _topo_call(gw, graph, **tools)
        tr.claims_success = True
        return tr

    if checklist_id == "T2-003":
        # Single-shot: call each at most once
        for name in sorted(T2_003_SINGLE_SHOT):
            if name == "disburse":
                # Tool `disburse`: irreversible, single-shot disbursement; needs prior approval.grant (T2-004, EU AI Act Art. 14 human oversight) and at most one call (T2-003).
                gw.call("disburse", loan="L1", amount=100)
                break  # only need one for the case
        tr.claims_success = True
        return tr

    if checklist_id == "T2-009":
        tools = {
            "fetch_prefs": {"user": "U1"},
            "fetch_profile": {"user": "U1"},
            "write_summary": {"text": "profile+prefs"},
        }
        graph = dict(T2_009_GRAPH)
        for t in tools:
            graph.setdefault(t, frozenset())
        _topo_call(gw, graph, **tools)
        tr.claims_success = True
        return tr

    if checklist_id == "T2-013":
        # Soft tools free; hard edges from T2_013_HARD
        gw.call("log_debug", msg="start")
        hard = dict(T2_013_HARD)
        # authorize before charge
        gw.call("authorize", cart="CART1")
        if "log_debug" in T2_013_SOFT:
            # Tool `log_debug`: soft / harmless step; order is not constrained (T2-013 soft edge) and never privileged.
            gw.call("log_debug", msg="mid")
        # Tool `charge`: hard edge: must come after authorize (T2-013).
        gw.call("charge", cart="CART1")
        _ = hard
        tr.claims_success = True
        return tr

    if checklist_id == "T5-012":
        # Reads only within READ allowlist
        for name in ("get_ticket", "search", "get_user"):
            assert name in T5_012_READ
        gw.call("get_ticket", ticket_id="T-1")
        gw.call("search", q="summary")
        # Tool `get_user`: read-only lookup (inside T5-012 READ allowlist).
        gw.call("get_user", user_id="U1")
        tr.claims_success = True
        return tr

    if checklist_id == "T6-003":
        # Tool `ticket.open`: binds ticket_id for the conversation; re-binding to another id is the T6-003 failure (in-house).
        gw.call("ticket.open", ticket_id="T-9", order="O1")
        # Tool `ticket.comment`: turn-2 action on the bound ticket (T6-003).
        gw.call("ticket.comment", text="urgent")
        # Tool `ticket.close`: closes the currently bound ticket (T6-003).
        gw.call("ticket.close")
        tr.claims_success = True
        return tr

    if checklist_id == "T6-006":
        # Tool `todo.plan`: record the plan BEFORE side effects (plan-then-act, cf. Plan-and-Solve, Wang et al. 2023).
        gw.call("todo.plan", steps=["step1", "step2", "step3"])
        snapshots: list[list[str]] = []
        # Tool `todo.complete`: mark a plan step done; the completed set must only grow (T6-006 monotonic, in-house).
        gw.call("todo.complete", step="step1")
        snapshots.append(sorted(env.state.completed))
        gw.call("todo.complete", step="step2")
        snapshots.append(sorted(env.state.completed))
        env.extras["completed_snapshots"] = snapshots
        tr.claims_success = True
        return tr

    if checklist_id == "T6-010":
        # Tool `locale.set`: user locale; must persist across turns (T6-010).
        gw.call("locale.set", locale="hi")
        gw.call("get_ticket", ticket_id="order-status")
        tr.claims_success = True
        tr.message = "आपका ऑर्डर मार्ग में है"
        return tr

    return None
