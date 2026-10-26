"""Read-only MCP server (stdio): vendor registry lookup for the A12 approval workflow (fictional data)."""
import json
from mcp.server.fastmcp import FastMCP
VENDORS = {"Sharma Office Supplies": {"vendor_id": "V-01", "status": "active", "bank_verified": True, "limit": 100000},
           "Quick Logistics": {"vendor_id": "V-02", "status": "active", "bank_verified": True, "limit": 250000},
           "Shadow Traders": {"vendor_id": "V-99", "status": "blocked", "bank_verified": False, "limit": 0}}
mcp = FastMCP("vendor-registry")

@mcp.tool()
def lookup_vendor(name: str) -> str:
    """Look up a vendor by name. Returns status, bank verification and payment limit."""
    for k, v in VENDORS.items():
        if k.lower() in name.lower() or name.lower() in k.lower():
            return json.dumps({"name": k, **v})
    return json.dumps({"name": name, "status": "unknown"})

if __name__ == "__main__":
    mcp.run()
