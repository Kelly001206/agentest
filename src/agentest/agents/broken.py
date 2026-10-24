"""Broken agent for T1-001 — claims success without correct ledger writes."""

from __future__ import annotations

from agentest.env import Env
from agentest.types import Trace


def run(env: Env) -> Trace:
    """False completion: claim success, leave all records PENDING."""
    # Seeded defect: perform NO ledger writes at all.
    _ = env  # intentionally unused — no writes
    # Claim success anyway -> T1-001 must report false completion (FAIL).
    return Trace(
        claims_success=True,
        message="Done — all requests processed",
        calls=[],
    )
