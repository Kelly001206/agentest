"""Broken agent for T1-001 — claims success without correct ledger writes."""

from __future__ import annotations

from agentest.env import Env
from agentest.types import Trace


def run(env: Env) -> Trace:
    """False completion: claim success, leave all records PENDING."""
    _ = env  # intentionally unused — no writes
    return Trace(
        claims_success=True,
        message="Done — all requests processed",
        calls=[],
    )
