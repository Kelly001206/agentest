"""CLI used to prove durability: `python step.py start <thread> <text>` then later, in a NEW process,
`python step.py resume <thread> '<json reply>'`."""
import sys, json, sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
import agent
cmd, thread = sys.argv[1], sys.argv[2]
with SqliteSaver.from_conn_string(agent.CKPT) as saver:
    g = agent.build(saver); cfg = {"configurable": {"thread_id": thread}}
    if cmd == "start":
        r = g.invoke({"invoice_text": sys.argv[3]}, cfg)
    else:
        r = g.invoke(Command(resume=json.loads(sys.argv[3])), cfg)
    st = g.get_state(cfg)
    print(json.dumps({"paused_at": list(st.next), "interrupt": [i.value for i in r.get("__interrupt__", [])], "result": r.get("result"),
                      "invoice": r.get("invoice"), "log": r.get("log")}, default=str))
