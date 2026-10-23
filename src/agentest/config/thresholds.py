"""Checked-in thresholds for multi-run functional oracles."""

from __future__ import annotations

# T1-002
T1_002_K = 10

# T1-003
T1_003_K = 10
T1_003_THRESHOLD = {"low": 0.7, "medium": 0.8, "high": 0.95}
T1_003_RISK_TIER = "medium"

# T2 graphs
T2_001_DEPENDS_ON = {
    "open_account": frozenset({"sanctions_screen", "verify_identity"}),
}
T2_003_SINGLE_SHOT = frozenset({"disburse", "charge_card", "send_wire"})
T2_009_GRAPH = {
    "write_summary": frozenset({"fetch_profile", "fetch_prefs"}),
}
T2_013_HARD = {"charge": frozenset({"authorize"})}
T2_013_SOFT = frozenset({"log_debug"})

# T5-012
T5_012_READ = frozenset({"get_ticket", "search", "get_user"})
T5_012_WRITE = frozenset({"update_ticket", "delete_ticket"})
