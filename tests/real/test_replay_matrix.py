"""Replay the recorded reference-agent episodes offline and build the full matrix.

Agent failures are findings (reported in the matrix), not test failures. This test
asserts the replay is complete, deterministic and matches the committed results.
"""

from __future__ import annotations

import json
from pathlib import Path

from agentest.real.checks import REF_AGENTS
from agentest.real.ids import REAL_IDS
from agentest.real.report import build, to_json

ROOT = Path(__file__).resolve().parents[2]
EPS = ROOT / "fixtures" / "real" / "episodes"
EXPECTED = ROOT / "fixtures" / "real" / "results.json"


def test_all_reference_agents_recorded():
    for a in REF_AGENTS:
        assert (EPS / f"{a}.jsonl").exists(), a


def test_matrix_is_41_by_27_and_complete():
    m = build(EPS)
    assert len(m) == 27
    for row in m.values():
        assert list(row) == REAL_IDS
        assert all(r.status in {"pass", "fail", "n/a"} for r in row.values())


def test_replay_matches_committed_results():
    assert to_json(build(EPS)) == json.loads(EXPECTED.read_text())


def test_replay_is_offline_no_network_imports():
    import agentest.real.checks as c
    src = Path(c.__file__).read_text()
    for bad in ("requests", "urllib", "httpx", "socket", "openai"):
        assert f"import {bad}" not in src
