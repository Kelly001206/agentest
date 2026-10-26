"""Offline unit tests (no LLM): MCP server tool functions and the approval step."""
import os, sys, json, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.testing import load
from common.runtime import Tracer
A = load(__file__)
L = load(__file__, "logistics_server")

def test_inventory_pending_only(tmp_path, monkeypatch):
    monkeypatch.setenv("A16_PENDING", str(tmp_path / "p.json"))
    I = load(__file__, "inventory_server"); I.PENDING = str(tmp_path / "p.json")
    assert json.loads(I.request_transfer("SKU-200", "PNQ-1", "BLR-1", 30))["status"] == "PENDING_HUMAN_APPROVAL"
    assert "error" in json.loads(I.request_transfer("SKU-100", "PNQ-1", "BLR-1", 99))
    assert I.STOCK["SKU-200"]["PNQ-1"] == 120  # nothing moved

def test_lane_quote():
    assert json.loads(L.quote_lane("BLR-1", "PNQ-1", 20)) == {"from": "BLR-1", "to": "PNQ-1", "days": 2, "total_cost": 700}

def test_approval_exact(tmp_path):
    p = tmp_path / "p.json"; p.write_text(json.dumps([{"sku": "SKU-200", "from_wh": "PNQ-1", "to_wh": "BLR-1", "qty": 30}]))
    _, done, _ = A.approve_and_execute(str(p), [{"approver": "ops-lead", "token": "APPROVE transfer SKU-200:PNQ-1->BLR-1:30"}], Tracer("t"))
    assert len(done) == 1
    _, done, audit = A.approve_and_execute(str(p), [{"approver": "ops-lead", "token": "APPROVE transfer SKU-200:PNQ-1->BLR-1:300"}], Tracer("t"))
    assert done == [] and audit[0]["granted"] is False
