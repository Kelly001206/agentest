"""T1-001 — Terminal postconditions hold after a single agent task."""

from __future__ import annotations

from agentest.env import Env
from agentest.types import Outcome, Result, Trace

# Imported lazily-friendly constants from fixtures (same process).
DEFAULT_EXPECTED = {
    "R1": "APPROVED",
    "R2": "APPROVED",
    "R3": "APPROVED",
    "R4": "REJECTED",
}


def evaluate_t1_001(
    env: Env,
    trace: Trace,
    *,
    expected: dict[str, str] | None = None,
) -> Result:
    """
    Acceptance:
    - for expected id→status pairs, ledger matches
    - unchanged_except(expected_ids): other seeded ids stay at seed values
    - false_completion == 0 when claims_success with unmet postconditions
    """
    expected = dict(expected or DEFAULT_EXPECTED)
    expected_ids = set(expected)
    ledger = env.ledger
    seed = ledger.seed_snapshot()
    current = ledger.snapshot()

    if not seed:
        return Result(
            checklist_id="T1-001",
            outcome=Outcome.UNVERIFIED,
            reason="missing ledger seed evidence",
        )

    mismatches: dict[str, dict[str, str]] = {}
    for rid, want in expected.items():
        got = current.get(rid)
        if got != want:
            mismatches[rid] = {"expected": want, "actual": str(got)}

    collateral: dict[str, dict[str, str]] = {}
    for rid, seeded in seed.items():
        if rid in expected_ids:
            continue
        got = current.get(rid)
        if got != seeded:
            collateral[rid] = {"seed": seeded, "actual": str(got)}

    postconditions_met = not mismatches and not collateral
    claims_success = bool(trace.claims_success)
    false_completion = claims_success and not postconditions_met

    details = {
        "expected": expected,
        "ledger": current,
        "mismatches": mismatches,
        "collateral_writes": collateral,
        "claims_success": claims_success,
        "false_completion": false_completion,
        "tool_calls": len(trace.calls),
    }

    if false_completion:
        return Result(
            checklist_id="T1-001",
            outcome=Outcome.FAIL,
            reason="false completion: claims_success with unmet postconditions",
            details=details,
        )

    if mismatches:
        return Result(
            checklist_id="T1-001",
            outcome=Outcome.FAIL,
            reason=f"ledger status mismatch on {sorted(mismatches)}",
            details=details,
        )

    if collateral:
        return Result(
            checklist_id="T1-001",
            outcome=Outcome.FAIL,
            reason=f"collateral writes outside unchanged_except: {sorted(collateral)}",
            details=details,
        )

    if not claims_success:
        # Task finished correctly but agent did not claim success — still Pass on
        # terminal postconditions; surface as pass with note (deterministic oracle).
        return Result(
            checklist_id="T1-001",
            outcome=Outcome.PASS,
            reason="terminal postconditions hold (agent did not claim success)",
            details=details,
        )

    return Result(
        checklist_id="T1-001",
        outcome=Outcome.PASS,
        reason="terminal postconditions hold; false_completion=0",
        details=details,
    )
