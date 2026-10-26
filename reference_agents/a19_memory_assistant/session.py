"""CLI: run ONE session in its own process.  python session.py <db> <user_id> '<message>'  -> prints one JSON line."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent import session
from common.runtime import Tracer
if __name__ == "__main__":
    tr = Tracer("A19", os.environ.get("A19_TRACE"))
    try: out = session(sys.argv[1], sys.argv[2], sys.argv[3], tracer=tr)
    except Exception as e: out = {"error": f"{type(e).__name__}: {e}"}
    print(json.dumps({**out, "spans": tr.compact(300)}, ensure_ascii=False))
