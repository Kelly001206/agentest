"""MCP server 1 (stdio): warehouse inventory. Reads are free. `request_transfer` only records a
PENDING transfer in pending.json - it never moves stock. Execution happens outside the agent,
after a human approval (see agent.approve_and_execute)."""
import json, os, sys
from mcp.server.fastmcp import FastMCP
HERE = os.path.dirname(os.path.abspath(__file__))
PENDING = os.environ.get("A16_PENDING", os.path.join(HERE, "pending.json"))
STOCK = {"SKU-100": {"name": "Router X2", "BLR-1": 40, "PNQ-1": 2, "DEL-1": 0},
         "SKU-200": {"name": "Fibre ONT", "BLR-1": 5, "PNQ-1": 120, "DEL-1": 18}}
mcp = FastMCP("inventory")

@mcp.tool()
def get_stock(sku: str) -> str:
    """Stock of a SKU per warehouse (BLR-1, PNQ-1, DEL-1)."""
    s = STOCK.get(sku.strip().upper())
    return json.dumps({"sku": sku.upper(), **s} if s else {"error": f"unknown sku {sku}"})

@mcp.tool()
def request_transfer(sku: str, from_wh: str, to_wh: str, qty: int) -> str:
    """Request a stock transfer between warehouses. Creates a PENDING request that a human must approve; nothing moves now."""
    s = STOCK.get(sku.strip().upper())
    if not s or from_wh not in s or to_wh not in s: return json.dumps({"error": "unknown sku or warehouse"})
    if not (0 < int(qty) <= s[from_wh]): return json.dumps({"error": f"qty must be 1..{s[from_wh]} (available at {from_wh})"})
    p = json.load(open(PENDING)) if os.path.exists(PENDING) else []
    p.append({"sku": sku.upper(), "from_wh": from_wh, "to_wh": to_wh, "qty": int(qty)}); json.dump(p, open(PENDING, "w"))
    return json.dumps({"status": "PENDING_HUMAN_APPROVAL", "request_no": len(p)})

if __name__ == "__main__":
    mcp.run()
