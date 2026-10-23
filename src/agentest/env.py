"""Environment: mock systems of record for functional + privacy packs."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


PENDING = "PENDING"
APPROVED = "APPROVED"
REJECTED = "REJECTED"
ACTIVE = "ACTIVE"


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

    def unchanged_except(self, expected_ids: set[str]) -> bool:
        seed = self._seed
        for rid, seeded in seed.items():
            if rid in expected_ids:
                continue
            if self.records.get(rid) != seeded:
                return False
        return True

    def clone(self) -> Ledger:
        other = Ledger()
        other.seed(deepcopy(self._seed))
        other.records = deepcopy(self.records)
        return other


@dataclass
class NotifyMock:
    call_count: int = 0

    def send(self, **_kwargs: Any) -> dict[str, Any]:
        self.call_count += 1
        return {"ok": True, "n": self.call_count}


@dataclass
class TenantStore:
    """Per-tenant durable store with write counter."""

    writes: int = 0
    contacts: dict[str, dict[str, Any]] = field(default_factory=dict)
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    bindings: dict[str, str] = field(default_factory=dict)
    binding_history: dict[str, list[str]] = field(default_factory=dict)
    completed: set[str] = field(default_factory=set)
    locale: str = "en"
    consent: dict[str, bool] = field(default_factory=dict)

    def bind(self, key: str, value: str) -> None:
        self.bindings[key] = value
        self.binding_history.setdefault(key, []).append(value)

    def complete(self, item: str) -> None:
        self.completed.add(item)

    def clone(self) -> AgentState:
        return AgentState(
            bindings=dict(self.bindings),
            binding_history={k: list(v) for k, v in self.binding_history.items()},
            completed=set(self.completed),
            locale=self.locale,
            consent=dict(self.consent),
        )


@dataclass
class Env:
    """Fresh mock environment for one agent run."""

    ledger: Ledger = field(default_factory=Ledger)
    contacts: dict[str, dict[str, Any]] = field(default_factory=dict)
    counters: dict[str, int] = field(default_factory=dict)
    users: dict[str, dict[str, Any]] = field(default_factory=dict)
    orders: dict[str, dict[str, Any]] = field(default_factory=dict)
    inventory: dict[str, int] = field(default_factory=dict)
    tickets: dict[str, dict[str, Any]] = field(default_factory=dict)
    notify: NotifyMock = field(default_factory=NotifyMock)
    state: AgentState = field(default_factory=AgentState)
    extras: dict[str, Any] = field(default_factory=dict)

    # Privacy pack
    profiles: dict[str, dict[str, Any]] = field(default_factory=dict)
    tenants: dict[str, TenantStore] = field(default_factory=dict)
    session_tenant_id: str = "A"
    files: list[dict[str, Any]] = field(default_factory=list)
    exports: list[dict[str, Any]] = field(default_factory=list)
    emails: list[dict[str, Any]] = field(default_factory=list)
    post_revoke_share_calls: int = 0
    denied: bool = False

    def snapshot(self) -> dict[str, Any]:
        """Business-store snapshot for diff / side-effect fence."""
        snap: dict[str, Any] = {}
        for rid, status in self.ledger.records.items():
            snap[f"ledger.{rid}"] = status
        for cid, data in self.contacts.items():
            snap[cid] = deepcopy(data)
        for name, val in self.counters.items():
            snap[f"counter.{name}"] = val
        for uid, data in self.users.items():
            snap[f"user.{uid}"] = deepcopy(data)
        for oid, data in self.orders.items():
            snap[f"order.{oid}"] = deepcopy(data)
        for sku, qty in self.inventory.items():
            snap[f"inventory.{sku}"] = qty
        for tid, data in self.tickets.items():
            snap[f"ticket.{tid}"] = deepcopy(data)
        for pid, data in self.profiles.items():
            snap[f"profile.{pid}"] = deepcopy(data)
        for k, v in self.extras.items():
            snap[k] = deepcopy(v)
        snap["state.locale"] = self.state.locale
        snap["state.bindings"] = dict(self.state.bindings)
        snap["state.completed"] = sorted(self.state.completed)
        snap["state.consent"] = dict(self.state.consent)
        return snap

    @staticmethod
    def diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
        keys = set(before) | set(after)
        changed: dict[str, Any] = {}
        for k in keys:
            if before.get(k) != after.get(k):
                changed[k] = {"before": before.get(k), "after": after.get(k)}
        return changed

    def clone(self) -> Env:
        return Env(
            ledger=self.ledger.clone(),
            contacts=deepcopy(self.contacts),
            counters=dict(self.counters),
            users=deepcopy(self.users),
            orders=deepcopy(self.orders),
            inventory=dict(self.inventory),
            tickets=deepcopy(self.tickets),
            notify=NotifyMock(call_count=self.notify.call_count),
            state=self.state.clone(),
            extras=deepcopy(self.extras),
            profiles=deepcopy(self.profiles),
            tenants={k: TenantStore(writes=v.writes, contacts=deepcopy(v.contacts), data=deepcopy(v.data)) for k, v in self.tenants.items()},
            session_tenant_id=self.session_tenant_id,
            files=deepcopy(self.files),
            exports=deepcopy(self.exports),
            emails=deepcopy(self.emails),
            post_revoke_share_calls=self.post_revoke_share_calls,
            denied=self.denied,
        )
