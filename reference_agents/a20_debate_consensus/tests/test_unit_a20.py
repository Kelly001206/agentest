"""Offline unit tests (no LLM): consensus parser and policy cap."""
import os, sys, pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.testing import load
A = load(__file__)

def test_parse_ok(): assert A.parse_consensus('x CONSENSUS: {"decision": "Approve", "limit": "4,000,000"}') == {"decision": "approve", "limit": 4000000}
def test_parse_bad_decision(): assert A.parse_consensus('CONSENSUS: {"decision": "maybe", "limit": 1}') is None
def test_parse_missing(): assert A.parse_consensus("we agree") is None
def test_cap(): assert A.policy_cap({"annual_revenue": 30000000, "dscr": 1.8, "defaults_24m": 0}) == 6000000
def test_cap_zero_on_default(): assert A.policy_cap({"annual_revenue": 1e7, "dscr": 2, "defaults_24m": 1}) == 0
def test_missing_field():
    with pytest.raises(ValueError): A.run({"applicant": "x"})
