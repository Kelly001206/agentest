"""Sample agents — stub fails; scripted…handoff pass all registered IDs."""

from __future__ import annotations

import pytest

from agentest.cases.registry import CASE_REGISTRY
from agentest.cli import main as cli_main
from agentest.runner import matrix_ok, run_ids, run_matrix
from agentest.samples import SAMPLE_AGENT_NAMES, get_sample, list_samples
from agentest.types import Outcome

ALL_IDS = sorted(CASE_REGISTRY.keys())
# Unique CaseSpecs: 34 prior + 7 new orchestration = 41
EXPECTED_UNIQUE = 41
# Matrix sums suites; T3-006 counted in explainability + orchestration → 42
EXPECTED_MATRIX_TOTAL = 42


def test_list_samples_returns_seven():
    infos = list_samples()
    assert len(infos) == 7
    assert [i.name for i in infos] == list(SAMPLE_AGENT_NAMES)
    assert [i.complexity for i in infos] == [1, 2, 3, 4, 5, 6, 7]


def test_cli_samples_exit_0():
    assert cli_main(["samples"]) == 0


def test_stub_fails_t1_001():
    results = run_ids(["T1-001"], suite="functional", agent="stub")
    assert results[0].outcome is Outcome.FAIL


def test_stub_fails_privacy_soft_delete():
    results = run_ids(["T1-016"], suite="privacy", agent="stub")
    assert results[0].outcome is Outcome.FAIL


@pytest.mark.parametrize("agent", ["scripted", "policy", "reflective", "supervisor", "handoff"])
@pytest.mark.parametrize("checklist_id", ALL_IDS)
def test_passing_samples_pass_every_id(agent: str, checklist_id: str):
    results = run_ids([checklist_id], suite="functional", agent=agent)
    assert len(results) == 1
    assert results[0].outcome is Outcome.PASS, (agent, checklist_id, results[0])


def test_registry_unique_count():
    assert len(CASE_REGISTRY) == EXPECTED_UNIQUE


def test_golden_still_passes_t1_001():
    results = run_ids(["T1-001"], suite="functional", agent="golden")
    assert results[0].outcome is Outcome.PASS


def test_broken_still_fails_t1_001():
    results = run_ids(["T1-001"], suite="functional", agent="broken")
    assert results[0].outcome is Outcome.FAIL


def test_run_agent_choices_include_samples():
    assert cli_main(["run", "--suite", "functional", "--ids", "T1-007", "--agent", "scripted"]) == 0
    assert cli_main(["run", "--suite", "orchestration", "--ids", "T3-001", "--agent", "supervisor"]) == 0
    assert cli_main(["run", "--suite", "orchestration", "--ids", "T3-001", "--agent", "handoff"]) == 0


def test_matrix_must_pass_agents():
    summary = run_matrix(include_golden=True)
    assert summary["stub"]["pass"] < summary["stub"]["total"]
    assert summary["stub"]["fail"] > summary["stub"]["pass"]
    for agent in ("scripted", "policy", "reflective", "supervisor", "handoff", "golden"):
        assert summary[agent]["pass"] == summary[agent]["total"] == EXPECTED_MATRIX_TOTAL, (
            agent,
            summary[agent],
        )
    assert matrix_ok(summary)


def test_cli_matrix_exit_0():
    assert cli_main(["matrix", "--no-golden"]) == 0


def test_get_sample_unknown():
    with pytest.raises(ValueError, match="unknown sample"):
        get_sample("nope")
