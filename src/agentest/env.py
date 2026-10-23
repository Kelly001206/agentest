"""Environment: mock systems of record (ledger, …)."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field


# Allowed ledger statuses for T1-001 style tasks.
PENDING = "PENDING"
APPROVED = "APPROVED"
REJECTED = "REJECTED"


@dataclass
class Ledger:
    """In-memory mock ledger keyed by record id."""

    records: dict[str, str] = field(default_factory=dict)
    _seed: dict[str, str] = field(default_factory=dict, repr=False)

    def seed(self, statuses: dict[str, str]) -> None:
        self.records = dict(statuses)
        self._seed = dict(statuses)

    def get(self, record_id: str) -> str | None:
        return self.records.get(record_id)

    def set_status(self, record_id: str, status: str) -> None:
        if record_id not in self.records:
            raise KeyError(f"unknown ledger id: {record_id}")
        self.records[record_id] = status

    def snapshot(self) -> dict[str, str]:
        return dict(self.records)

    def seed_snapshot(self) -> dict[str, str]:
        return dict(self._seed)

    def clone(self) -> Ledger:
        other = Ledger()
        other.seed(deepcopy(self._seed))
        other.records = deepcopy(self.records)
        return other


@dataclass
class Env:
    """Fresh mock environment for one agent run."""

    ledger: Ledger = field(default_factory=Ledger)

    def clone(self) -> Env:
        return Env(ledger=self.ledger.clone())
