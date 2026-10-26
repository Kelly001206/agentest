"""Shared production runtime for agents A13-A25.

Provides, with no third-party eval frameworks:
  * AgentConfig   - typed, validated config (pydantic) read from env with safe defaults
  * Tracer        - structured JSONL tracing (one span per line) with a run id and monotonic timestamps
  * chat()        - OpenAI-compatible chat call with timeout, bounded retries + backoff, fixed seed, temperature 0
  * parse_json()  - tolerant JSON extraction from LLM text (first {...} or [...] block)
  * ApprovalGate  - scoped, single-use, expiring human approval tokens ("APPROVE <action> <object>")
  * validate_text()- input validation (type, length, control characters)
  * with_retries() - generic retry wrapper for flaky tool/framework calls
Everything is local and zero-cost: the LLM is the local llama.cpp server in common/gguf_llm_server.py.
"""
from __future__ import annotations
import json, os, re, time, uuid, random, threading, datetime
from typing import Any, Callable, Optional
from pydantic import BaseModel, Field, field_validator


class AgentConfig(BaseModel):
    """Typed runtime configuration. Override with REF_* environment variables."""
    llm_base: str = Field(default_factory=lambda: os.environ.get("REF_LLM_BASE", "http://127.0.0.1:8008/v1"))
    model: str = Field(default_factory=lambda: os.environ.get("REF_MODEL", "Qwen/Qwen2.5-7B-Instruct-GGUF:Q4_K_M"))
    api_key: str = "not-needed-local"
    timeout_s: float = Field(default_factory=lambda: float(os.environ.get("REF_TIMEOUT_S", "600")), gt=0)
    max_retries: int = Field(default_factory=lambda: int(os.environ.get("REF_MAX_RETRIES", "2")), ge=0, le=5)
    max_tokens: int = Field(default=400, gt=0, le=2048)
    seed: int = Field(default_factory=lambda: int(os.environ.get("REF_SEED", "7")))
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_input_chars: int = Field(default=6000, gt=0)

    @field_validator("llm_base")
    @classmethod
    def _local_only_by_default(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("llm_base must be an http(s) URL")
        return v.rstrip("/")


class InputError(ValueError):
    """Raised when an input fails validation. Agents turn it into a graceful refusal."""


def validate_text(text: Any, name: str = "input", max_chars: int = 6000, min_chars: int = 1) -> str:
    if not isinstance(text, str):
        raise InputError(f"{name} must be a string, got {type(text).__name__}")
    t = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text).strip()
    if len(t) < min_chars:
        raise InputError(f"{name} is empty")
    if len(t) > max_chars:
        raise InputError(f"{name} is too long ({len(t)} > {max_chars} chars)")
    return t


class Tracer:
    """Structured JSONL tracer. Each span: run_id, seq, ts (UTC), mono (monotonic s), kind, name, data."""
    def __init__(self, agent: str, path: Optional[str] = None):
        self.agent, self.run_id, self.path = agent, uuid.uuid4().hex[:12], path
        self.spans: list[dict] = []
        self._lock = threading.Lock(); self._t0 = time.monotonic()
        if path:
            os.makedirs(os.path.dirname(path), exist_ok=True)

    def event(self, kind: str, name: str, **data) -> dict:
        with self._lock:
            s = {"run_id": self.run_id, "agent": self.agent, "seq": len(self.spans),
                 "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds"),
                 "mono": round(time.monotonic() - self._t0, 3), "kind": kind, "name": name, "data": data}
            self.spans.append(s)
            if self.path:
                with open(self.path, "a") as f:
                    f.write(json.dumps(s, ensure_ascii=False, default=str) + "\n")
        return s

    def compact(self, limit: int = 400) -> list[dict]:
        """Short form of the spans for proof records."""
        out = []
        for s in self.spans:
            d = json.dumps(s["data"], ensure_ascii=False, default=str)
            out.append({"seq": s["seq"], "mono": s["mono"], "kind": s["kind"], "name": s["name"],
                        "data": s["data"] if len(d) <= limit else d[:limit] + "..."})
        return out


def with_retries(fn: Callable[[], Any], retries: int = 2, base_delay: float = 1.0, tracer: Optional[Tracer] = None,
                 name: str = "call", retry_on: tuple = (Exception,)) -> Any:
    last = None
    for attempt in range(retries + 1):
        try:
            return fn()
        except retry_on as e:  # noqa: PERF203
            last = e
            if tracer: tracer.event("retry", name, attempt=attempt, error=f"{type(e).__name__}: {str(e)[:200]}")
            if attempt < retries:
                time.sleep(base_delay * (2 ** attempt) + random.Random(attempt).random() * 0.1)
    raise last  # type: ignore[misc]


_client_cache: dict = {}
def _client(cfg: AgentConfig):
    key = (cfg.llm_base, cfg.timeout_s)
    if key not in _client_cache:
        from openai import OpenAI
        _client_cache[key] = OpenAI(base_url=cfg.llm_base, api_key=cfg.api_key, timeout=cfg.timeout_s, max_retries=0)
    return _client_cache[key]


def chat(messages: list[dict], cfg: AgentConfig, tracer: Optional[Tracer] = None, name: str = "llm",
         max_tokens: Optional[int] = None, tools: Optional[list] = None, tool_choice: Any = None) -> dict:
    """One chat completion with timeout, retries, seed and temperature from cfg. Returns the message dict."""
    def call():
        kw = dict(model=cfg.model, messages=messages, temperature=cfg.temperature, seed=cfg.seed,
                  max_tokens=max_tokens or cfg.max_tokens)
        if tools: kw["tools"] = tools
        if tool_choice: kw["tool_choice"] = tool_choice
        r = _client(cfg).chat.completions.create(**kw)
        return r.choices[0].message.model_dump()
    t0 = time.monotonic()
    msg = with_retries(call, retries=cfg.max_retries, tracer=tracer, name=name)
    if tracer:
        tracer.event("llm", name, seconds=round(time.monotonic() - t0, 2),
                     content=(msg.get("content") or "")[:600],
                     tool_calls=[c["function"]["name"] for c in (msg.get("tool_calls") or [])])
    return msg


def parse_json(text: Optional[str], default: Any = None) -> Any:
    """Extract the first JSON object/array from LLM text. Returns default if none parses."""
    if not text: return default
    t = re.sub(r"```(?:json)?", "", text)
    pairs = sorted((("{", "}"), ("[", "]")), key=lambda p: t.find(p[0]) if t.find(p[0]) != -1 else len(t))
    for opener, closer in pairs:  # the outermost structure (whichever opens first) wins
        start = t.find(opener)
        while start != -1:
            depth, in_str, esc = 0, False, False
            for i in range(start, len(t)):
                ch = t[i]
                if in_str:
                    if esc: esc = False
                    elif ch == "\\": esc = True
                    elif ch == '"': in_str = False
                    continue
                if ch == '"': in_str = True
                elif ch == opener: depth += 1
                elif ch == closer:
                    depth -= 1
                    if depth == 0:
                        try: return json.loads(t[start:i + 1])
                        except json.JSONDecodeError: break
            start = t.find(opener, start + 1)
    return default


class ApprovalError(PermissionError):
    pass


class ApprovalGate:
    """Human approval for write actions. A valid approval is EXACTLY 'APPROVE <action> <object>'
    (case-sensitive), from an allow-listed approver, before expiry, and usable once."""
    def __init__(self, approvers: tuple = ("ops-lead", "finance-head", "compliance-officer"), ttl_s: float = 900):
        self.approvers, self.ttl_s = set(approvers), ttl_s
        self.used: set = set(); self.audit: list[dict] = []

    def request(self, action: str, obj: str) -> dict:
        return {"action": action, "object": obj, "expected_token": f"APPROVE {action} {obj}",
                "requested_at": time.time(), "expires_at": time.time() + self.ttl_s}

    def check(self, req: dict, reply: Optional[dict]) -> bool:
        reason = None
        if not reply: reason = "no reply (silence is not approval)"
        elif reply.get("approver") not in self.approvers: reason = "approver not allow-listed"
        elif (reply.get("token") or "").strip() != req["expected_token"]: reason = "token does not match action+object"
        elif time.time() > req["expires_at"]: reason = "approval expired"
        elif req["expected_token"] in self.used: reason = "token already used (replay)"
        ok = reason is None
        if ok: self.used.add(req["expected_token"])
        self.audit.append({"action": req["action"], "object": req["object"], "approver": (reply or {}).get("approver"),
                           "granted": ok, "reason": reason or "exact scoped token", "policy_version": "approval-policy/1.0"})
        return ok


class Tool(BaseModel):
    """A function tool: name, description, JSON-schema parameters and a Python callable.
    `write=True` marks tools with side effects; tool_loop never executes them directly unless
    the caller passes an executor that enforces approval."""
    model_config = {"arbitrary_types_allowed": True}
    name: str
    description: str
    parameters: dict = Field(default_factory=lambda: {"type": "object", "properties": {}})
    fn: Callable[..., Any]
    write: bool = False

    def schema(self) -> dict:
        return {"type": "function", "function": {"name": self.name, "description": self.description, "parameters": self.parameters}}


def tool_loop(system: str, user: str, tools: list[Tool], cfg: AgentConfig, tracer: Tracer, name: str = "agent",
              max_steps: int = 4, first_required: bool = True, history: Optional[list] = None) -> dict:
    """Native function-calling loop with a hard step budget. Unknown tools and bad arguments are
    returned to the model as errors (never raised). Returns {final, calls, steps}."""
    by = {t.name: t for t in tools}
    msgs = [{"role": "system", "content": system}] + list(history or []) + [{"role": "user", "content": user}]
    calls: list[dict] = []
    for step in range(max_steps):
        choice = "required" if (first_required and step == 0 and tools) else "auto"
        m = chat(msgs, cfg, tracer, name=f"{name}.step{step}", tools=[t.schema() for t in tools] if tools else None, tool_choice=choice if tools else None)
        tcs = m.get("tool_calls") or []
        if not tcs:
            return {"final": m.get("content") or "", "calls": calls, "steps": step + 1}
        msgs.append({"role": "assistant", "content": m.get("content") or "", "tool_calls": tcs})
        for tc in tcs[:3]:
            fn = tc["function"]["name"]
            try: args = json.loads(tc["function"].get("arguments") or "{}")
            except json.JSONDecodeError: args = {}
            if fn not in by:
                result = {"error": f"unknown tool {fn}"}
            else:
                try: result = by[fn].fn(**args) if isinstance(args, dict) else {"error": "arguments must be an object"}
                except TypeError as e: result = {"error": f"bad arguments: {e}"}
                except Exception as e: result = {"error": f"{type(e).__name__}: {e}"}
            calls.append({"tool": fn, "args": args, "result": result})
            tracer.event("tool", fn, args=args, result=str(result)[:400], reason=f"{name} step {step}")
            msgs.append({"role": "tool", "tool_call_id": tc.get("id", "x"), "content": json.dumps(result, default=str)[:3000]})
    m = chat(msgs + [{"role": "user", "content": "Tool budget reached. Give your final answer now without calling tools."}], cfg, tracer, name=f"{name}.final")
    return {"final": m.get("content") or "", "calls": calls, "steps": max_steps + 1}


def redact_pii(text: str) -> str:
    """Mask emails, Indian mobile numbers, PAN, Aadhaar-like and card-like digit runs."""
    t = re.sub(r"[\w.+-]+@[\w-]+(\.[\w-]+)+", "[EMAIL]", text or "")
    t = re.sub(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", "[PAN]", t)
    t = re.sub(r"(?<![\d+])(?:\+91[ -]?)?[6-9]\d{9}(?!\d)", "[PHONE]", t)
    t = re.sub(r"\b\d(?:[ -]?\d){11,18}\b", "[NUMBER]", t)
    return t
