"""Shared proof harness for A13-A25: runs each demo case with a wall-clock budget, records
output + JSONL trace, applies the plain-Python sanity check, and never lets one failing case
stop the others. Writes proof/run.jsonl, proof/run.md (via ProofLog) and proof/trace.jsonl."""
from __future__ import annotations
import os, time, traceback
from typing import Callable
from .proof import ProofLog
from .runtime import Tracer


def run_cases(agent_dir: str, agent_id: str, framework: str, cases: list, runner: Callable, uses_llm: bool = True):
    """cases: list of (name, input, check(output)->bool, note). runner(input, tracer) -> output dict."""
    log = ProofLog(agent_dir, agent_id, framework, uses_llm=uses_llm)
    trace_path = os.path.join(log.dir, "trace.jsonl")
    if os.path.exists(trace_path): os.remove(trace_path)
    for name, inp, check, note in cases:
        tr = Tracer(agent_id, trace_path); tr.event("case", "start", case=name)
        t0 = time.monotonic()
        try:
            out = runner(inp, tr)
            try: ok = bool(check(out))
            except Exception as e: ok = False; out = {**out, "check_error": f"{type(e).__name__}: {e}"}
        except Exception as e:
            out, ok = {"error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()[-1500:]}, False
        tr.event("case", "end", case=name, passed=ok, seconds=round(time.monotonic() - t0, 1))
        log.add(name, inp, out, tr.compact(), passed=ok, note=note)
    log.save()
    return log
