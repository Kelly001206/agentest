"""Check YOUR agent: run the trace-level checks over episodes you recorded.

Episode format (one JSON object per line)::

    {"probe": "case0", "input": "...", "output": {...},
     "trace": [{"seq": 0, "mono": 0.0, "kind": "tool", "name": "get_invoice",
                "data": {"args": {...}, "result": "...", "reason": "why"}},
               {"kind": "llm" | "message" | "plan" | "write" | ..., ...}],
     "extra": {"check_passed": true, "note": "your own scenario oracle"}}

``kind`` values used by the checks: ``tool`` (a tool call; put args and a
reason in ``data``), ``write`` (an executed side effect), ``llm`` /
``message`` / ``subagent`` / ``step`` (agent steps). ``mono`` is seconds since
the case started. ``extra.check_passed`` is your own pass/fail oracle for the
case; omit it and T1-001/T1-003/T1-018 report ``n/a``.

Same checks as reference agents A13-A25 (:mod:`agentest.real.checks3`).
"""

from __future__ import annotations

import html
import json
from pathlib import Path

from agentest.real.checks import Eps, R
from agentest.real.checks3 import RULES
from agentest.real.ids import what

ORACLE_IDS = {"T1-001", "T1-003", "T1-018"}


def load(path: Path) -> list[dict]:
    """Read a JSONL episodes file; fills ``probe`` (case<N>) when absent."""
    eps = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        try:
            e = json.loads(line)
        except ValueError as exc:
            raise ValueError(f"{path}:{n + 1}: not valid JSON ({exc})") from exc
        if not isinstance(e, dict):
            raise ValueError(f"{path}:{n + 1}: each line must be a JSON object")
        e.setdefault("probe", f"case{len(eps)}")
        e.setdefault("extra", {})
        e.setdefault("trace", [])
        eps.append(e)
    if not eps:
        raise ValueError(f"{path}: no episodes")
    return eps


def run(eps: list[dict]) -> dict[str, R]:
    """Apply every trace rule; IDs without a recorded surface are ``n/a``."""
    has_oracle = any("check_passed" in (e.get("extra") or {}) for e in eps)
    out: dict[str, R] = {}
    E = Eps(eps)
    for id_, fn, applies in RULES:
        if id_ in ORACLE_IDS and not has_oracle:
            out[id_] = R("n/a", "no extra.check_passed oracle recorded")
        elif not applies(eps):
            out[id_] = R("n/a", "no surface for this ID in the recorded trace")
        else:
            try:
                out[id_] = fn(E)
            except Exception as exc:  # noqa: BLE001 - a malformed episode is a finding, not a crash
                out[id_] = R("error", f"{type(exc).__name__}: {exc}"[:200])
    return out


def to_md(name: str, res: dict[str, R]) -> str:
    """Markdown report."""
    c = {s: sum(r.status == s for r in res.values()) for s in ("pass", "fail", "n/a", "error")}
    lines = [f"# agentest report: {name}", "",
             f"**{c['pass']} pass, {c['fail']} fail, {c['n/a']} n/a, {c['error']} error** over {len(res)} trace-level checks.", "",
             "Checks are deterministic Python over your recorded episodes (no model judge). n/a = your trace does not record that surface.", "",
             "| ID | Status | Detail | What it checks |", "|---|---|---|---|"]
    for i, r in res.items():
        lines.append(f"| {i} | {r.status.upper()} | {r.detail.replace('|', '/')} | {what(i).replace('|', '/')[:160]} |")
    return "\n".join(lines) + "\n"


def to_html(name: str, res: dict[str, R]) -> str:
    """Self-contained HTML report (no external assets)."""
    col = {"pass": "#1a7f37", "fail": "#cf222e", "n/a": "#6e7781", "error": "#9a6700"}
    rows = "".join(
        f"<tr><td>{html.escape(i)}</td><td style='color:{col.get(r.status, '#000')};font-weight:600'>{r.status.upper()}</td>"
        f"<td>{html.escape(r.detail)}</td><td>{html.escape(what(i)[:200])}</td></tr>" for i, r in res.items())
    c = {s: sum(r.status == s for r in res.values()) for s in col}
    return (f"<!doctype html><meta charset='utf-8'><title>agentest report: {html.escape(name)}</title>"
            "<style>body{font:14px system-ui,sans-serif;margin:2em;max-width:1100px}table{border-collapse:collapse;width:100%}"
            "td,th{border:1px solid #d0d7de;padding:6px;vertical-align:top;text-align:left}th{background:#f6f8fa}</style>"
            f"<h1>agentest report: {html.escape(name)}</h1><p><b>{c['pass']} pass, {c['fail']} fail, {c['n/a']} n/a, {c['error']} error</b> "
            f"over {len(res)} trace-level checks. Deterministic Python over recorded episodes; no model judge.</p>"
            f"<table><tr><th>ID</th><th>Status</th><th>Detail</th><th>What it checks</th></tr>{rows}</table>")


class Recorder:
    """Tiny helper to record episodes in the format above from your own agent code.

    >>> rec = Recorder()
    >>> rec.start("case0", "refund ORD-1")
    >>> rec.tool("lookup_order", {"order_id": "ORD-1"}, "found", reason="verify the order before refunding")
    >>> rec.finish({"status": "pending_approval"}, check_passed=True)
    >>> rec.save("episodes.jsonl")  # doctest: +SKIP
    """

    def __init__(self) -> None:
        import time

        self._time = time.monotonic
        self.episodes: list[dict] = []
        self._cur: dict | None = None
        self._t0 = 0.0

    def start(self, probe: str, input_: object) -> None:
        """Begin a new case."""
        self._t0 = self._time()
        self._cur = {"probe": probe, "input": input_, "output": None, "trace": [], "extra": {}, "error": None}

    def event(self, kind: str, name: str, **data: object) -> None:
        """Record any trace event (``llm``, ``message``, ``plan``, ``write`` ...)."""
        assert self._cur is not None, "call start() first"
        tr = self._cur["trace"]
        tr.append({"seq": len(tr), "mono": round(self._time() - self._t0, 3), "kind": kind, "name": name, "data": data})

    def tool(self, name: str, args: dict, result: object, reason: str = "") -> None:
        """Record a tool call with its arguments, result and reason."""
        self.event("tool", name, args=args, result=result, reason=reason)

    def write(self, name: str, **data: object) -> None:
        """Record an executed side effect (payment, email, DB write ...)."""
        self.event("write", name, **data)

    def finish(self, output: dict, check_passed: bool | None = None, note: str = "") -> None:
        """End the case with its output and (optionally) your own oracle verdict."""
        assert self._cur is not None, "call start() first"
        self._cur["output"] = output
        if check_passed is not None:
            self._cur["extra"] = {"check_passed": check_passed, "note": note}
        self.episodes.append(self._cur)
        self._cur = None

    def save(self, path: str | Path) -> Path:
        """Write all finished cases as JSONL."""
        p = Path(path)
        p.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in self.episodes), encoding="utf-8")
        return p
