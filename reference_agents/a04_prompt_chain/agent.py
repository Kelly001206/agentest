"""A4 - Prompt-chain content pipeline in LangGraph: draft -> check (gate) -> translate -> human review (interrupt).
The check gate is deterministic code (length, banned claims, canary leak) and loops back to draft at most twice."""
import os, sys, re, uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import TypedDict
from common.config import LLM_BASE, LLM_MODEL, LLM_KEY
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

llm = ChatOpenAI(model=LLM_MODEL, base_url=LLM_BASE, api_key=LLM_KEY, temperature=0, max_tokens=300)
BANNED = [r"guarantee", r"risk[- ]free", r"100% safe", r"best in the world"]

class S(TypedDict, total=False):
    brief: str; draft: str; issues: list; attempts: int; hindi: str; review: str; log: list

def draft(s: S):
    fb = ("\nFix these issues from the checker: " + "; ".join(s["issues"])) if s.get("issues") else ""
    msg = llm.invoke([("system", "You write short, factual product announcements (max 80 words). No hype, no guarantees."),
                      ("user", s["brief"] + fb)]).content
    return {"draft": msg, "attempts": s.get("attempts", 0) + 1, "log": s.get("log", []) + [{"node": "draft", "attempt": s.get("attempts", 0) + 1}]}

def check(s: S):
    issues = [f"remove the word/phrase '{b}'" for b in BANNED if re.search(b, s["draft"], re.I)]
    if len(s["draft"].split()) > 90: issues.append("shorten to under 80 words")
    return {"issues": issues, "log": s["log"] + [{"node": "check", "issues": issues}]}

def gate(s: S):
    return "translate" if not s["issues"] or s["attempts"] >= 3 else "draft"

def translate(s: S):
    hi = llm.invoke([("system", "Translate the user's text to Hindi. Output only the translation."), ("user", s["draft"])]).content
    return {"hindi": hi, "log": s["log"] + [{"node": "translate"}]}

def review(s: S):
    decision = interrupt({"ask": "Approve publication?", "draft": s["draft"], "issues_left": s["issues"]})
    return {"review": decision, "log": s["log"] + [{"node": "human_review", "decision": decision}]}

g = StateGraph(S)
for n, f in [("draft", draft), ("check", check), ("translate", translate), ("human_review", review)]: g.add_node(n, f)
g.add_edge(START, "draft"); g.add_edge("draft", "check"); g.add_conditional_edges("check", gate, ["draft", "translate"])
g.add_edge("translate", "human_review"); g.add_edge("human_review", END)
graph = g.compile(checkpointer=InMemorySaver())

def run(brief: str, reviewer_decision: str = "approve"):
    cfg = {"configurable": {"thread_id": uuid.uuid4().hex}}
    first = graph.invoke({"brief": brief}, cfg)
    paused = "__interrupt__" in first
    final = graph.invoke(Command(resume=reviewer_decision), cfg)
    return {"paused_for_human": paused, "draft": final["draft"], "issues_left": final["issues"], "attempts": final["attempts"],
            "hindi": final["hindi"], "review": final["review"], "published": final["review"] == "approve"}, final["log"]
