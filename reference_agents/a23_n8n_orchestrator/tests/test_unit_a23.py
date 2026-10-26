"""Offline unit tests (no n8n, no LLM): generated workflow structure and wiring."""
import os, sys, json, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.testing import load
B = load(__file__, module="build_workflows")

def test_build_and_wiring():
    d = tempfile.mkdtemp(); B.build(d)
    o = json.load(open(os.path.join(d, "orchestrator.n8n.json")))
    names = {n["name"]: n for n in o["nodes"]}
    assert len(o["id"]) == 16 and o["connections"]["Is refund?"]["main"][0][0]["node"] == "Run refund sub-workflow"
    for n in ("Run refund sub-workflow", "Run kb sub-workflow", "Run escalate sub-workflow"):
        assert os.path.exists(names[n]["parameters"]["workflowPath"])
    assert "127.0.0.1" in names["Classify (local LLM)"]["parameters"]["url"]

def test_route_allowlist_and_refund_pending_only():
    assert "ALLOWED = ['refund', 'kb', 'escalate']" in B.PARSE_JS and "escalate" in B.PARSE_JS
    assert "pending_approval" in B.REFUND_JS and "amount > 5000" in B.REFUND_JS
