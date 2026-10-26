"""All 130 IDs against the 15 teaching sample agents.

The first 41 use the scenario oracles in ``agentest.cases``; the rest use the
mini-world scenarios in :mod:`agentest.real.synth`.
"""

from __future__ import annotations

from agentest.cases.registry import get_case
from agentest.real import synth
from agentest.real.checks import R
from agentest.real.ids import ALL_IDS, REAL_IDS
from agentest.samples import SAMPLE_AGENT_NAMES
from agentest.types import Outcome


def evaluate_sample(agent: str) -> dict[str, R]:
    """Evaluate every ID for one sample agent and return ``{id: R}``."""
    out: dict[str, R] = {}
    for i in ALL_IDS:
        if i not in REAL_IDS:
            out[i] = synth.run(i, agent)
            continue
        r = get_case(i).run(agent)
        st = {Outcome.PASS: "pass", Outcome.FAIL: "fail"}.get(r.outcome, "n/a")
        out[i] = R(st, (getattr(r, "reason", "") or "")[:200])
    return out


def all_samples() -> dict[str, dict[str, R]]:
    """Evaluate all sample agents."""
    return {a: evaluate_sample(a) for a in SAMPLE_AGENT_NAMES}
