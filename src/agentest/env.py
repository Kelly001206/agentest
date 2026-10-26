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
        """Seed rows into the store."""
        self.records = dict(statuses)
        self._seed = dict(statuses)

    def get(self, record_id: str) -> str | None:
        """Return the stored value for a key (None if absent)."""
        return self.records.get(record_id)

    def set_status(self, record_id: str, status: str) -> None:
        """Set the status of one row."""
        if record_id not in self.records:
            raise KeyError(f"unknown ledger id: {record_id}")
        self.records[record_id] = status

    def snapshot(self) -> dict[str, str]:
        """Return a copy of the current rows."""
        return dict(self.records)

    def seed_snapshot(self) -> dict[str, str]:
        """Return the rows as they were seeded."""
        return dict(self._seed)

    def unchanged_except(self, expected_ids: set[str]) -> bool:
        """True when no row outside ``ids`` differs from the seed."""
        seed = self._seed
        for rid, seeded in seed.items():
            if rid in expected_ids:
                continue
            if self.records.get(rid) != seeded:
                return False
        return True

    def clone(self) -> Ledger:
        """Return an independent deep copy."""
        other = Ledger()
        other.seed(deepcopy(self._seed))
        other.records = deepcopy(self.records)
        return other


@dataclass
class NotifyMock:
    """In-memory notification sink recording every message sent."""
    call_count: int = 0

    def send(self, **_kwargs: Any) -> dict[str, Any]:
        """Record one outbound message."""
        self.call_count += 1
        return {"ok": True, "n": self.call_count}


@dataclass
class AuthzEntry:
    """Independent authz decision recorded by a receiving agent (T3-006)."""

    actor: str
    decision: str  # allow | deny
    policy_version: str
    task: str = ""
    resource: str = ""


@dataclass
class AuthzLog:
    """Append-only authorisation decision log (allow/deny + policy version)."""
    entries: list[AuthzEntry] = field(default_factory=list)

    def record(
        self,
        *,
        actor: str,
        decision: str,
        policy_version: str,
        task: str = "",
        resource: str = "",
    ) -> AuthzEntry:
        """Append one entry."""
        entry = AuthzEntry(
            actor=actor,
            decision=decision,
            policy_version=policy_version,
            task=task,
            resource=resource,
        )
        self.entries.append(entry)
        return entry

    def last(self, actor: str | None = None) -> AuthzEntry | None:
        """Return the most recent entry (None if empty)."""
        for entry in reversed(self.entries):
            if actor is None or entry.actor == actor:
                return entry
        return None




@dataclass
class ApprovalToken:
    """Single-use (or multi) approval record in the durable approvals store."""

    ref: str
    tool: str
    target: str = ""
    single_use: bool = True
    consumed: bool = False
    granted_by: str = ""


_REFUND_ALIASES = frozenset({"refund.issue", "issue_refund", "refund"})


@dataclass
class ApprovalsStore:
    """Durable approval tokens — handover prose is NOT a substitute."""

    tokens: dict[str, ApprovalToken] = field(default_factory=dict)
    _seq: int = 0

    def clear(self) -> None:
        """Remove all entries."""
        self.tokens.clear()

    def grant(
        self,
        *,
        tool: str,
        target: str = "",
        single_use: bool = True,
        granted_by: str = "",
        ref: str | None = None,
    ) -> ApprovalToken:
        """Grant an approval token."""
        self._seq += 1
        token_ref = ref or f"apr-{self._seq}"
        tok = ApprovalToken(
            ref=token_ref,
            tool=tool,
            target=target,
            single_use=single_use,
            consumed=False,
            granted_by=granted_by,
        )
        self.tokens[token_ref] = tok
        return tok

    def get(self, ref: str) -> ApprovalToken | None:
        """Return the stored value for a key (None if absent)."""
        return self.tokens.get(ref)

    @staticmethod
    def _tool_match(token_tool: str, tool: str) -> bool:
        if token_tool == tool:
            return True
        return token_tool in _REFUND_ALIASES and tool in _REFUND_ALIASES

    def has_valid(self, *, tool: str, target: str = "") -> bool:
        """True when a non-expired, unconsumed approval exists."""
        for tok in self.tokens.values():
            if tok.consumed:
                continue
            if not self._tool_match(tok.tool, tool):
                continue
            if target and tok.target and tok.target != target:
                continue
            return True
        return False

    def consume(self, ref: str) -> ApprovalToken:
        """Consume an approval; return True on success."""
        tok = self.tokens.get(ref)
        if tok is None:
            raise KeyError(f"unknown approval ref: {ref}")
        if tok.consumed:
            raise PermissionError(f"approval token already consumed: {ref}")
        if tok.single_use:
            tok.consumed = True
        return tok

    def clone(self) -> ApprovalsStore:
        """Return an independent deep copy."""
        other = ApprovalsStore(_seq=self._seq)
        for ref, tok in self.tokens.items():
            other.tokens[ref] = ApprovalToken(
                ref=tok.ref,
                tool=tok.tool,
                target=tok.target,
                single_use=tok.single_use,
                consumed=tok.consumed,
                granted_by=tok.granted_by,
            )
        return other

@dataclass
class TenantStore:
    """Per-tenant durable store with write counter."""

    writes: int = 0
    contacts: dict[str, dict[str, Any]] = field(default_factory=dict)
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    """Multi-turn agent state: bound slots, completion flag, constraints."""
    bindings: dict[str, str] = field(default_factory=dict)
    binding_history: dict[str, list[str]] = field(default_factory=dict)
    completed: set[str] = field(default_factory=set)
    locale: str = "en"
    consent: dict[str, bool] = field(default_factory=dict)

    def bind(self, key: str, value: str) -> None:
        """Bind a slot value."""
        self.bindings[key] = value
        self.binding_history.setdefault(key, []).append(value)

    def complete(self, item: str) -> None:
        """Mark the task complete."""
        self.completed.add(item)

    def clone(self) -> AgentState:
        """Return an independent deep copy."""
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

    # Explainability pack
    authz_log: AuthzLog = field(default_factory=AuthzLog)
    memory: list[str] = field(default_factory=list)
    memory_reads: list[str] = field(default_factory=list)
    db_ok: bool = False  # terminal world-state for T1-018

    # Orchestration pack (multi-agent handoff / HITL)
    approvals: ApprovalsStore = field(default_factory=ApprovalsStore)
    actor: str = "agent"
    role: str = "worker"  # supervisor | worker | intern | triage
    clock: int = 0  # minutes (logical clock)
    session_expires_at: int | None = None  # exclusive expiry in clock units
    handover_notes: str = ""
    refunds: list[dict[str, Any]] = field(default_factory=list)
    require_approval_for_disburse: bool = True
    enforce_authz: bool = False  # when True, gateway blocks unpermitted HIGH_PRIV
    inbox: list[dict[str, Any]] = field(default_factory=list)  # agent-to-agent messages


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
        """Return the keys whose values differ from ``other``."""
        keys = set(before) | set(after)
        changed: dict[str, Any] = {}
        for k in keys:
            if before.get(k) != after.get(k):
                changed[k] = {"before": before.get(k), "after": after.get(k)}
        return changed

    def clone(self) -> Env:
        """Return an independent deep copy."""
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
            authz_log=AuthzLog(
                entries=[
                    AuthzEntry(
                        actor=e.actor,
                        decision=e.decision,
                        policy_version=e.policy_version,
                        task=e.task,
                        resource=e.resource,
                    )
                    for e in self.authz_log.entries
                ]
            ),
            memory=list(self.memory),
            memory_reads=list(self.memory_reads),
            db_ok=self.db_ok,
            approvals=self.approvals.clone(),
            actor=self.actor,
            role=self.role,
            clock=self.clock,
            session_expires_at=self.session_expires_at,
            handover_notes=self.handover_notes,
            refunds=deepcopy(self.refunds),
            require_approval_for_disburse=self.require_approval_for_disburse,
            enforce_authz=self.enforce_authz,
            inbox=deepcopy(self.inbox),
        )
