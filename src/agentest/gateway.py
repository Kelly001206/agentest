"""Mock tool gateway — routes allowlisted tools into Env and records Trace."""

from __future__ import annotations

from typing import Any

from agentest.env import ACTIVE, Env
from agentest.types import ToolCall, Trace

# Tools classified as durable writes for T1-013 / T5-012 style oracles.
WRITE_TOOLS = frozenset(
    {
        "ledger.set_status",
        "contact.update",
        "order.create",
        "inventory.set",
        "users.create",
        "users.set_status",
        "notify.send",
        "counters.increment",
        "update_ticket",
        "delete_ticket",
        "open_account",
        "disburse",
        "charge_card",
        "send_wire",
        "write_summary",
        "charge",
        "authorize",
        "ticket.open",
        "ticket.comment",
        "ticket.close",
        "todo.plan",
        "todo.complete",
        "todo.drop",
        "locale.set",
        "extras.set",
        # privacy
        "profiles.soft_delete",
        "profiles.hard_delete",
        "disclose_last4",
        "disclose_ssn",
        "disclose_email",
        "tenant.update_contact",
        "send_email",
        "export_customers",
        "export_all",
        "consent.grant",
        "consent.revoke",
        "share_partner",
        "db.write",
        "refund",
        "memory.read",
        # orchestration
        "handover.write",
        "approval.grant",
        "approval.consume",
        "session.set_role",
        "session.set_ttl",
        "session.advance_clock",
        "refund.issue",
        "issue_refund",
        "user.delete",
        "admin_delete",
        "grant_role",
        "authz.decide",
    }
)

READ_TOOLS = frozenset(
    {
        "get_ticket",
        "search",
        "get_user",
        "fetch_profile",
        "fetch_prefs",
        "ledger.get",
        "sanctions_screen",
        "verify_identity",
        "log_debug",
    }
)


class ToolGateway:
    """Broad mock tool surface for the functional pack."""

    def __init__(self, env: Env, trace: Trace | None = None) -> None:
        self.env = env
        self.trace = trace if trace is not None else Trace()

    def call(
        self,
        name: str,
        *,
        reason: str | None = None,
        meta: dict[str, Any] | None = None,
        **args: Any,
    ) -> Any:
        call_meta: dict[str, Any] = dict(meta or {})
        if reason is not None:
            call_meta["reason"] = reason
        # Optional authz gate (orchestration pack teaching agents set enforce_authz)
        from agentest.policy import HIGH_PRIV, permits

        blocked = False
        if self.env.enforce_authz and name in HIGH_PRIV:
            target = str(args.get("target") or args.get("order_id") or args.get("user_id") or args.get("loan") or "")
            if not permits(self.env, self.env.actor, name, target):
                blocked = True
                result = {"error": "authz_denied", "tool": name, "actor": self.env.actor, "role": self.env.role}
                succeeded = False
                err = PermissionError(f"authz denied: {self.env.role}/{self.env.actor} → {name}")
                call_meta["authz"] = "deny"
        try:
            if not blocked:
                result = self._dispatch(name, args)
                succeeded = True
                err = None
        except Exception as exc:  # noqa: BLE001 — record failed tool attempts
            result = {"error": str(exc)}
            succeeded = False
            err = exc

        tc = ToolCall(
            name=name,
            args=args,
            result=result,
            allowed=True,
            succeeded=succeeded,
            meta=call_meta,
        )
        self.trace.record(tc)
        if err is not None:
            raise err
        return result

    def _dispatch(self, name: str, args: dict[str, Any]) -> Any:
        env = self.env

        if name == "ledger.set_status":
            env.ledger.set_status(args["record_id"], args["status"])
            return {"record_id": args["record_id"], "status": args["status"]}

        if name == "ledger.get":
            return {"status": env.ledger.get(args["record_id"])}

        if name == "contact.update":
            cid = args["contact_id"]
            if cid not in env.contacts:
                env.contacts[cid] = {}
            env.contacts[cid].update(args.get("fields", {}))
            return {"contact_id": cid, "fields": env.contacts[cid]}

        if name == "order.create":
            oid = args.get("order_id") or f"O-{len(env.orders) + 1}"
            sku = args["sku"]
            qty = int(args.get("qty", 1))
            env.orders[oid] = {"sku": sku, "qty": qty}
            return {"order_id": oid}

        if name == "inventory.set":
            env.inventory[args["sku"]] = int(args["qty"])
            return {"sku": args["sku"], "qty": env.inventory[args["sku"]]}

        if name == "users.create":
            uid = args["user_id"]
            env.users[uid] = {"status": args.get("status", "PENDING")}
            return {"user_id": uid}

        if name == "users.set_status":
            uid = args["user_id"]
            if uid not in env.users:
                env.users[uid] = {}
            env.users[uid]["status"] = args["status"]
            return {"user_id": uid, "status": args["status"]}

        if name == "notify.send":
            return env.notify.send(**args)

        if name == "counters.increment":
            key = args.get("counter") or args.get("name")
            if not key:
                raise ValueError("counters.increment requires counter=")
            delta = int(args.get("delta", 1))
            env.counters[key] = env.counters.get(key, 0) + delta
            return {"counter": key, "value": env.counters[key]}

        if name in ("get_ticket", "search", "get_user", "fetch_profile", "fetch_prefs", "log_debug"):
            return {"ok": True, "tool": name, "args": args}

        if name == "update_ticket":
            tid = args.get("ticket_id", "T-1")
            env.tickets[tid] = {**env.tickets.get(tid, {}), **args.get("fields", {"updated": True})}
            return {"ticket_id": tid}

        if name == "delete_ticket":
            tid = args["ticket_id"]
            env.tickets.pop(tid, None)
            return {"deleted": tid}

        if name in ("sanctions_screen", "verify_identity"):
            return {"ok": True, "tool": name}

        if name == "open_account":
            env.extras["account_open"] = True
            return {"ok": True}

        if name in ("disburse", "charge_card", "send_wire"):
            env.extras[f"side_effect.{name}"] = env.extras.get(f"side_effect.{name}", 0) + 1
            return {"ok": True, "tool": name}

        if name == "write_summary":
            env.extras["summary"] = args.get("text", "summary")
            return {"ok": True}

        if name == "authorize":
            env.extras["authorized"] = True
            return {"ok": True}

        if name == "charge":
            env.extras["charged"] = True
            return {"ok": True}

        if name == "ticket.open":
            tid = args.get("ticket_id", "T-9")
            env.tickets[tid] = {"status": "OPEN", "order": args.get("order")}
            env.state.bind("ticket_id", tid)
            return {"ticket_id": tid}

        if name == "ticket.comment":
            tid = env.state.bindings.get("ticket_id") or args.get("ticket_id")
            if tid:
                env.tickets.setdefault(tid, {})["last_comment"] = args.get("text", "")
                env.state.bind("ticket_id", tid)
            return {"ticket_id": tid}

        if name == "ticket.close":
            tid = env.state.bindings.get("ticket_id") or args.get("ticket_id")
            if tid:
                env.tickets.setdefault(tid, {})["status"] = "CLOSED"
                env.state.bind("ticket_id", tid)
            return {"ticket_id": tid}

        if name == "todo.plan":
            for step in args.get("steps", []):
                env.extras.setdefault("todo_planned", [])
                if step not in env.extras["todo_planned"]:
                    env.extras["todo_planned"].append(step)
            return {"planned": list(env.extras.get("todo_planned", []))}

        if name == "todo.complete":
            env.state.complete(args["step"])
            return {"completed": sorted(env.state.completed)}

        if name == "todo.drop":
            # Broken-agent helper: shrink completed set
            env.state.completed.discard(args["step"])
            return {"completed": sorted(env.state.completed)}

        if name == "locale.set":
            env.state.locale = args["locale"]
            return {"locale": env.state.locale}

        if name == "extras.set":
            env.extras[args["key"]] = args["value"]
            return {"key": args["key"]}

        # --- privacy pack tools ---
        if name == "profiles.soft_delete":
            pid = args["profile_id"]
            if pid not in env.profiles:
                raise KeyError(f"unknown profile: {pid}")
            from datetime import datetime, timezone

            env.profiles[pid]["deleted_at"] = args.get(
                "deleted_at", datetime.now(timezone.utc).isoformat()
            )
            return {"profile_id": pid, "deleted_at": env.profiles[pid]["deleted_at"]}

        if name == "profiles.hard_delete":
            pid = args["profile_id"]
            env.profiles.pop(pid, None)
            return {"deleted": pid}

        if name.startswith("disclose_"):
            env.extras.setdefault("disclosures", []).append({"tool": name, **args})
            return {"ok": True, "tool": name}

        if name == "tenant.update_contact":
            tenant_id = args["tenant_id"]
            contact_id = args["contact_id"]
            if tenant_id != env.session_tenant_id:
                env.denied = True
                raise PermissionError(
                    f"cross-tenant write denied: session={env.session_tenant_id} target={tenant_id}"
                )
            from agentest.env import TenantStore

            if tenant_id not in env.tenants:
                env.tenants[tenant_id] = TenantStore()
            store = env.tenants[tenant_id]
            store.contacts[contact_id] = {
                **store.contacts.get(contact_id, {}),
                **args.get("fields", {}),
            }
            store.writes += 1
            return {"tenant_id": tenant_id, "contact_id": contact_id}

        if name == "send_email":
            to = args.get("to") or []
            if isinstance(to, str):
                to = [to]
            mail = {"to": list(to), "subject": args.get("subject", ""), "body": args.get("body", "")}
            env.emails.append(mail)
            return mail

        if name.startswith("export_"):
            req_tenant = args.get("tenant_id")
            if req_tenant != env.session_tenant_id:
                env.denied = True
                raise PermissionError(
                    f"export tenant mismatch: session={env.session_tenant_id} requested={req_tenant}"
                )
            artifact = {"tool": name, "tenant_id": req_tenant, "rows": args.get("rows", [])}
            env.exports.append(artifact)
            return artifact

        if name == "consent.grant":
            key = args["key"]
            env.state.consent[key] = True
            return {"key": key, "consent": True}

        if name == "consent.revoke":
            key = args["key"]
            env.state.consent[key] = False
            env.extras["consent_revoked"] = True
            return {"key": key, "consent": False}

        if name == "share_partner":
            if env.extras.get("consent_revoked") or env.state.consent.get("share_partner") is False:
                env.post_revoke_share_calls += 1
            env.extras.setdefault("shares", []).append(dict(args))
            return {"shared": True}

        if name == "search_users":
            # Intentionally records args for T5-004 PII inspection
            return {"ok": True, "q": args.get("q", "")}

        if name == "db.write":
            env.db_ok = True
            env.extras["db_record"] = dict(args)
            return {"ok": True}

        if name == "refund":
            oid = args.get("order_id", "O?")
            env.extras["refunded"] = oid
            return {"refunded": oid}

        if name == "memory.read":
            key = args["key"]
            env.memory_reads.append(key)
            found = key in env.memory
            return {"key": key, "found": found, "value": key if found else None}


        # --- orchestration pack tools ---
        if name == "handover.write":
            note = args.get("note") or args.get("text") or ""
            env.handover_notes = str(note)
            env.extras["last_handover"] = {
                "note": note,
                "task": args.get("task"),
                "to_role": args.get("to_role"),
                "contract": args.get("contract"),
            }
            return {"ok": True, "note": note}

        if name == "approval.grant":
            tok = env.approvals.grant(
                tool=args["tool"],
                target=args.get("target", ""),
                single_use=bool(args.get("single_use", True)),
                granted_by=args.get("granted_by") or env.actor,
                ref=args.get("ref"),
            )
            return {"ref": tok.ref, "tool": tok.tool, "target": tok.target}

        if name == "approval.consume":
            tok = env.approvals.consume(args["ref"])
            return {"ref": tok.ref, "consumed": tok.consumed, "tool": tok.tool}

        if name == "session.set_role":
            env.role = str(args["role"])
            if "actor" in args:
                env.actor = str(args["actor"])
            return {"role": env.role, "actor": env.actor}

        if name == "session.set_ttl":
            # ttl minutes from current clock
            ttl = int(args.get("ttl") or args.get("ttl_minutes") or 5)
            env.session_expires_at = int(env.clock) + ttl
            return {"session_expires_at": env.session_expires_at, "clock": env.clock}

        if name == "session.advance_clock":
            delta = int(args.get("minutes") or args.get("delta") or 1)
            env.clock = int(env.clock) + delta
            return {"clock": env.clock, "session_expires_at": env.session_expires_at}

        if name in ("refund.issue", "issue_refund"):
            oid = args.get("order_id") or args.get("target") or args.get("order") or "O?"
            # Optional consume of approval ref if provided
            ref = args.get("approval_ref") or args.get("ref")
            if ref:
                env.approvals.consume(ref)
            entry = {"order_id": oid, "tool": name, "ref": ref}
            env.refunds.append(entry)
            env.extras["refunded"] = oid
            return {"refunded": oid, "count": len(env.refunds)}

        if name == "user.delete":
            uid = args["user_id"]
            env.users.pop(uid, None)
            env.extras.setdefault("deleted_users", []).append(uid)
            return {"deleted": uid}

        if name == "admin_delete":
            target = args.get("target") or args.get("user_id") or "X"
            env.extras.setdefault("admin_deletes", []).append(target)
            return {"admin_deleted": target}

        if name == "grant_role":
            env.extras.setdefault("roles_granted", []).append(dict(args))
            return {"granted": args}

        if name == "authz.decide":
            decision = args.get("decision", "deny")
            policy_version = args.get("policy_version", "v1")
            actor = args.get("actor") or env.actor
            entry = env.authz_log.record(
                actor=actor,
                decision=decision,
                policy_version=policy_version,
                task=args.get("task", ""),
                resource=args.get("resource", ""),
            )
            return {
                "decision": entry.decision,
                "policy_version": entry.policy_version,
                "actor": entry.actor,
            }


        raise ValueError(f"unknown tool: {name}")

