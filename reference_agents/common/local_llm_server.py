"""Tiny OpenAI-compatible /v1/chat/completions server backed by a small open model
running locally on CPU via Hugging Face transformers. Zero cost, no API keys.

Supports tool calling using Qwen2.5's native <tool_call>{...}</tool_call> format,
so LangGraph, CrewAI, AutoGen, the OpenAI Agents SDK, LlamaIndex and n8n can all
talk to it as if it were an OpenAI endpoint.

Run:  python common/local_llm_server.py          (port 8008)
Env:  REF_MODEL (default Qwen/Qwen2.5-1.5B-Instruct), REF_PORT, REF_MAX_NEW_TOKENS
"""
import json, os, re, time, uuid, threading
import torch
from fastapi import FastAPI, Request
from transformers import AutoModelForCausalLM, AutoTokenizer
import uvicorn

MODEL = os.environ.get("REF_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")
PORT = int(os.environ.get("REF_PORT", "8008"))
MAX_NEW = int(os.environ.get("REF_MAX_NEW_TOKENS", "384"))
torch.set_num_threads(max(1, os.cpu_count() or 1))
tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16)
model.eval()
lock = threading.Lock()
app = FastAPI()


def _norm_messages(msgs):
    out = []
    for m in msgs:
        role = m.get("role")
        c = m.get("content")
        if isinstance(c, list):
            c = "".join(p.get("text", "") for p in c if isinstance(p, dict))
        if role == "developer":
            role = "system"
        mm = {"role": role, "content": c or ""}
        if m.get("tool_calls"):
            mm["tool_calls"] = [
                {"type": "function", "function": {"name": tc["function"]["name"],
                 "arguments": json.loads(tc["function"]["arguments"] or "{}") if isinstance(tc["function"].get("arguments"), str) else tc["function"].get("arguments", {})}}
                for tc in m["tool_calls"]]
        out.append(mm)
    # Qwen template wants system first only
    sys = [m for m in out if m["role"] == "system"]
    rest = [m for m in out if m["role"] != "system"]
    if len(sys) > 1:
        sys = [{"role": "system", "content": "\n\n".join(s["content"] for s in sys)}]
    return sys + rest


def generate(messages, tools=None, temperature=0.0, max_tokens=None, prefix=""):
    prompt = tok.apply_chat_template(messages, tools=tools or None, add_generation_prompt=True, tokenize=False) + prefix
    ids = tok(prompt, return_tensors="pt")
    kw = dict(max_new_tokens=min(max_tokens or MAX_NEW, MAX_NEW), do_sample=False)
    with lock, torch.no_grad():
        out = model.generate(**ids, **kw)
    text = prefix + tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True)
    return text, ids["input_ids"].shape[1], out.shape[1] - ids["input_ids"].shape[1]


def pick_tool(messages, tools):
    """Constrained choice for tool_choice='required': score each allowed tool name by log-likelihood."""
    base = tok.apply_chat_template(messages, tools=tools, add_generation_prompt=True, tokenize=False) + '<tool_call>\n{"name": "'
    base_ids = tok(base, return_tensors="pt")["input_ids"]
    best, best_lp = None, -1e9
    for t in tools:
        name = t["function"]["name"]
        cand = tok(base + name + '"', return_tensors="pt")["input_ids"]
        with lock, torch.no_grad():
            logits = model(cand).logits[0]
        lp = torch.log_softmax(logits[:-1].float(), -1)
        tgt = cand[0, 1:]
        n = cand.shape[1] - base_ids.shape[1]
        score = lp[-n:].gather(1, tgt[-n:, None]).sum().item()
        if score > best_lp: best, best_lp = name, score
    return best


TC_RE = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.S)


def parse_tool_calls(text):
    calls = []
    for m in TC_RE.finditer(text):
        try:
            j = json.loads(m.group(1))
            calls.append({"id": "call_" + uuid.uuid4().hex[:12], "type": "function",
                          "function": {"name": j["name"], "arguments": json.dumps(j.get("arguments", {}))}})
        except Exception:
            pass
    return calls, TC_RE.sub("", text).strip()


@app.get("/v1/models")
def models():
    return {"object": "list", "data": [{"id": MODEL, "object": "model", "owned_by": "local"}]}


@app.post("/v1/chat/completions")
async def chat(req: Request):
    body = await req.json()
    tools = body.get("tools")
    if tools and body.get("tool_choice") == "none":
        tools = None
    msgs = _norm_messages(body["messages"])
    t0 = time.time()
    tc = body.get("tool_choice")
    # tool_choice="required" (or a named function) is honoured by pre-filling the start of a <tool_call> block
    prefix = ""
    if tools and tc == "required":
        prefix = '<tool_call>\n{"name": "' + pick_tool(msgs, tools) + '", "arguments": '
    elif tools and isinstance(tc, dict) and tc.get("function", {}).get("name"):
        prefix = '<tool_call>\n{"name": "' + tc["function"]["name"] + '", "arguments": '
    text, pt, ct = generate(msgs, tools=tools, max_tokens=body.get("max_tokens") or body.get("max_completion_tokens"), prefix=prefix)
    calls, content = parse_tool_calls(text) if tools else ([], text)
    msg = {"role": "assistant", "content": content if content else (None if calls else "")}
    if calls:
        msg["tool_calls"] = calls
    print(f"[llm] {time.time()-t0:.1f}s prompt={pt} completion={ct} tools={len(tools or [])} calls={[c['function']['name'] for c in calls]}", flush=True)
    return {"id": "chatcmpl-" + uuid.uuid4().hex, "object": "chat.completion", "created": int(time.time()),
            "model": MODEL, "choices": [{"index": 0, "message": msg, "finish_reason": "tool_calls" if calls else "stop"}],
            "usage": {"prompt_tokens": pt, "completion_tokens": ct, "total_tokens": pt + ct}}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
