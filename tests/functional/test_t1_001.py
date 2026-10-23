"""T1-001 — Pass golden / Fail broken_agent."""

from __future__ import annotations

from agentest.agents import broken as broken_agent
from agentest.agents import golden as golden_agent
from agentest.cli import main as cli_main
from agentest.env import APPROVED, PENDING, REJECTED
from agentest.fixtures.ledger import T1_001_EXPECTED, fresh_env_t1_001
from agentest.oracles.t1_001 import evaluate_t1_001
from agentest.runner import run_ids
from agentest.types import Outcome


def test_fresh_ledger_is_pending():
    env = fresh_env_t1_001()
    assert env.ledger.snapshot() == {
        "R1": PENDING,
        "R2": PENDING,
        "R3": PENDING,
        "R4": PENDING,
        "R5": PENDING,
    }


def test_t1_001_pass_golden():
    env = fresh_env_t1_001()
    trace = golden_agent.run(env)
    result = evaluate_t1_001(env, trace, expected=T1_001_EXPECTED)
    assert result.outcome is Outcome.PASS
    assert result.details["false_completion"] is False
    assert env.ledger.get("R1") == APPROVED
    assert env.ledger.get("R2") == APPROVED
    assert env.ledger.get("R3") == APPROVED
    assert env.ledger.get("R4") == REJECTED
    assert env.ledger.get("R5") == PENDING  # unchanged_except


def test_t1_001_fail_broken_false_completion():
    env = fresh_env_t1_001()
    trace = broken_agent.run(env)
    result = evaluate_t1_001(env, trace, expected=T1_001_EXPECTED)
    assert result.outcome is Outcome.FAIL
    assert result.details["false_completion"] is True
    assert trace.claims_success is True
    # No correct writes
    assert env.ledger.get("R1") == PENDING
    assert env.ledger.get("R4") == PENDING


def test_runner_golden_passes():
    results = run_ids(["T1-001"], agent="golden")
    assert len(results) == 1
    assert results[0].ok


def test_runner_broken_fails():
    results = run_ids(["T1-001"], agent="broken")
    assert len(results) == 1
    assert not results[0].ok
    assert results[0].outcome is Outcome.FAIL


def test_cli_golden_exit_0():
    assert cli_main(["run", "--suite", "functional", "--ids", "T1-001", "--agent", "golden"]) == 0


def test_cli_broken_exit_nonzero():
    code = cli_main(["run", "--suite", "functional", "--ids", "T1-001", "--agent", "broken"])
    assert code != 0
