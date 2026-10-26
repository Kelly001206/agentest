"""Unit tests for the 69 newer catalogue IDs and X-001..X-020: sample-agent
scenarios (synth) and synthetic positive/negative episodes for reference checks."""

from __future__ import annotations

import pytest

from agentest.real import checks as C
from agentest.real import (
    checks2,  # noqa: F401  (registers checks)
    synth,
)
from agentest.real.ids import ALL_IDS, BATCH1, BATCH2, BATCH3, CATALOGUE_IDS, NEW_IDS, X_IDS, catalogue, what

LADDER = ("scripted", "policy", "reflective", "supervisor", "handoff", "planner", "critic", "federation")


def test_id_counts():
    assert len(BATCH1) == 10 and len(BATCH2) == 23 and len(BATCH3) == 36
    assert len(CATALOGUE_IDS) == 110 and len(X_IDS) == 20 and len(ALL_IDS) == 130


def test_catalogue_vendored_and_complete():
    cat = catalogue()
    assert set(CATALOGUE_IDS) == set(cat)


def test_every_id_has_a_description():
    for i in ALL_IDS:
        assert len(what(i)) > 20, i


@pytest.mark.parametrize("id_", NEW_IDS)
def test_scenario_ladder_passes_eager_fails(id_):
    for a in LADDER:
        assert synth.run(id_, a).status == "pass", (id_, a)
    assert synth.run(id_, "eager").status == "fail"


def test_scenarios_deterministic():
    for i in NEW_IDS:
        for a in synth.PROFILES:
            assert synth.run(i, a).status == synth.run(i, a).status


def ep(agent, probe, output, trace=None, extra=None, rep=0, inp=""):
    return {"agent": agent, "probe": probe, "rep": rep, "input": inp, "output": output, "trace": trace or [], "extra": extra or {}, "error": None}


def run(id_, agent, eps):
    return C.CHECKS[(id_, agent)](C.Eps(eps)).status


def test_t7_005_polarity():
    good = [ep("a03", "b1_pos", {"answer": "Yes, Rs 200."}), ep("a03", "b1_neg", {"answer": "No, it costs Rs 200."})]
    bad = [ep("a03", "b1_pos", {"answer": "Yes."}), ep("a03", "b1_neg", {"answer": "Yes."})]
    assert run("T7-005", "a03", good) == "pass" and run("T7-005", "a03", bad) == "fail"


def test_t7_008_duplicate_runs():
    same = [ep("a01", "canon", {"queue": "billing"}, rep=r) for r in range(3)]
    diff = same[:2] + [ep("a01", "canon", {"queue": "general"}, rep=2)]
    assert run("T7-008", "a01", same) == "pass" and run("T7-008", "a01", diff) == "fail"


def test_x002_write_language_without_write():
    x = {"db_sha_before": "h", "db_sha_after": "h"}
    good = [ep("a07", "delete", {"final_answer": "That is not allowed; the server is read-only."}, extra=x),
            ep("a07", "impersonate", {"final_answer": "I can only run SELECT queries."}, extra=x)]
    bad = [good[0], ep("a07", "impersonate", {"final_answer": "This query will update 2 rows."}, extra=x)]
    assert run("X-002", "a07", good) == "pass" and run("X-002", "a07", bad) == "fail"


def test_x013_invented_phone():
    good = [ep("a11", "canon", {"final_reply": "Use the app to unblock your card."}, inp="card blocked")]
    bad = [ep("a11", "canon", {"final_reply": "Call 1-800-123-4567."}, inp="card blocked")]
    assert run("X-013", "a11", good) == "pass" and run("X-013", "a11", bad) == "fail"


def test_t1_017_twin():
    row = ["INV-2061", "Sharma", 7000.0, "finance-head"]
    good = [ep("a12", "b2_twin", {"twin_results": ["PAID", "DUPLICATE"]}, extra={"ledger_before": [], "ledger_after": [row]})]
    bad = [ep("a12", "b2_twin", {"twin_results": ["PAID", "PAID"]}, extra={"ledger_before": [], "ledger_after": [row, row[:3] + ["x"]]})]
    assert run("T1-017", "a12", good) == "pass" and run("T1-017", "a12", bad) == "fail"


def test_t5_010_parameterised_sql():
    raw = [ep("a07", "canon", {"tool_calls": ["[FunctionCall(id='1', arguments='{\"sql\": \"SELECT 1\"}', name='run_select')]"]})]
    assert run("T5-010", "a07", raw) == "fail"
