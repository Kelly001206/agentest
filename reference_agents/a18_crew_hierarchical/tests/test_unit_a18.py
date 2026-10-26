"""Offline unit tests (no LLM): deterministic onboarding policy guard and validation."""
import os, sys, pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.testing import load
from common.runtime import InputError
A = load(__file__)

def test_guard_clean(): assert A.policy_guard("Sahyadri Cloud Services")["allowed"]
def test_guard_sanctions(): assert A.policy_guard("Volga Edge Networks")["reason"] == "sanctions hit"
def test_guard_cert(): assert A.policy_guard("Bluepeak Analytics")["reason"] == "missing ISO 27001"
def test_guard_unknown(): assert not A.policy_guard("Nobody Ltd")["allowed"]
def test_crew_is_hierarchical():
    from crewai import Process
    c = A.build_crew(A.AgentConfig()); assert c.process == Process.hierarchical and len(c.agents) == 3
def test_validation():
    with pytest.raises(InputError): A.run("ok", "")
