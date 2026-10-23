"""Sample agents — stub fails; scripted/reflective/policy pass all 34 IDs."""

from __future__ import annotations

import pytest

from agentest.cases.registry import CASE_REGISTRY
from agentest.cli import main as cli_main
from agentest.runner import matrix_ok, run_ids, run_matrix
from agentest.samples import SAMPLE_AGENT_NAMES, get_sample, list_samples
from agentest.types import Outcome

ALL_IDS = sorted(CASE_REGISTRY.keys())


def test_list_samples_returns_five():
    infos = list_samples()
    assert len(infos) == 5
    assert [i.name for i in infos] == list(SAMPLE_AGENT_NAMES)
    assert [i.complexity for i in infos] == [1, 2, 3, 4, 5]


def test_cli_samples_exit_0():
    assert cli_main(["samples"]) == 0


def test_stub_fails_t1_001():
    results = run_ids(["T1-001"], suite="functional", agent="stub")
    assert results[0].outcome is Outcome.FAIL


def test_stub_fails_privacy_soft_delete():
    results = run_ids(["T1-016"], suite="privacy", agent="stub")
    assert results[0].outcome is Outcome.FAIL


@pytest.mark.parametrize("agent", ["scripted", "policy", "reflective"])
@pytest.mark.parametrize("checklist_id", ALL_IDS)
def test_passing_samples_pass_every_id(agent: str, checklist_id: str):
    # suite arg is ignored when ids are explicit; pick functional as placeholder
    results = run_ids([checklist_id], suite="functional", agent=agent)
    assert len(results) == 1
    assert results[0].outcome is Outcome.PASS, (agent, checklist_id, results[0])


def test_golden_still_passes_t1_001():
    results = run_ids(["T1-001"], suite="functional", agent="golden")
    assert results[0].outcome is Outcome.PASS


def test_broken_still_fails_t1_001():
    results = run_ids(["T1-001"], suite="functional", agent="broken")
    assert results[0].outcome is Outcome.FAIL


def test_run_agent_choices_include_samples():
    assert cli_main(["run", "--suite", "functional", "--ids", "T1-007", "--agent", "scripted"]) == 0


def test_matrix_must_pass_agents():
    summary = run_matrix(include_golden=True)
    assert summary["stub"]["pass"] < summary["stub"]["total"]
    assert summary["stub"]["fail"] > summary["stub"]["pass"]  # fails most
    assert summary["scripted"]["pass"] == summary["scripted"]["total"] == 34
    assert summary["policy"]["pass"] == 34
    assert summary["reflective"]["pass"] == 34
    assert summary["golden"]["pass"] == 34
    assert matrix_ok(summary)


def test_cli_matrix_exit_0():
    assert cli_main(["matrix", "--no-golden"]) == 0


def test_get_sample_unknown():
    with pytest.raises(ValueError, match="unknown sample"):
        get_sample("nope")
