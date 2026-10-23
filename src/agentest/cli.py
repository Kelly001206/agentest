"""CLI placeholder — M0 implements `agentest run --ids T1-001`."""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agentest", description="Agentic AI checklist runner")
    sub = parser.add_subparsers(dest="cmd")
    run = sub.add_parser("run", help="Run checklist IDs")
    run.add_argument("--suite", default="functional")
    run.add_argument("--ids", default="T1-001", help="Comma-separated Hub IDs")
    args = parser.parse_args(argv)

    if args.cmd != "run":
        parser.print_help()
        return 2

    print(
        f"agentest {args.suite}: ids={args.ids} — M0 harness not implemented yet "
        "(scaffold only). See docs/M0-BACKLOG.md"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
