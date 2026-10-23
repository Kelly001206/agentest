"""Run checklist IDs against a chosen agent."""

from __future__ import annotations

from agentest.cases.registry import (
    ALL_AGENTS,
    BIAS_FAIRNESS_IDS,
    CASE_REGISTRY,
    EXPLAINABILITY_IDS,
    FUNCTIONAL_IDS,
    ORCHESTRATION_IDS,
    PRIVACY_IDS,
    get_case,
)
from agentest.types import Outcome, Result

# Primary suite name: bias_fairness; alias: bias
SUITE_IDS: dict[str, list[str]] = {
    "functional": list(FUNCTIONAL_IDS),
    "privacy": list(PRIVACY_IDS),
    "explainability": list(EXPLAINABILITY_IDS),
    "bias_fairness": list(BIAS_FAIRNESS_IDS),
    "bias": list(BIAS_FAIRNESS_IDS),  # alias
    "orchestration": list(ORCHESTRATION_IDS),
    "orch": list(ORCHESTRATION_IDS),  # alias
}

MATRIX_SUITES: tuple[str, ...] = ("functional", "privacy", "explainability", "bias_fairness", "orchestration")


def resolve_ids(suite: str, ids: list[str] | None) -> list[str]:
    if ids:
        return ids
    try:
        return list(SUITE_IDS[suite])
    except KeyError as exc:
        known = ", ".join(sorted(SUITE_IDS))
        raise ValueError(f"unknown suite {suite!r}; choose one of: {known}") from exc


def run_ids(
    ids: list[str] | None = None,
    *,
    suite: str = "functional",
    agent: str = "golden",
) -> list[Result]:
    if agent not in ALL_AGENTS:
        raise ValueError(f"unknown agent {agent!r}; choose one of: {', '.join(ALL_AGENTS)}")
    resolved = resolve_ids(suite, ids)
    results: list[Result] = []
    for checklist_id in resolved:
        if checklist_id not in CASE_REGISTRY:
            results.append(
                Result(
                    checklist_id=checklist_id,
                    outcome=Outcome.UNVERIFIED,
                    reason="ID not implemented in this runner yet",
                )
            )
            continue
        results.append(get_case(checklist_id).run(agent))
    return results


def all_passed(results: list[Result]) -> bool:
    return bool(results) and all(r.ok for r in results)


def run_matrix(
    *,
    agents: list[str] | None = None,
    include_golden: bool = True,
) -> dict[str, dict[str, int]]:
    """Run all suites × sample agents (and optionally golden).

    Returns ``{agent: {"pass": n, "fail": n, "unverified": n, "total": n}}``.
    Stub/eager are *expected* to fail many IDs — callers should not treat
    their failures as a process error.
    """
    from agentest.samples import SAMPLE_AGENT_NAMES

    if agents is None:
        names = list(SAMPLE_AGENT_NAMES)
        if include_golden:
            names = ["golden", *names]
    else:
        names = list(agents)

    summary: dict[str, dict[str, int]] = {}
    for agent in names:
        passed = failed = unverified = 0
        for suite in MATRIX_SUITES:
            for r in run_ids(None, suite=suite, agent=agent):
                if r.outcome is Outcome.PASS:
                    passed += 1
                elif r.outcome is Outcome.FAIL:
                    failed += 1
                else:
                    unverified += 1
        summary[agent] = {
            "pass": passed,
            "fail": failed,
            "unverified": unverified,
            "total": passed + failed + unverified,
        }
    return summary


def matrix_ok(summary: dict[str, dict[str, int]], *, must_pass: list[str] | None = None) -> bool:
    """True iff every agent in must_pass has pass == total (stub failures ignored)."""
    from agentest.samples import MATRIX_MUST_PASS

    required = must_pass if must_pass is not None else [a for a in MATRIX_MUST_PASS if a in summary]
    for agent in required:
        row = summary.get(agent)
        if row is None:
            return False
        if row["pass"] != row["total"]:
            return False
    return bool(required)
