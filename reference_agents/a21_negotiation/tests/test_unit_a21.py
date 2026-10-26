"""Offline unit tests (no LLM): hard negotiation limits in the Ledger."""
import os, sys, pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.testing import load
A = load(__file__)

def test_offer_above_ceiling_refused():
    l = A.Ledger(900, 10); assert l.make_offer(950).startswith("REFUSED") and l.offers == []
def test_offers_monotonic():
    l = A.Ledger(900, 10); l.make_offer(700); assert l.make_offer(650).startswith("REFUSED")
def test_accept_creates_pending_only():
    l = A.Ledger(900, 10); assert "DEAL_PENDING_APPROVAL" in l.accept_offer(850) and l.pending_po["total"] == 8500
def test_accept_above_ceiling():
    l = A.Ledger(900, 10); assert l.accept_offer(901).startswith("REFUSED") and l.pending_po is None
def test_bad_ledger():
    with pytest.raises(ValueError): A.Ledger(0, 1)
