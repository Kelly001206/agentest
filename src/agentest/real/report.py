"""Build the 41 x 27 matrix (15 sample agents + 12 reference agents)."""

from __future__ import annotations

import json
from pathlib import Path

from agentest.real.checks import REF_AGENTS, R, evaluate, load_episodes
from agentest.real.ids import REAL_IDS, WHAT
from agentest.real.samples import all_samples

SYM = {"pass": "P", "fail": "F", "n/a": "-", "not-run": "?"}


def build(episodes_dir: Path, include_samples: bool = True, include_reference: bool = True) -> dict[str, dict[str, R]]:
    m: dict[str, dict[str, R]] = {}
    if include_samples:
        m.update(all_samples())
    if include_reference:
        eps = load_episodes(episodes_dir)
        for a in REF_AGENTS:
            m[a] = evaluate(a, eps.get(a))
    return m


def to_json(m: dict[str, dict[str, R]]) -> dict:
    return {a: {i: {"status": r.status, "detail": r.detail} for i, r in row.items()} for a, row in m.items()}


def to_markdown(m: dict[str, dict[str, R]]) -> str:
    agents = list(m)
    lines = ["| ID | " + " | ".join(agents) + " |", "|---|" + "---|" * len(agents)]
    for i in REAL_IDS:
        lines.append(f"| {i} | " + " | ".join(SYM[m[a][i].status] for a in agents) + " |")
    tot = {a: {s: sum(1 for r in m[a].values() if r.status == s) for s in SYM} for a in agents}
    lines.append("| **pass/fail/n-a** | " + " | ".join(f"{t['pass']}/{t['fail']}/{t['n/a']}" for t in tot.values()) + " |")
    fails = [f"- **{a} {i}**: {m[a][i].detail}" for a in agents for i in REAL_IDS if m[a][i].status == "fail"]
    legend = "P = pass, F = fail, - = n/a (agent has no surface for the ID), ? = not run"
    ids = "\n".join(f"- **{i}**: {WHAT[i]}" for i in REAL_IDS)
    return "\n".join(["# Real-test results matrix (41 IDs x agents)", "", legend, "", *lines, "", "## Failures", "", *fails, "", "## What each ID checks (reference agents)", "", ids, ""])


def main_report(episodes_dir: Path, md: Path | None, js: Path | None, samples: bool, reference: bool) -> dict:
    m = build(episodes_dir, samples, reference)
    if md:
        md.write_text(to_markdown(m))
    if js:
        js.write_text(json.dumps(to_json(m), indent=1))
    return m
