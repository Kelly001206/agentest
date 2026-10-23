"""Sample agents — green ladder all-pass; expected-fail band partial fails."""

from __future__ import annotations

import pytest

from agentest.cases.registry import CASE_REGISTRY
from agentest.cli import main as cli_main
from agentest.runner import matrix_ok, run_ids, run_matrix
from agentest.samples import (
    EXPECTED_FAIL_SCENARIOS,
    MATRIX_EXPECTED_FAIL,
    MATRIX_MUST_PASS,
    SAMPLE_AGENT_NAMES,
    get_sample,
    list_samples,
)
from agentest.types import Outcome

ALL_IDS = sorted(CASE_REGISTRY.keys())
# Unique CaseSpecs: 34 prior + 7 new orchestration = 41
EXPECTED_UNIQUE = 41
# Matrix sums suites; T3-006 counted in explainability + orchestration → 42
EXPECTED_MATRIX_TOTAL = 42

GREEN = [
    "scripted",
    "policy",
    "reflective",
    "supervisor",
    "handoff",
    "planner",
    "critic",
    "federation",
]


def test_list_samples_returns_fifteen():
    infos = list_samples()
    assert len(infos) == 15
    assert [i.name for i in infos] == list(SAMPLE_AGENT_NAMES)
    assert [i.complexity for i in infos] == list(range(1, 16))


def test_list_samples_failing_only():
    infos = list_samples(failing_only=True)
    assert [i.name for i in infos] == list(EXPECTED_FAIL_SCENARIOS)
    assert all(11 <= i.complexity <= 15 for i in infos)


def test_cli_samples_exit_0():
    assert cli_main(["samples"]) == 0
    assert cli_main(["samples", "--failing"]) == 0


def test_stub_fails_t1_001():
    results = run_ids(["T1-001"], suite="functional", agent="stub")
    assert results[0].outcome is Outcome.FAIL


def test_stub_fails_privacy_soft_delete():
    results = run_ids(["T1-016"], suite="privacy", agent="stub")
    assert results[0].outcome is Outcome.FAIL


@pytest.mark.parametrize("agent", GREEN)
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
    assert cli_main(["run", "--suite", "functional", "--ids", "T2-001", "--agent", "planner"]) == 0
    assert cli_main(["run", "--suite", "explainability", "--ids", "T1-018", "--agent", "critic"]) == 0
    assert cli_main(["run", "--suite", "orchestration", "--ids", "T3-007", "--agent", "federation"]) == 0
    assert cli_main(["run", "--suite", "privacy", "--ids", "T1-016", "--agent", "leaky"]) == 1
    assert cli_main(["run", "--suite", "explainability", "--ids", "T1-018", "--agent", "hallucinator"]) == 1
    assert cli_main(["run", "--suite", "bias_fairness", "--ids", "T7-007", "--agent", "biased"]) == 1
    assert cli_main(["run", "--suite", "orchestration", "--ids", "T3-001", "--agent", "overreach"]) == 1
    assert cli_main(["run", "--suite", "functional", "--ids", "T2-001", "--agent", "flaky_plan"]) == 1


@pytest.mark.parametrize("agent", EXPECTED_FAIL_SCENARIOS)
def test_expected_fail_partial_profile(agent: str):
    """Each cx 11–15 agent fails some IDs and still passes many (not a total wipeout)."""
    summary = run_matrix(agents=[agent], include_golden=False)
    row = summary[agent]
    assert row["total"] == EXPECTED_MATRIX_TOTAL
    assert row["fail"] >= 3, (agent, row)
    assert row["pass"] >= 5, (agent, row)
    assert row["pass"] + row["fail"] + row["unverified"] == row["total"]
    assert agent in MATRIX_EXPECTED_FAIL
    assert agent not in MATRIX_MUST_PASS


def test_matrix_must_pass_agents():
    summary = run_matrix(include_golden=True)
    assert summary["stub"]["pass"] < summary["stub"]["total"]
    assert summary["stub"]["fail"] > summary["stub"]["pass"]
    for agent in (*GREEN, "golden"):
        assert summary[agent]["pass"] == summary[agent]["total"] == EXPECTED_MATRIX_TOTAL, (
            agent,
            summary[agent],
        )
    for agent in EXPECTED_FAIL_SCENARIOS:
        assert summary[agent]["fail"] >= 3
        assert summary[agent]["pass"] >= 5
    assert matrix_ok(summary)


def test_cli_matrix_exit_0():
    assert cli_main(["matrix", "--no-golden"]) == 0


def test_get_sample_unknown():
    with pytest.raises(ValueError, match="unknown sample"):
        get_sample("nope")
