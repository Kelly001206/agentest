"""Offline unit tests (no LLM): runbook allow-list and pending-only remediation."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.testing import load
A = load(__file__)

def test_destructive_refused():
    r = A.Remediations(); assert r.propose("drop_database", "orders-db", "x").startswith("REFUSED") and r.pending == [] and r.refused
def test_unknown_service():
    r = A.Remediations(); assert r.propose("restart_service", "mainframe", "x").startswith("REFUSED")
def test_pending_only():
    r = A.Remediations(); assert r.propose("Rollback_Deploy", "checkout-api", "bad deploy").startswith("PENDING") and r.pending[0]["action"] == "rollback_deploy"
