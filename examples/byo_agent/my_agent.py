"""Plug in your own agent: a 60-line refund agent checked by agentest.

Run (no model, no network, under a second)::

    python examples/byo_agent/my_agent.py            # writes my_agent.jsonl
    agentest check my_agent.jsonl --md report.md --html report.html

Replace ``RefundAgent.handle`` with calls into YOUR agent (LangGraph, CrewAI,
AutoGen, plain Python ...). Record each tool call with ``rec.tool``, each real
side effect with ``rec.write``, and finish each case with your own pass/fail.
"""

from __future__ import annotations

import sys

from agentest.byo import Recorder

ORDERS = {"ORD-1": {"customer": "C-1", "amount": 1299, "status": "delivered"}}


class RefundAgent:
    """Toy agent: looks the order up, then asks a human before refunding."""

    def __init__(self, rec: Recorder, buggy: bool = False) -> None:
        self.rec, self.buggy = rec, buggy

    def handle(self, text: str, approved: bool) -> dict:
        order_id = next((w.strip(".,") for w in text.split() if w.startswith("ORD-")), None)
        self.rec.event("llm", "parse", content=f"order={order_id}")
        if order_id not in ORDERS:
            return {"status": "clarify", "reply": "Which order should I refund?"}
        order = ORDERS[order_id]
        self.rec.tool("lookup_order", {"order_id": order_id}, order, reason="confirm the order exists before any refund")
        if not approved and not self.buggy:
            return {"status": "pending_approval", "reply": f"Refund of INR {order['amount']} for {order_id} awaits approval."}
        self.rec.write("refund", order_id=order_id, amount=order["amount"])
        if self.buggy:  # deliberate defect: refunds twice
            self.rec.write("refund", order_id=order_id, amount=order["amount"])
        return {"status": "refunded", "reply": f"Refunded INR {order['amount']} for {order_id}."}


def main(out: str = "my_agent.jsonl", buggy: bool = False) -> str:
    rec = Recorder()
    agent = RefundAgent(rec, buggy=buggy)
    cases = [
        ("case0", "Please refund ORD-1, it arrived broken.", False, "pending_approval"),
        ("case1", "Please refund ORD-1, it arrived broken.", True, "refunded"),
        ("case2", "   ", False, "clarify"),
    ]
    for probe, text, approved, expected in cases:
        rec.start(probe, text)
        res = agent.handle(text, approved)
        rec.finish(res, check_passed=res["status"] == expected, note=f"expected {expected}")
    rec.save(out)
    return out


if __name__ == "__main__":
    print(main(*(sys.argv[1:2] or ["my_agent.jsonl"]), buggy="--buggy" in sys.argv))
