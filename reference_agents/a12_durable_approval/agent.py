"""A12 - Long-running approval workflow (finance/ops) in LangGraph with a durable SQLite checkpointer.
extract (LLM -> JSON) -> vendor_check (MCP tool over stdio) -> policy (code) -> approval (interrupt, MANDATORY)
-> pay (function call writing to a mock ledger) | reject.
State survives process restarts: the graph can pause in one process and be resumed in another with the same thread_id."""
import os, sys, json, re, sqlite3, asyncio, datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import TypedDict
from common.config import LLM_BASE, LLM_MODEL, LLM_KEY
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import interrupt
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = os.path.dirname(os.path.abspath(__file__))
CKPT = os.environ.get("A12_CKPT", os.path.join(HERE, "checkpoints.sqlite"))
LEDGER = os.environ.get("A12_LEDGER", os.path.join(HERE, "ledger.sqlite"))
llm = ChatOpenAI(model=LLM_MODEL, base_url=LLM_BASE, api_key=LLM_KEY, temperature=0, max_tokens=200)

class S(TypedDict, total=False):
    invoice_text: str; invoice: dict; vendor: dict; policy: dict; approval: dict; result: str; log: list

def extract(s: S):
    raw = llm.invoke([("system", "Extract from the invoice text a JSON object with keys vendor (string), invoice_no (string), amount (number, INR). Output only JSON."),
                      ("user", s["invoice_text"])]).content
    m = re.search(r"\{.*\}", raw, re.S)
    try: inv = json.loads(m.group(0))
    except Exception: inv = {"vendor": None, "invoice_no": None, "amount": None, "parse_error": raw[:200]}
    return {"invoice": inv, "log": [{"node": "extract", "invoice": inv}]}

async def _mcp_lookup(name):
    p = StdioServerParameters(command=sys.executable, args=[os.path.join(HERE, "vendor_mcp_server.py")])
    async with stdio_client(p) as (r, w):
        async with ClientSession(r, w) as sess:
            await sess.initialize()
            res = await sess.call_tool("lookup_vendor", {"name": name or ""})
            return json.loads(res.content[0].text)

def vendor_check(s: S):
    v = asyncio.run(_mcp_lookup(s["invoice"].get("vendor")))
    return {"vendor": v, "log": s["log"] + [{"node": "vendor_check(mcp)", "vendor": v}]}

def policy(s: S):
    amt, v = s["invoice"].get("amount") or 0, s["vendor"]
    reasons = []
    if v.get("status") != "active": reasons.append(f"vendor status {v.get('status')}")
    if not v.get("bank_verified"): reasons.append("bank not verified")
    if amt > v.get("limit", 0): reasons.append(f"amount {amt} exceeds vendor limit {v.get('limit', 0)}")
    p = {"auto_reject": bool(reasons), "reasons": reasons}
    return {"policy": p, "log": s["log"] + [{"node": "policy", **p}]}

def route(s: S): return "reject" if s["policy"]["auto_reject"] else "approval"

def approval(s: S):
    inv = s["invoice"]
    reply = interrupt({"ask": "Approve payment?", "invoice_no": inv.get("invoice_no"), "vendor": inv.get("vendor"), "amount": inv.get("amount"),
                       "expected_token": "APPROVE <invoice_no> <amount>"})
    expected = f"APPROVE {inv.get('invoice_no')} {inv.get('amount')}"
    ok = isinstance(reply, dict) and reply.get("token", "").strip() == expected and reply.get("approver")
    a = {"granted": bool(ok), "reply": reply, "expected": expected}
    return {"approval": a, "log": s["log"] + [{"node": "approval", **a}]}

def after_approval(s: S): return "pay" if s["approval"]["granted"] else "reject"

def pay(s: S):
    c = sqlite3.connect(LEDGER); c.execute("CREATE TABLE IF NOT EXISTS payments(invoice_no TEXT UNIQUE, vendor TEXT, amount REAL, approver TEXT, ts TEXT)")
    inv = s["invoice"]
    try:
        c.execute("INSERT INTO payments VALUES (?,?,?,?,?)", (inv["invoice_no"], inv["vendor"], inv["amount"], s["approval"]["reply"]["approver"], datetime.datetime.now().isoformat()))
        c.commit(); r = "PAID"
    except sqlite3.IntegrityError:
        r = "DUPLICATE: already paid, nothing written"
    c.close()
    return {"result": r, "log": s["log"] + [{"node": "pay", "result": r}]}

def reject(s: S):
    return {"result": "REJECTED", "log": s["log"] + [{"node": "reject"}]}

def build(saver):
    g = StateGraph(S)
    for n, f in [("extract", extract), ("vendor_check", vendor_check), ("policy", policy), ("approval", approval), ("pay", pay), ("reject", reject)]:
        g.add_node(n, f)
    g.add_edge(START, "extract"); g.add_edge("extract", "vendor_check"); g.add_edge("vendor_check", "policy")
    g.add_conditional_edges("policy", route, ["approval", "reject"]); g.add_conditional_edges("approval", after_approval, ["pay", "reject"])
    g.add_edge("pay", END); g.add_edge("reject", END)
    return g.compile(checkpointer=saver)

def ledger_rows():
    if not os.path.exists(LEDGER): return []
    c = sqlite3.connect(LEDGER)
    try: return [list(r) for r in c.execute("SELECT invoice_no, vendor, amount, approver FROM payments")]
    except sqlite3.OperationalError: return []
