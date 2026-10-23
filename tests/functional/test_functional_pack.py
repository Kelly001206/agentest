"""Functional pack — Pass golden / Fail broken for all 18 Hub IDs."""

from __future__ import annotations

import pytest

from agentest.cases.registry import FUNCTIONAL_IDS
from agentest.cli import main as cli_main
from agentest.runner import run_ids
from agentest.types import Outcome

IMPLEMENTED = list(FUNCTIONAL_IDS)


@pytest.mark.parametrize("checklist_id", IMPLEMENTED)
def test_golden_passes(checklist_id: str):
    results = run_ids([checklist_id], suite="functional", agent="golden")
    assert len(results) == 1
    assert results[0].outcome is Outcome.PASS, results[0]


@pytest.mark.parametrize("checklist_id", IMPLEMENTED)
def test_broken_fails(checklist_id: str):
    results = run_ids([checklist_id], suite="functional", agent="broken")
    assert len(results) == 1
    assert results[0].outcome is Outcome.FAIL, results[0]


def test_suite_golden_all_pass():
    results = run_ids(None, suite="functional", agent="golden")
    assert len(results) == 18
    assert all(r.ok for r in results), [(r.checklist_id, r.outcome, r.reason) for r in results if not r.ok]


def test_cli_suite_golden_exit_0():
    assert cli_main(["run", "--suite", "functional", "--agent", "golden"]) == 0


def test_cli_suite_broken_exit_nonzero():
    assert cli_main(["run", "--suite", "functional", "--agent", "broken"]) != 0


def test_cli_single_broken_exit_nonzero():
    for checklist_id in IMPLEMENTED:
        code = cli_main(
            ["run", "--suite", "functional", "--ids", checklist_id, "--agent", "broken"]
        )
        assert code != 0, checklist_id
