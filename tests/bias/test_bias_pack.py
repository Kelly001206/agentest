"""Bias/fairness pack — Pass golden / Fail broken for all 3 Hub IDs."""

from __future__ import annotations

import pytest

from agentest.cases.registry import BIAS_FAIRNESS_IDS
from agentest.cli import main as cli_main
from agentest.runner import run_ids
from agentest.types import Outcome

IMPLEMENTED = list(BIAS_FAIRNESS_IDS)


@pytest.mark.parametrize("checklist_id", IMPLEMENTED)
def test_golden_passes(checklist_id: str):
    results = run_ids([checklist_id], suite="bias_fairness", agent="golden")
    assert len(results) == 1
    assert results[0].outcome is Outcome.PASS, results[0]


@pytest.mark.parametrize("checklist_id", IMPLEMENTED)
def test_broken_fails(checklist_id: str):
    results = run_ids([checklist_id], suite="bias_fairness", agent="broken")
    assert len(results) == 1
    assert results[0].outcome is Outcome.FAIL, results[0]


def test_suite_golden_all_pass():
    results = run_ids(None, suite="bias_fairness", agent="golden")
    assert len(results) == 3
    assert all(r.ok for r in results)


def test_bias_alias_matches_bias_fairness():
    a = run_ids(None, suite="bias", agent="golden")
    b = run_ids(None, suite="bias_fairness", agent="golden")
    assert [r.checklist_id for r in a] == [r.checklist_id for r in b]
    assert all(r.ok for r in a)


def test_cli_bias_fairness_golden_exit_0():
    assert cli_main(["run", "--suite", "bias_fairness", "--agent", "golden"]) == 0


def test_cli_bias_alias_golden_exit_0():
    assert cli_main(["run", "--suite", "bias", "--agent", "golden"]) == 0


def test_cli_bias_broken_exit_nonzero():
    assert cli_main(["run", "--suite", "bias", "--agent", "broken"]) != 0


def test_prior_suites_still_green():
    assert cli_main(["run", "--suite", "functional", "--agent", "golden"]) == 0
    assert cli_main(["run", "--suite", "privacy", "--agent", "golden"]) == 0
    assert cli_main(["run", "--suite", "explainability", "--agent", "golden"]) == 0
