"""A1 - Rule-based ticket router. NO LLM, NO model of any kind.
Same rules as workflow.n8n.json (n8n Code + Switch nodes); this Python twin
lets the demo Space run without an n8n server."""
import re

RULES = [  # (queue, priority, keyword regex) first match wins
    ("security", "P1", r"\b(phish|hack|breach|password reset|fraud|unauthori[sz]ed)\b"),
    ("billing", "P2", r"\b(refund|invoice|charged|payment|billing|overcharg)"),
    ("outage", "P1", r"\b(down|outage|not loading|500 error|cannot log ?in)\b"),
    ("account", "P3", r"\b(change (my )?email|update address|close (my )?account|profile)\b"),
]
PII = [(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b", "[CARD]"), (r"[\w.+-]+@[\w-]+\.[\w.]+", "[EMAIL]"), (r"\b\d{10}\b", "[PHONE]")]

def route(ticket: dict) -> dict:
    text = f"{ticket.get('subject','')} {ticket.get('body','')}".lower()
    trace = []
    queue, prio, rule = "general", "P4", "default"
    for q, p, rx in RULES:
        if re.search(rx, text):
            queue, prio, rule = q, p, rx; break
    trace.append({"step": "match_rules", "matched": rule})
    redacted = ticket.get("body", "")
    for rx, tag in PII:
        redacted = re.sub(rx, tag, redacted)
    trace.append({"step": "redact_pii", "changed": redacted != ticket.get("body", "")})
    return {"ticket_id": ticket.get("id"), "queue": queue, "priority": prio, "matched_rule": rule,
            "body_redacted": redacted, "write_actions": []}, trace
