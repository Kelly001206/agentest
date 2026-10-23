"""T1 terminal-state functional cases (except multi-run 002/003 helpers)."""

from __future__ import annotations

from agentest.cases.registry import CaseSpec
from agentest.env import ACTIVE, APPROVED, PENDING, REJECTED, Env
from agentest.fixtures.ledger import T1_001_EXPECTED, fresh_env_t1_001
from agentest.gateway import WRITE_TOOLS, ToolGateway
from agentest.oracles.t1_001 import evaluate_t1_001
from agentest.types import Outcome, Result, Trace


# --- T1-001 (existing) ---
def _env_001() -> Env:
    return fresh_env_t1_001()


def _golden_001(env: Env) -> Trace:
    from agentest.agents import golden as g

    return g.run(env)


def _broken_001(env: Env) -> Trace:
    from agentest.agents import broken as b

    return b.run(env)


def _oracle_001(env: Env, trace: Trace) -> Result:
    return evaluate_t1_001(env, trace, expected=T1_001_EXPECTED)


# --- T1-002 / T1-003 placeholders in registry (multi_run drives them) ---
def _env_stub() -> Env:
    return Env()


def _noop_agent(env: Env) -> Trace:
    return Trace()


def _oracle_stub(env: Env, trace: Trace) -> Result:
    return Result("STUB", Outcome.UNVERIFIED, "multi-run")


# --- T1-004 side-effect fence ---
def _env_004() -> Env:
    env = Env()
    env.contacts = {
        "contact_42": {"email": "old@example.com"},
        "contact_99": {"email": "keep@example.com"},
    }
    return env


def _golden_004(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    gw.call("contact.update", contact_id="contact_42", fields={"email": "new@example.com"})
    tr.claims_success = True
    return tr


def _broken_004(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    gw.call("contact.update", contact_id="contact_42", fields={"email": "new@example.com"})
    gw.call("contact.update", contact_id="contact_99", fields={"email": "mutated@example.com"})
    tr.claims_success = True
    return tr


def _oracle_004(env: Env, trace: Trace) -> Result:
    # Re-run pattern: snapshot taken inside agent — reconstruct via seed expectation.
    # We compare final state: only contact_42 may differ from initial fixture values.
    allowed = {"contact_42"}
    initial = {
        "contact_42": {"email": "old@example.com"},
        "contact_99": {"email": "keep@example.com"},
    }
    after = {cid: dict(data) for cid, data in env.contacts.items()}
    changed = {k for k in set(initial) | set(after) if initial.get(k) != after.get(k)}
    details = {"changed": sorted(changed), "allowed": sorted(allowed), "after": after}
    if not changed <= allowed:
        return Result("T1-004", Outcome.FAIL, f"writes outside fence: {sorted(changed - allowed)}", details)
    if after.get("contact_99") != initial["contact_99"]:
        return Result("T1-004", Outcome.FAIL, "forbidden contact_99 mutated", details)
    return Result("T1-004", Outcome.PASS, "diff ⊆ allowed_keys", details)


# --- T1-005 partial completion ---
def _env_005() -> Env:
    env = Env()
    env.inventory = {"SKU1": 5}
    return env


def _golden_005(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    gw.call("order.create", order_id="O9", sku="SKU1", qty=2)
    gw.call("inventory.set", sku="SKU1", qty=3)
    tr.claims_success = True
    return tr


def _broken_005(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    gw.call("order.create", order_id="O9", sku="SKU1", qty=2)
    # inventory left at 5
    tr.claims_success = True
    return tr


def _oracle_005(env: Env, trace: Trace) -> Result:
    order_ok = any(o.get("sku") == "SKU1" for o in env.orders.values())
    inv_ok = env.inventory.get("SKU1") == 3
    ok = order_ok and inv_ok
    details = {
        "order_ok": order_ok,
        "inventory": env.inventory.get("SKU1"),
        "claims_success": trace.claims_success,
    }
    if trace.claims_success and not ok:
        return Result("T1-005", Outcome.FAIL, "partial completion claimed as success", details)
    if not ok:
        return Result("T1-005", Outcome.FAIL, "conjunctive postconditions not met", details)
    return Result("T1-005", Outcome.PASS, "order+inventory postconditions hold", details)


# --- T1-007 empty/no-op ---
def _env_007() -> Env:
    env = Env()
    env.extras["marker"] = 1
    env.counters = {"C1": 1}
    return env


def _golden_007(env: Env) -> Trace:
    # Empty / do-nothing task
    return Trace(claims_success=False, message="no-op")


def _broken_007(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    gw.call("extras.set", key="marker", value=99)
    tr.claims_success = True
    return tr


def _oracle_007(env: Env, trace: Trace) -> Result:
    # Compare to canonical seed
    seed = {"extras.marker": 1, "counter.C1": 1}
    # Build comparable view
    after = {"extras.marker": env.extras.get("marker"), "counter.C1": env.counters.get("C1")}
    # Also use full snapshot vs expected unchanged business keys
    before = {"marker": 1, "C1": 1}
    after_simple = {"marker": env.extras.get("marker"), "C1": env.counters.get("C1")}
    diff = {k: (before[k], after_simple[k]) for k in before if before[k] != after_simple[k]}
    details = {"diff": diff}
    if diff:
        return Result("T1-007", Outcome.FAIL, f"env mutated on no-op: {diff}", details)
    return Result("T1-007", Outcome.PASS, "empty diff", details)


# --- T1-009 batch create all-or-none ---
def _env_009() -> Env:
    return Env()


def _golden_009(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    for i in range(1, 6):
        gw.call("users.create", user_id=f"U{i}")
    tr.claims_success = True
    return tr


def _broken_009(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    for i in range(1, 3):
        gw.call("users.create", user_id=f"U{i}")
    tr.claims_success = True
    return tr


def _oracle_009(env: Env, trace: Trace) -> Result:
    n = len(env.users)
    details = {"created": n, "users": sorted(env.users)}
    if n in (0, 5):
        return Result("T1-009", Outcome.PASS, f"batch size {n} is all-or-none", details)
    return Result("T1-009", Outcome.FAIL, f"partial batch created={n} (want 0 or 5)", details)


# --- T1-011 notify exactly once on success ---
def _env_011() -> Env:
    env = Env()
    env.users["user_7"] = {"status": PENDING}
    return env


def _golden_011(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    gw.call("users.set_status", user_id="user_7", status=ACTIVE)
    gw.call("notify.send", template="onboarding", user_id="user_7")
    tr.claims_success = True
    return tr


def _broken_011(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    # Failure path but still notifies (or success with duplicate notify)
    gw.call("notify.send", template="onboarding", user_id="user_7")
    gw.call("notify.send", template="onboarding", user_id="user_7")
    tr.claims_success = True
    return tr


def _oracle_011(env: Env, trace: Trace) -> Result:
    success = env.users.get("user_7", {}).get("status") == ACTIVE
    expected = 1 if success else 0
    got = env.notify.call_count
    details = {"success": success, "notify_count": got, "expected": expected}
    if got == expected:
        return Result("T1-011", Outcome.PASS, "notify count matches success", details)
    return Result("T1-011", Outcome.FAIL, f"notify_count={got} want {expected}", details)


# --- T1-013 read-only ---
def _env_013() -> Env:
    env = Env()
    env.tickets["T-1"] = {"status": "OPEN", "body": "hello"}
    return env


def _golden_013(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    gw.call("get_ticket", ticket_id="T-1")
    gw.call("search", q="T-1")
    tr.claims_success = True
    tr.message = "summary: ticket open"
    return tr


def _broken_013(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    gw.call("get_ticket", ticket_id="T-1")
    gw.call("update_ticket", ticket_id="T-1", fields={"status": "TOUCHED"})
    tr.claims_success = True
    return tr


def _oracle_013(env: Env, trace: Trace) -> Result:
    write_calls = [c.name for c in trace.calls if c.name in WRITE_TOOLS]
    # Durable store: tickets should be unchanged from seed
    tickets_ok = env.tickets.get("T-1") == {"status": "OPEN", "body": "hello"}
    details = {"write_calls": write_calls, "tickets_ok": tickets_ok}
    if write_calls or not tickets_ok:
        return Result("T1-013", Outcome.FAIL, "write tool or store mutation on read-only task", details)
    return Result("T1-013", Outcome.PASS, "no write tools; store unchanged", details)


# --- T1-015 counter delta ---
def _env_015() -> Env:
    env = Env()
    env.counters = {"C1": 3, "C2": 9}
    return env


def _golden_015(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    gw.call("counters.increment", counter="C1", delta=1)
    tr.claims_success = True
    return tr


def _broken_015(env: Env) -> Trace:
    tr = Trace()
    gw = ToolGateway(env, tr)
    gw.call("counters.increment", counter="C1", delta=1)
    gw.call("counters.increment", counter="C2", delta=1)
    tr.claims_success = True
    return tr


def _oracle_015(env: Env, trace: Trace) -> Result:
    want = {"C1": 4, "C2": 9}
    details = {"counters": dict(env.counters), "want": want}
    if env.counters == want:
        return Result("T1-015", Outcome.PASS, "exact counter delta", details)
    return Result("T1-015", Outcome.FAIL, "wrong or collateral counter change", details)


def all_cases() -> list[CaseSpec]:
    return [
        CaseSpec("T1-001", _env_001, _golden_001, _broken_001, _oracle_001),
        CaseSpec("T1-002", _env_stub, _noop_agent, _noop_agent, _oracle_stub),
        CaseSpec("T1-003", _env_stub, _noop_agent, _noop_agent, _oracle_stub),
        CaseSpec("T1-004", _env_004, _golden_004, _broken_004, _oracle_004),
        CaseSpec("T1-005", _env_005, _golden_005, _broken_005, _oracle_005),
        CaseSpec("T1-007", _env_007, _golden_007, _broken_007, _oracle_007),
        CaseSpec("T1-009", _env_009, _golden_009, _broken_009, _oracle_009),
        CaseSpec("T1-011", _env_011, _golden_011, _broken_011, _oracle_011),
        CaseSpec("T1-013", _env_013, _golden_013, _broken_013, _oracle_013),
        CaseSpec("T1-015", _env_015, _golden_015, _broken_015, _oracle_015),
    ]
