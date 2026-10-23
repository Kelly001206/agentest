"""Explainability pack — Pass golden / Fail broken for all 5 Hub IDs."""

from __future__ import annotations

import pytest

from agentest.cases.registry import EXPLAINABILITY_IDS
from agentest.cli import main as cli_main
from agentest.runner import run_ids
from agentest.types import Outcome

IMPLEMENTED = list(EXPLAINABILITY_IDS)


@pytest.mark.parametrize("checklist_id", IMPLEMENTED)
def test_golden_passes(checklist_id: str):
    results = run_ids([checklist_id], suite="explainability", agent="golden")
    assert len(results) == 1
    assert results[0].outcome is Outcome.PASS, results[0]


@pytest.mark.parametrize("checklist_id", IMPLEMENTED)
def test_broken_fails(checklist_id: str):
    results = run_ids([checklist_id], suite="explainability", agent="broken")
    assert len(results) == 1
    assert results[0].outcome is Outcome.FAIL, results[0]


def test_suite_golden_all_pass():
    results = run_ids(None, suite="explainability", agent="golden")
    assert len(results) == 5
    assert all(r.ok for r in results), [(r.checklist_id, r.reason) for r in results if not r.ok]


def test_cli_explainability_golden_exit_0():
    assert cli_main(["run", "--suite", "explainability", "--agent", "golden"]) == 0


def test_cli_explainability_broken_exit_nonzero():
    assert cli_main(["run", "--suite", "explainability", "--agent", "broken"]) != 0


def test_prior_suites_still_green():
    assert cli_main(["run", "--suite", "functional", "--agent", "golden"]) == 0
    assert cli_main(["run", "--suite", "privacy", "--agent", "golden"]) == 0
