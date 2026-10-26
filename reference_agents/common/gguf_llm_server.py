"""OpenAI-compatible /v1/chat/completions server backed by a quantized GGUF model
(default: Qwen2.5-7B-Instruct Q4_K_M) running locally on CPU via llama.cpp (llama-cpp-python).
Zero cost, no API keys, no account. Same API as local_llm_server.py, which stays as the small
fallback (Qwen2.5-1.5B-Instruct via transformers).

Tool calling uses Qwen2.5's native <tool_call>{...}</tool_call> format (chat template from the
the model tokenizer). tool_choice="required" pre-fills only '<tool_call>' so the MODEL picks the
tool; a named tool_choice pre-fills that name (standard OpenAI semantics). The constrained
log-likelihood tool picker used for the 1.5B model is NOT used here.

Get the model:  download a Qwen2.5-7B-Instruct Q4_K_M GGUF file and set REF_GGUF
Run:            REF_GGUF=gguf/Qwen2.5-7B-Instruct-Q4_K_M.gguf python common/gguf_llm_server.py   (port 8008)
"""
import json, os, re, time, uuid, threading
from fastapi import FastAPI, Request
from transformers import AutoTokenizer
from llama_cpp import Llama
import uvicorn

GGUF = os.environ.get("REF_GGUF", "gguf/Qwen2.5-7B-Instruct-Q4_K_M.gguf")
MODEL = os.environ.get("REF_MODEL", "Qwen/Qwen2.5-7B-Instruct-GGUF:Q4_K_M")
PORT = int(os.environ.get("REF_PORT", "8008"))
MAX_NEW = int(os.environ.get("REF_MAX_NEW_TOKENS", "512"))
tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")
llm = Llama(model_path=GGUF, n_ctx=int(os.environ.get("REF_CTX", "8192")), n_threads=os.cpu_count(), verbose=False)
lock = threading.Lock()
app = FastAPI()

def _norm_messages(msgs):
    out = []
    for m in msgs:
        role = m.get("role"); c = m.get("content")
        if isinstance(c, list):
            c = "".join(p.get("text", "") for p in c if isinstance(p, dict))
        if role == "developer": role = "system"
        mm = {"role": role, "content": c or ""}
        if m.get("tool_calls"):
            mm["tool_calls"] = [{"type": "function", "function": {"name": tc["function"]["name"],
                "arguments": json.loads(tc["function"]["arguments"] or "{}") if isinstance(tc["function"].get("arguments"), str) else tc["function"].get("arguments", {})}}
                for tc in m["tool_calls"]]
        out.append(mm)
    sys = [m for m in out if m["role"] == "system"]; rest = [m for m in out if m["role"] != "system"]
    if len(sys) > 1: sys = [{"role": "system", "content": "\n\n".join(s["content"] for s in sys)}]
    return sys + rest

def generate(messages, tools=None, max_tokens=None, prefix=""):
    prompt = tok.apply_chat_template(messages, tools=tools or None, add_generation_prompt=True, tokenize=False) + prefix
    with lock:
        r = llm.create_completion(prompt, max_tokens=min(max_tokens or MAX_NEW, MAX_NEW), temperature=0.0, stop=["<|im_end|>", "<|endoftext|>"])
    return prefix + r["choices"][0]["text"], r["usage"]["prompt_tokens"], r["usage"]["completion_tokens"]

TC_RE = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.S)
def parse_tool_calls(text):
    calls = []
    if "<tool_call>" in text and "</tool_call>" not in text: text += "</tool_call>"
    for m in TC_RE.finditer(text):
        try:
            j = json.loads(m.group(1))
            calls.append({"id": "call_" + uuid.uuid4().hex[:12], "type": "function",
                          "function": {"name": j["name"], "arguments": json.dumps(j.get("arguments", {}))}})
        except Exception: pass
    return calls, TC_RE.sub("", text).strip()

@app.get("/v1/models")
def models():
    return {"object": "list", "data": [{"id": MODEL, "object": "model", "owned_by": "local"}]}

@app.post("/v1/chat/completions")
async def chat(req: Request):
    body = await req.json(); tools = body.get("tools"); tc = body.get("tool_choice")
    if tools and tc == "none": tools = None
    msgs = _norm_messages(body["messages"]); t0 = time.time(); prefix = ""
    if tools and tc == "required": prefix = "<tool_call>\n"
    elif tools and isinstance(tc, dict) and tc.get("function", {}).get("name"):
        prefix = '<tool_call>\n{"name": "' + tc["function"]["name"] + '", "arguments": '
    text, pt, ct = generate(msgs, tools=tools, max_tokens=body.get("max_tokens") or body.get("max_completion_tokens"), prefix=prefix)
    calls, content = parse_tool_calls(text) if tools else ([], text)
    msg = {"role": "assistant", "content": content if content else (None if calls else "")}
    if calls: msg["tool_calls"] = calls
    print(f"[llm] {time.time()-t0:.1f}s prompt={pt} completion={ct} tools={len(tools or [])} calls={[c['function']['name'] for c in calls]}", flush=True)
    return {"id": "chatcmpl-" + uuid.uuid4().hex, "object": "chat.completion", "created": int(time.time()), "model": MODEL,
            "choices": [{"index": 0, "message": msg, "finish_reason": "tool_calls" if calls else "stop"}],
            "usage": {"prompt_tokens": pt, "completion_tokens": ct, "total_tokens": pt + ct}}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
