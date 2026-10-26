"""Offline unit tests for common/runtime.py (shared by A13-A25)."""
import os, sys, json, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import pytest
from common.runtime import parse_json, validate_text, InputError, ApprovalGate, redact_pii, with_retries, AgentConfig, Tracer

def test_parse_json_outermost_wins():
    assert parse_json('[{"tool":"a","args":{}}]') == [{"tool": "a", "args": {}}]   # regression: used to return the inner dict
    assert parse_json('text {"a": [1]} more') == {"a": [1]}
    assert parse_json("```json\n[1, 2]\n```") == [1, 2] and parse_json("none", "d") == "d"

def test_validate_text():
    assert validate_text("  hi ") == "hi"
    for bad in ("", None, "x" * 7000):
        with pytest.raises(InputError): validate_text(bad)

def test_gate():
    g = ApprovalGate(); q = g.request("refund", "ORD-1")
    assert not g.check(q, None) and not g.check(q, {"approver": "intern", "token": "APPROVE refund ORD-1"})
    assert not g.check(q, {"approver": "ops-lead", "token": "approve refund ORD-1"})
    assert g.check(q, {"approver": "ops-lead", "token": "APPROVE refund ORD-1"})
    assert not g.check(q, {"approver": "ops-lead", "token": "APPROVE refund ORD-1"})  # replay
    g2 = ApprovalGate(ttl_s=0.001); q2 = g2.request("a", "b"); time.sleep(0.01)
    assert not g2.check(q2, {"approver": "ops-lead", "token": "APPROVE a b"})

def test_redact_and_retries_and_config():
    r = redact_pii("call +91 98765 43210 card 4111111111111111")
    assert "98765" not in r and "4111111111111111" not in r
    n = {"c": 0}
    def f():
        n["c"] += 1
        if n["c"] < 2: raise TimeoutError("x")
        return "ok"
    assert with_retries(f, retries=2, base_delay=0.01) == "ok" and n["c"] == 2
    with pytest.raises(Exception): AgentConfig(timeout_s=0)
