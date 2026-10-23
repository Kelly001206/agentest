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

    def call(self, name: str, **args: Any) -> Any:
        try:
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

        raise ValueError(f"unknown tool: {name}")

