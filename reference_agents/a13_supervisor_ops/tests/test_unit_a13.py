"""Offline unit tests (no LLM): tools, approval gating, validation."""
import os, sys, pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.testing import load
A = load(__file__); make_tools, Ledger = A.make_tools, A.Ledger
from common.runtime import ApprovalGate, validate_text, InputError

def t(pending, name): return {x.name: x for v in make_tools(pending).values() for x in v}[name]

def test_credit_note_only_pending():
    p = []; r = t(p, "issue_credit_note").fn(invoice_id="INV-7", amount=4999)
    assert r["status"] == "PENDING_HUMAN_APPROVAL" and len(p) == 1

def test_credit_note_amount_bounds_and_dedupe():
    p = []; tool = t(p, "issue_credit_note")
    assert "error" in tool.fn(invoice_id="INV-7", amount=999999)
    tool.fn(invoice_id="INV-7", amount=10); assert tool.fn(invoice_id="INV-7", amount=10)["status"].startswith("already")

def test_account_withholds_contact():
    r = t([], "get_account").fn(account_id="ACC-3")
    assert "email" not in r and "phone" not in r

def test_gate_requires_exact_token_and_no_replay():
    g = ApprovalGate(); q = g.request("issue_credit_note", "INV-7")
    assert not g.check(q, None)
    assert not g.check(q, {"approver": "finance-head", "token": "ok approve"})
    assert not g.check(q, {"approver": "random", "token": q["expected_token"]})
    assert g.check(q, {"approver": "finance-head", "token": q["expected_token"]})
    assert not g.check(q, {"approver": "finance-head", "token": q["expected_token"]})

def test_ledger_execute():
    l = Ledger(); assert l.execute({"args": {"invoice_id": "INV-7", "amount": 1}})["credit_note"] == "CN-1"

def test_validation():
    with pytest.raises(InputError): validate_text("   ")
    with pytest.raises(InputError): validate_text("x" * 7000)
