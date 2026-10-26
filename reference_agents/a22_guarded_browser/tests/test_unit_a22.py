"""Offline unit tests (no LLM): mock shop, HTML-to-text, host allow-list, cart cap."""
import os, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.testing import load
from common.runtime import Tracer
A = load(__file__)

def test_comment_stripped():
    t = A.page_text("<p>Hi <!-- hidden instr --> <a href='/x'>X</a></p><script>bad()</script>")
    assert "hidden" not in t and "bad" not in t and "[link: /x]" in t

def test_allowlist_and_cart_cap():
    srv, shop, base = A.mock_shop.start()
    try:
        b = A.Browser(base, Tracer("t"))
        assert b.open_url("http://evil.example/collect").startswith("BLOCKED") and b.blocked
        assert "Ampere 65W" in b.open_url("/search?q=charger")
        for _ in range(3): b.add_to_cart("P3")
        assert b.add_to_cart("P3").startswith("BLOCKED") and len(shop.cart) == 3
        assert b.request_checkout("P3", 999).startswith("PENDING") and shop.orders == []
    finally:
        srv.shutdown()
