"""The 41 IDs against the 15 teaching sample agents (scenario oracles in ``agentest.cases``)."""

from __future__ import annotations

from agentest.cases.registry import get_case
from agentest.real.checks import R
from agentest.real.ids import REAL_IDS
from agentest.samples import SAMPLE_AGENT_NAMES
from agentest.types import Outcome


def evaluate_sample(agent: str) -> dict[str, R]:
    out: dict[str, R] = {}
    for i in REAL_IDS:
        r = get_case(i).run(agent)
        st = {Outcome.PASS: "pass", Outcome.FAIL: "fail"}.get(r.outcome, "n/a")
        out[i] = R(st, (getattr(r, "reason", "") or "")[:200])
    return out


def all_samples() -> dict[str, dict[str, R]]:
    return {a: evaluate_sample(a) for a in SAMPLE_AGENT_NAMES}
