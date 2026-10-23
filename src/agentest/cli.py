"""CLI: agentest run | samples | matrix."""

from __future__ import annotations

import argparse
import json
import sys

from agentest.cases.registry import ALL_AGENTS
from agentest.runner import SUITE_IDS, all_passed, matrix_ok, run_ids, run_matrix
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
        choices=list(ALL_AGENTS),
        help="Agent under test: golden|broken|stub|eager|scripted|policy|reflective",
    )
    run.add_argument("--json", action="store_true", help="Emit machine-readable results")

    samples = sub.add_parser("samples", help="List teaching sample agents (complexity 1–5)")
    samples.add_argument("--json", action="store_true", help="Emit JSON")

    matrix = sub.add_parser(
        "matrix",
        help=(
            "Run all suites × sample agents (and golden). "
            "Exit 0 if scripted/policy/reflective/(golden) all-pass; "
            "stub/eager failures are expected and do not fail the process."
        ),
    )
    matrix.add_argument(
        "--no-golden",
        action="store_true",
        help="Omit the golden oracle agent from the matrix",
    )
    matrix.add_argument("--json", action="store_true", help="Emit JSON summary")

    args = parser.parse_args(argv)

    if args.cmd == "samples":
        return _cmd_samples(args)
    if args.cmd == "matrix":
        return _cmd_matrix(args)
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


def _cmd_samples(args: argparse.Namespace) -> int:
    from agentest.samples import list_samples

    infos = list_samples()
    if args.json:
        print(
            json.dumps(
                [
                    {
                        "name": i.name,
                        "title": i.title,
                        "complexity": i.complexity,
                        "description": i.description,
                    }
                    for i in infos
                ],
                indent=2,
            )
        )
    else:
        print(f"{'name':<12} {'cx':>2}  title")
        print("-" * 60)
        for i in infos:
            print(f"{i.name:<12} {i.complexity:>2}  {i.title}")
            print(f"{'':12}     {i.description}")
            print()
    return 0


def _cmd_matrix(args: argparse.Namespace) -> int:
    summary = run_matrix(include_golden=not args.no_golden)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"{'agent':<12} {'pass':>5} {'fail':>5} {'unv':>5} {'total':>5}")
        print("-" * 40)
        for agent, row in summary.items():
            print(
                f"{agent:<12} {row['pass']:>5} {row['fail']:>5} "
                f"{row['unverified']:>5} {row['total']:>5}"
            )
        print()
        print(
            "Note: stub/eager are meant to fail many IDs. "
            "Exit status reflects scripted/policy/reflective/(golden) all-pass only."
        )
    return 0 if matrix_ok(summary) else 1


if __name__ == "__main__":
    raise SystemExit(main())
