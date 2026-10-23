"""T6 multi-turn state functional cases."""

from __future__ import annotations

from agentest.cases.registry import CaseSpec
from agentest.env import Env
from agentest.gateway import ToolGateway
from agentest.types import Outcome, Result, Trace


def _env() -> Env:
    return Env()


# --- T6-003 binding stability ---
def _golden_003(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    gw.call("ticket.open", ticket_id="T-9", order="O1")
    gw.call("ticket.comment", text="urgent")
    gw.call("ticket.close")
    tr.claims_success = True
    return tr


def _broken_003(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    gw.call("ticket.open", ticket_id="T-9", order="O1")
    gw.call("ticket.comment", text="urgent")
    # Switch binding to wrong id
    gw.call("ticket.open", ticket_id="T-OTHER", order="O2")
    gw.call("ticket.close")
    tr.claims_success = True
    return tr


def _oracle_003(env: Env, trace: Trace) -> Result:
    hist = env.state.binding_history.get("ticket_id", [])
    details = {"binding_history": hist, "bindings": dict(env.state.bindings)}
    if not hist:
        return Result("T6-003", Outcome.FAIL, "no ticket_id bindings recorded", details)
    if len(set(hist)) == 1:
        return Result("T6-003", Outcome.PASS, "ticket_id binding stable", details)
    return Result("T6-003", Outcome.FAIL, f"ticket_id switched across turns: {hist}", details)


# --- T6-006 completed monotonic ---
def _golden_006(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    gw.call("todo.plan", steps=["step1", "step2", "step3"])
    # Simulate turns: completed grows
    snapshots: list[set[str]] = []
    gw.call("todo.complete", step="step1")
    snapshots.append(set(env.state.completed))
    gw.call("todo.complete", step="step2")
    snapshots.append(set(env.state.completed))
    # Stash for oracle
    env.extras["completed_snapshots"] = [sorted(s) for s in snapshots]
    tr.claims_success = True
    return tr


def _broken_006(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    gw.call("todo.plan", steps=["step1", "step2", "step3"])
    gw.call("todo.complete", step="step1")
    gw.call("todo.complete", step="step2")
    snap1 = sorted(env.state.completed)
    gw.call("todo.drop", step="step1")  # shrinks completed
    snap2 = sorted(env.state.completed)
    env.extras["completed_snapshots"] = [snap1, snap2]
    tr.claims_success = True
    return tr


def _oracle_006(env: Env, trace: Trace) -> Result:
    snaps = env.extras.get("completed_snapshots")
    if not snaps:
        # Fall back: single final set is trivially monotonic
        snaps = [sorted(env.state.completed)]
    prev: set[str] = set()
    for raw in snaps:
        cur = set(raw)
        if not prev <= cur:
            details = {"snapshots": snaps}
            return Result("T6-006", Outcome.FAIL, "completed set shrank across turns", details)
        prev = cur
    return Result(
        "T6-006",
        Outcome.PASS,
        "completed grows monotonically",
        {"snapshots": snaps},
    )


# --- T6-010 locale persistence ---
def _golden_010(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    gw.call("locale.set", locale="hi")
    # Later turn: answer order status without resetting locale
    gw.call("get_ticket", ticket_id="order-status")
    tr.claims_success = True
    tr.message = "आपका ऑर्डर मार्ग में है"
    return tr


def _broken_010(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    gw.call("locale.set", locale="hi")
    gw.call("locale.set", locale="en")  # drift
    gw.call("get_ticket", ticket_id="order-status")
    tr.claims_success = True
    tr.message = "Your order is on the way"
    return tr


def _oracle_010(env: Env, trace: Trace) -> Result:
    details = {"locale": env.state.locale}
    if env.state.locale == "hi":
        return Result("T6-010", Outcome.PASS, "locale persisted as hi", details)
    return Result("T6-010", Outcome.FAIL, f"locale={env.state.locale!r} want 'hi'", details)


def all_cases() -> list[CaseSpec]:
    return [
        CaseSpec("T6-003", _env, _golden_003, _broken_003, _oracle_003),
        CaseSpec("T6-006", _env, _golden_006, _broken_006, _oracle_006),
        CaseSpec("T6-010", _env, _golden_010, _broken_010, _oracle_010),
    ]
