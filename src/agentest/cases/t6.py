"""T6 multi-turn state functional cases.

Each oracle below documents: Hub catalogue ID(s), the algorithm step by step,
thresholds and rationale, pass/fail interpretation, limitations, and an
Attribution / References section (published method vs in-house heuristic).
Full verified bibliography: docs/REFERENCES.md.
"""

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
    """T6-003 oracle: entity binding (ticket_id) stays stable across turns.

    Hub catalogue ID(s): T6-003

    Algorithm (step by step):
    1. Read env.state.binding_history['ticket_id'].
    2. Empty -> FAIL (nothing bound).
    3. If all bindings identical -> PASS; else FAIL (binding switched).

    Thresholds / rationale: Exactly one distinct value allowed.

    Pass / fail interpretation: FAIL = agent drifted to another ticket mid-conversation.

    Limitations: Only tracks the ticket_id slot.

    Attribution / References:
    - In-house heuristic: this check is our own deterministic design (not a published algorithm); references below are conceptual background only.
    - Padmanabhuni, S. (2026). Agentic AI Assurance Test Taxonomy v1. Zenodo. https://doi.org/10.5281/zenodo.23587407 (Hub catalogue: https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110)
    """
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
    """T6-006 oracle: the set of completed plan steps grows monotonically.

    Hub catalogue ID(s): T6-006

    Algorithm (step by step):
    1. Read completed_snapshots recorded per turn (fallback: final set).
    2. For consecutive snapshots require prev subset-of cur.
    3. Any shrink -> FAIL; else PASS.

    Thresholds / rationale: Monotonic (subset) ordering; no completed step may be dropped.

    Pass / fail interpretation: FAIL = agent 'forgot' completed work.

    Limitations: Relies on snapshots the agent records.

    Attribution / References:
    - In-house heuristic: this check is our own deterministic design (not a published algorithm); references below are conceptual background only.
    - Padmanabhuni, S. (2026). Agentic AI Assurance Test Taxonomy v1. Zenodo. https://doi.org/10.5281/zenodo.23587407 (Hub catalogue: https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110)
    """
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
    """T6-010 oracle: user-selected locale (hi) persists across later turns.

    Hub catalogue ID(s): T6-010

    Algorithm (step by step):
    1. Read env.state.locale at end of run.
    2. == 'hi' -> PASS, else FAIL.

    Thresholds / rationale: Exact match.

    Pass / fail interpretation: FAIL = silent locale drift.

    Limitations: Does not check message language itself.

    Attribution / References:
    - In-house heuristic: this check is our own deterministic design (not a published algorithm); references below are conceptual background only.
    - Padmanabhuni, S. (2026). Agentic AI Assurance Test Taxonomy v1. Zenodo. https://doi.org/10.5281/zenodo.23587407 (Hub catalogue: https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110)
    """
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
