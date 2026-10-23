"""CLI: `agentest run --suite functional [--ids T1-001] [--agent golden|broken]`."""

from __future__ import annotations

import argparse
import json
import sys

from agentest.runner import SUITE_IDS, all_passed, run_ids
from agentest.types import Outcome


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agentest", description="Agentic AI checklist runner")
    sub = parser.add_subparsers(dest="cmd")
    run = sub.add_parser("run", help="Run checklist IDs")
    run.add_argument("--suite", default="functional", choices=sorted(SUITE_IDS))
    run.add_argument(
        "--ids",
        default=None,
        help="Comma-separated Hub IDs (default: all IDs in --suite)",
    )
    run.add_argument(
        "--agent",
        default="golden",
        choices=("golden", "broken"),
        help="Reference agent under test (default: golden)",
    )
    run.add_argument("--json", action="store_true", help="Emit machine-readable results")
    args = parser.parse_args(argv)

    if args.cmd != "run":
        parser.print_help()
        return 2

    ids: list[str] | None = None
    if args.ids is not None:
        ids = [part.strip() for part in args.ids.split(",") if part.strip()]
        if not ids:
            print("error: --ids must list at least one checklist ID", file=sys.stderr)
            return 2

    try:
        results = run_ids(ids, suite=args.suite, agent=args.agent)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        payload = [
            {
                "id": r.checklist_id,
                "outcome": r.outcome.value,
                "reason": r.reason,
                "details": r.details,
            }
            for r in results
        ]
        print(json.dumps(payload, indent=2))
    else:
        for r in results:
            mark = {
                Outcome.PASS: "PASS",
                Outcome.FAIL: "FAIL",
                Outcome.UNVERIFIED: "UNVERIFIED",
            }[r.outcome]
            print(f"{r.checklist_id}\t{mark}\tagent={args.agent}\t{r.reason}")

    return 0 if all_passed(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
