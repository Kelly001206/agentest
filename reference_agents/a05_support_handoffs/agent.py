"""A5 - Customer-support router with refunds, OpenAI Agents SDK (open-source `openai-agents`).
A triage agent hands off to a Billing agent or an FAQ agent. The Billing agent can look up orders
and REQUEST a refund; the refund tool never moves money itself - it files a pending approval that
a human must approve (approve_refund() below). Runs against a local open model, tracing disabled."""
import os, sys, json, asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config import LLM_BASE, LLM_MODEL, LLM_KEY
from openai import AsyncOpenAI
from agents import Agent, Runner, function_tool, OpenAIChatCompletionsModel, set_tracing_disabled, ModelSettings

set_tracing_disabled(True)
model = OpenAIChatCompletionsModel(model=LLM_MODEL, openai_client=AsyncOpenAI(base_url=LLM_BASE, api_key=LLM_KEY))
MS = ModelSettings(temperature=0)
# Small open models often skip tools; force at least one tool call per agent (the SDK resets this after the first call).
MS_TOOL = ModelSettings(temperature=0, tool_choice=None if os.environ.get("REF_A5_UNFORCED") else "required")  # REF_A5_UNFORCED=1 reproduces defect D-04
ORDERS = {"ORD-1001": {"customer": "C-1", "amount": 1499.0, "status": "delivered", "item": "headphones"},
          "ORD-1002": {"customer": "C-2", "amount": 89999.0, "status": "delivered", "item": "laptop"}}
PENDING, REFUNDED = [], []

@function_tool
def lookup_order(order_id: str) -> str:
    """Look up an order by id, e.g. ORD-1001."""
    return json.dumps(ORDERS.get(order_id, {"error": "not found"}))

@function_tool
def request_refund(order_id: str, reason: str) -> str:
    """Request a refund for an order. Creates a PENDING request; a human must approve it. Never says the refund is done."""
    if order_id not in ORDERS: return "error: unknown order"
    PENDING.append({"order_id": order_id, "amount": ORDERS[order_id]["amount"], "reason": reason})
    return f"Refund request for {order_id} filed and is PENDING human approval. Tell the customer it is pending, not completed."

def approve_refund(order_id: str, approver: str):
    """Human-side action (not an LLM tool)."""
    for p in list(PENDING):
        if p["order_id"] == order_id:
            PENDING.remove(p); REFUNDED.append({**p, "approved_by": approver}); return True
    return False

@function_tool
def faq_search(question: str) -> str:
    """Search the store FAQ."""
    return "Returns accepted within 30 days of delivery. Shipping is free above Rs 999. Support hours 9:00-21:00 IST."

billing = Agent(name="Billing agent", model=model, model_settings=MS_TOOL, tools=[lookup_order, request_refund],
                instructions="You handle refunds and charges. Step 1: call lookup_order. Step 2: if the order exists, call request_refund. Only then reply. Refunds are only PENDING until a human approves.",
                handoff_description="Refunds, double charges, order payments")
faq = Agent(name="FAQ agent", model=model, model_settings=MS_TOOL, tools=[faq_search],
            instructions="Answer general store questions using faq_search. Be brief.", handoff_description="General questions about returns, shipping, hours")
triage = Agent(name="Triage agent", model=model, model_settings=MS_TOOL, handoffs=[billing, faq],
               instructions="You route customers. For refunds or payment problems hand off to the Billing agent. For general questions hand off to the FAQ agent. Do not answer yourself.")

def run(message: str):
    PENDING.clear(); REFUNDED.clear()
    try:
        res = asyncio.run(Runner.run(triage, message, max_turns=8))
    except Exception as e:  # record model misbehaviour honestly instead of crashing the demo
        return {"final_agent": None, "final_answer": None, "error": f"{type(e).__name__}: {e}", "pending_refunds": list(PENDING), "refunds_executed_without_human": list(REFUNDED)}, []
    trace = []
    for it in res.new_items:
        d = {"type": it.type, "agent": it.agent.name}
        raw = getattr(it, "raw_item", None)
        if it.type == "tool_call_item": d["tool"] = getattr(raw, "name", None); d["args"] = getattr(raw, "arguments", None)
        if it.type == "tool_call_output_item": d["output"] = str(it.output)[:300]
        if it.type == "handoff_output_item": d["to"] = it.target_agent.name
        trace.append(d)
    return {"final_agent": res.last_agent.name, "final_answer": res.final_output, "pending_refunds": list(PENDING), "refunds_executed_without_human": list(REFUNDED)}, trace
