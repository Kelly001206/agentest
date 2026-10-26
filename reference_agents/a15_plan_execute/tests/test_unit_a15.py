"""Offline unit tests (no LLM): mock tools, policy, validation."""
import os, sys, pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.testing import load
from common.runtime import InputError
A = load(__file__)

def test_past_date_refused(): assert "error" in A.search_flights("DEL", "IXL", "2026-10-01")
def test_flight_found(): assert A.search_flights("bom", "blr", "2026-11-12")["results"]
def test_whitefield_sold_out(): assert A.search_hotels("Whitefield", "2026-11-12", 6000)["results"] == []
def test_price_filter(): assert [h["hotel"] for h in A.search_hotels("indiranagar", "x", 6000)["results"]] == ["Lotus Residency"]
def test_unknown_area(): assert "error" in A.search_hotels("mars", "x", 1)
def test_policy_caps():
    assert A.check_policy("hotel", 5999)["allowed"] and not A.check_policy("hotel", 14500)["allowed"] and not A.check_policy("yacht", 1)["allowed"]
def test_validation():
    with pytest.raises(InputError): A.run("")

def test_hold_must_match_a_search_result():
    hold_is_grounded = A.hold_is_grounded
    done = [{"tool": "search_hotels", "result": {"results": [{"hotel": "Lotus Residency", "price": 5200}]}}]
    assert hold_is_grounded({"kind": "hotel", "item": "Lotus Residency", "price": 5200}, done)
    assert not hold_is_grounded({"kind": "hotel", "item": "hotel123", "price": 5500}, done)
    assert not hold_is_grounded({"kind": "hotel", "item": "Lotus Residency", "price": 100}, done)
    assert not hold_is_grounded({"kind": "hotel", "item": "Lotus Residency", "price": None}, done)
    flights = [{"tool": "search_flights", "result": {"results": [{"flight": "6E-512", "fare": 4300}]}}]
    assert hold_is_grounded({"kind": "flight", "item": "6E-512", "price": 4300}, flights)
