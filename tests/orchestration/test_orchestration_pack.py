"""Orchestration pack — Pass golden / Fail broken for Hub theme IDs."""

from __future__ import annotations

import pytest

from agentest.cases.registry import ORCHESTRATION_IDS
from agentest.cli import main as cli_main
from agentest.runner import run_ids
from agentest.types import Outcome

# New CaseSpecs (T3-006 is reused from explainability — still in suite list)
NEW_ORCH_IDS = [i for i in ORCHESTRATION_IDS if i != "T3-006"]


@pytest.mark.parametrize("checklist_id", ORCHESTRATION_IDS)
def test_golden_passes(checklist_id: str):
    results = run_ids([checklist_id], suite="orchestration", agent="golden")
    assert len(results) == 1
    assert results[0].outcome is Outcome.PASS, results[0]


@pytest.mark.parametrize("checklist_id", ORCHESTRATION_IDS)
def test_broken_fails(checklist_id: str):
    results = run_ids([checklist_id], suite="orchestration", agent="broken")
    assert len(results) == 1
    assert results[0].outcome is Outcome.FAIL, results[0]


def test_suite_golden_all_pass():
    results = run_ids(None, suite="orchestration", agent="golden")
    assert len(results) == 8
    assert all(r.ok for r in results), [(r.checklist_id, r.reason) for r in results if not r.ok]


def test_suite_alias_orch():
    results = run_ids(None, suite="orch", agent="golden")
    assert len(results) == 8
    assert all(r.ok for r in results)


def test_cli_orchestration_golden_exit_0():
    assert cli_main(["run", "--suite", "orchestration", "--agent", "golden"]) == 0


def test_cli_orchestration_broken_exit_nonzero():
    assert cli_main(["run", "--suite", "orchestration", "--agent", "broken"]) != 0


@pytest.mark.parametrize("agent", ["scripted", "policy", "reflective", "supervisor", "handoff"])
def test_passing_samples_pass_orchestration_suite(agent: str):
    results = run_ids(None, suite="orchestration", agent=agent)
    assert len(results) == 8
    assert all(r.ok for r in results), [(r.checklist_id, r.reason) for r in results if not r.ok]


def test_stub_fails_handover_prose():
    results = run_ids(["T3-001"], suite="orchestration", agent="stub")
    assert results[0].outcome is Outcome.FAIL


def test_eager_fails_hitl():
    results = run_ids(["T2-004"], suite="orchestration", agent="eager")
    assert results[0].outcome is Outcome.FAIL


def test_prior_suites_still_green():
    assert cli_main(["run", "--suite", "functional", "--agent", "golden"]) == 0
    assert cli_main(["run", "--suite", "privacy", "--agent", "golden"]) == 0
    assert cli_main(["run", "--suite", "explainability", "--agent", "golden"]) == 0
    assert cli_main(["run", "--suite", "bias_fairness", "--agent", "golden"]) == 0


def test_new_ids_implemented():
    assert set(NEW_ORCH_IDS) == {
        "T3-001",
        "T3-002",
        "T3-007",
        "T3-010",
        "T3-011",
        "T3-014",
        "T2-004",
    }
