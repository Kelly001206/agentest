"""Run checklist IDs against a chosen agent."""

from __future__ import annotations

from agentest.cases.registry import CASE_REGISTRY, FUNCTIONAL_IDS, PRIVACY_IDS, get_case
from agentest.types import Outcome, Result

SUITE_IDS: dict[str, list[str]] = {
    "functional": list(FUNCTIONAL_IDS),
    "privacy": list(PRIVACY_IDS),
}


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
