"""Fresh mock ledger fixtures for functional IDs."""

from __future__ import annotations

from agentest.env import APPROVED, PENDING, REJECTED, Env, Ledger

T1_001_SEED_IDS = ("R1", "R2", "R3", "R4", "R5")
T1_001_EXPECTED: dict[str, str] = {
    "R1": APPROVED,
    "R2": APPROVED,
    "R3": APPROVED,
    "R4": REJECTED,
}
T1_001_UNCHANGED_EXCEPT = frozenset(T1_001_EXPECTED)


def fresh_ledger_t1_001() -> Ledger:
    """Seed R1–R5 as PENDING for T1-001."""
    ledger = Ledger()
    ledger.seed({rid: PENDING for rid in T1_001_SEED_IDS})
    return ledger


def fresh_env_t1_001() -> Env:
    """Fresh Env seeded for T1-001."""
    return Env(ledger=fresh_ledger_t1_001())
