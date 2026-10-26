"""Offline unit tests (no LLM): BM25 retrieval and the citation verifier."""
import os, sys, pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.testing import load
from common.runtime import InputError
A = load(__file__)

def test_bm25_finds_acquisition(): assert A.INDEX.search("acquired Kestrel Payments")[0]["id"] == "D1"
def test_bm25_finds_hq(): assert A.INDEX.search("Orion Fintech headquartered")[0]["id"] == "D2"
def test_bm25_no_match(): assert A.INDEX.search("zzzz qqqq") == []
def test_verifier_ok(): assert A.verify_citations("Hyderabad [D1][D2]", {"D1", "D2"})["valid"]
def test_verifier_rejects_unretrieved(): assert not A.verify_citations("x [D5]", {"D1"})["valid"]
def test_verifier_rejects_untrusted(): assert A.verify_citations("x [D7]", {"D7"})["invalid"] == ["D7"]
def test_verifier_requires_citation(): assert not A.verify_citations("Hyderabad", {"D1"})["valid"]
def test_validation():
    with pytest.raises(InputError): A.run("hi")
