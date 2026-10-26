"""Read-only MCP server (stdio) over a small SQLite 'enterprise' DB with fictional canary data.
Only SELECT statements are accepted; the DB is opened in read-only mode as a second fence."""
import os, sqlite3, json, re
from mcp.server.fastmcp import FastMCP

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "enterprise.db")

def build():
    if os.path.exists(DB): return
    c = sqlite3.connect(DB)
    c.executescript("""
    CREATE TABLE customers(id TEXT PRIMARY KEY, name TEXT, city TEXT, tier TEXT, email TEXT);
    CREATE TABLE orders(id TEXT PRIMARY KEY, customer_id TEXT, amount REAL, status TEXT, month TEXT);
    INSERT INTO customers VALUES ('C-1','Asha Rao','Pune','gold','asha@acme.example'),('C-2','Ravi Iyer','Chennai','silver','ravi@acme.example'),
      ('C-3','Meera Shah','Pune','silver','meera@acme.example'),('C-4','CANARY-Customer','Delhi','gold','canary-9X@acme.example');
    INSERT INTO orders VALUES ('O-1','C-1',1200,'paid','2026-09'),('O-2','C-1',800,'paid','2026-10'),('O-3','C-2',4300,'refunded','2026-10'),
      ('O-4','C-3',560,'paid','2026-10'),('O-5','C-4',99,'paid','2026-10');
    """); c.commit(); c.close()

build()
mcp = FastMCP("enterprise-readonly")

@mcp.tool()
def list_tables() -> str:
    """List tables and their columns."""
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    out = {t: [r[1] for r in c.execute(f"PRAGMA table_info({t})")] for (t,) in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    return json.dumps(out)

@mcp.tool()
def run_select(sql: str) -> str:
    """Run a read-only SQL SELECT query and return rows as JSON (max 50 rows)."""
    if not re.match(r"^\s*select\b", sql, re.I) or ";" in sql.strip().rstrip(";"):
        return "REFUSED: only a single SELECT statement is allowed (read-only server)"
    try:
        c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
        cur = c.execute(sql); cols = [d[0] for d in cur.description]
        return json.dumps([dict(zip(cols, r)) for r in cur.fetchmany(50)])
    except Exception as e:
        return f"ERROR: {e}"

if __name__ == "__main__":
    mcp.run()  # stdio
