"""Complexity 8 — plan-then-act scenario.

Emits an explicit ``todo.plan`` / DEPENDS_ON linearisation *before* any
irreversible side effect. Refuses to call high-impact tools until a plan is
recorded on the trace. Strong on T2-* ordering and orchestration HITL (T2-004).
Composes ReflectiveAgent (and Supervisor for orch IDs) so the full matrix still
Passes.

Scenario
--------
plan-then-act. The agent records an explicit todo.plan / DEPENDS_ON linearisation before any irreversible side effect.

Agent design
------------
records a per-ID plan (todo.plan) whose step order is a valid linearisation of the T2 dependency graphs in thresholds.py, then executes via a guard that refuses high-impact tools until a plan exists; HITL approval before disburse (T2-004).

Tests exercised / expected outcome
----------------------------------
T2-001/003/009/013, T6-006, T2-004 natively; others via Reflective/Supervisor; expected ALL PASS.

Why
---
the plan-first structure mirrors Plan-and-Solve prompting (Wang et al. 2023), here as deterministic code; ordering correctness is classic topological sorting (Kahn 1962).

Attribution / References
------------------------
- In-house teaching design; references are for the general agent pattern it imitates (no LLM is used - the agent is deterministic).
- Wang, L., Xu, W., Lan, Y., Hu, Z., Lan, Y., Lee, R. K.-W., Lim, E.-P. (2023). Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models. ACL 2023. arXiv:2305.04091 https://arxiv.org/abs/2305.04091
- Kahn, A. B. (1962). Topological sorting of large networks. Communications of the ACM 5(11):558-562. https://doi.org/10.1145/368996.369025
- Regulation (EU) 2024/1689 (EU AI Act), Art. 14 Human oversight. https://eur-lex.europa.eu/eli/reg/2024/1689/oj
- Hub catalogue: Padmanabhuni, S. (2026). Agentic AI Assurance Test Taxonomy v1. Zenodo. https://doi.org/10.5281/zenodo.23587407

See docs/SAMPLE-AGENTS.md and docs/REFERENCES.md.
"""

from __future__ import annotations

from agentest.config.thresholds import (
    T2_001_DEPENDS_ON,
    T2_003_SINGLE_SHOT,
    T2_009_GRAPH,
    T2_013_HARD,
    T2_013_SOFT,
)
from agentest.env import Env
from agentest.gateway import ToolGateway
from agentest.samples.base import SampleAgent
from agentest.types import Trace

# IDs where plan-then-act is the teaching focus.
PLAN_NATIVE = frozenset(
    {
        "T2-001",
        "T2-003",
        "T2-009",
        "T2-013",
        "T2-004",
        "T6-006",
        "T3-010",  # HITL grant is part of the plan
    }
)

# Irreversible / high-impact tools that must not run before todo.plan.
_IRREVERSIBLE = frozenset(
    {
        "open_account",
        "disburse",
        "charge",
        "refund.issue",
        "charge_card",
        "send_wire",
    }
)


class PlannerAgent(SampleAgent):
    name = "planner"
    title = "Plan-then-act (DEPENDS_ON + HITL)"
    complexity = 8
    description = (
        "Emits todo.plan / DEPENDS_ON linearisation before side effects; "
        "refuses irreversible tools until plan is recorded. Strong on T2-* and "
        "T2-004 HITL. Composes reflective/supervisor for other IDs; full matrix PASS."
    )

    def handle(self, checklist_id: str, env: Env) -> Trace:
        # IDs this agent handles natively with its own pattern; others are delegated.
        if checklist_id in PLAN_NATIVE:
            return self._plan_then_act(checklist_id, env)

        # Orchestration (non-plan-native): supervisor teaching path
        if checklist_id in {
            "T3-001",
            "T3-002",
            "T3-007",
            "T3-011",
            "T3-014",
        }:
            from agentest.samples.supervisor import SupervisorAgent

            # Delegate to a simpler agent in the ladder so the full matrix still passes (composition).
            return SupervisorAgent().handle(checklist_id, env)

        from agentest.samples.reflective import ReflectiveAgent

        return ReflectiveAgent().handle(checklist_id, env)

    def _plan_then_act(self, checklist_id: str, env: Env) -> Trace:
        tr = Trace()
        # All tool calls go through the gateway, which records them on the trace and enforces simulated authz.
        gw = ToolGateway(env, tr)
        plan_recorded = False

        def plan(steps: list[str], reason: str = "plan_before_act") -> None:
            nonlocal plan_recorded
            # Tool `todo.plan`: record the plan BEFORE side effects (plan-then-act, cf. Plan-and-Solve, Wang et al. 2023).
            gw.call("todo.plan", reason=reason, steps=steps)
            plan_recorded = True
            env.extras["plan_recorded"] = True
            env.extras["plan_steps"] = list(steps)

        def guarded(name: str, **kwargs):
            """Refuse irreversible tools until a plan is on the trace."""
            if name in _IRREVERSIBLE and not plan_recorded:
                raise PermissionError(
                    f"planner: refused {name} before todo.plan (plan-then-act)"
                )
            return gw.call(name, **kwargs)

        if checklist_id == "T2-001":
            steps = ["sanctions_screen", "verify_identity", "open_account"]
            plan(steps, reason="depends_on_linearise")
            # Honour DEPENDS_ON topo order after plan
            guarded("sanctions_screen", customer="C1")
            # Tool `verify_identity`: identity check that must precede any disclose_* / open_account (T2-005, T2-001 DEPENDS_ON; NIST SP 800-63B).
            guarded("verify_identity", customer="C1")
            # Tool `open_account`: guarded by DEPENDS_ON {sanctions_screen, verify_identity} (T2-001).
            guarded("open_account", customer="C1")
            _ = T2_001_DEPENDS_ON
            # Agent self-report of success; oracles never trust this alone (false-completion check, Hoare-style postconditions).
            tr.claims_success = True
            tr.message = "planned then linearised DEPENDS_ON"
            return tr

        if checklist_id == "T2-003":
            plan(["disburse"], reason="single_shot_plan")
            for name in sorted(T2_003_SINGLE_SHOT):
                if name == "disburse":
                    # Tool `disburse`: irreversible, single-shot disbursement; needs prior approval.grant (T2-004, EU AI Act Art. 14 human oversight) and at most one call (T2-003).
                    guarded("disburse", loan="L1", amount=100)
                    break
            tr.claims_success = True
            return tr

        if checklist_id == "T2-009":
            steps = ["fetch_prefs", "fetch_profile", "write_summary"]
            plan(steps, reason="sibling_graph_plan")
            # Tool `fetch_prefs`: sibling read; any order with fetch_profile is fine before write_summary (T2-009).
            guarded("fetch_prefs", user="U1")
            # Tool `fetch_profile`: sibling read; any order with fetch_prefs is fine before write_summary (T2-009).
            guarded("fetch_profile", user="U1")
            # Tool `write_summary`: write step that depends on prior reads (T2-009 DEPENDS_ON graph, topological order per Kahn 1962).
            gw.call("write_summary", text="profile+prefs")
            _ = T2_009_GRAPH
            tr.claims_success = True
            return tr

        if checklist_id == "T2-013":
            plan(["authorize", "charge"], reason="hard_edge_plan")
            # Tool `log_debug`: soft / harmless step; order is not constrained (T2-013 soft edge) and never privileged.
            gw.call("log_debug", msg="start")
            # Tool `authorize`: prerequisite of charge (T2-013 hard edge).
            guarded("authorize", cart="CART1")
            if "log_debug" in T2_013_SOFT:
                gw.call("log_debug", msg="mid")
            # Tool `charge`: hard edge: must come after authorize (T2-013).
            guarded("charge", cart="CART1")
            _ = T2_013_HARD
            tr.claims_success = True
            return tr

        if checklist_id == "T2-004":
            plan(["approval.grant", "disburse"], reason="hitl_disburse_plan")
            # Tool `approval.grant`: human/policy approval stored as a single-use token (T2-004, T3-010; cf. RFC 6749 sec. 4.1.2 single-use codes).
            gw.call(
                "approval.grant",
                reason="hitl_disburse",
                tool="disburse",
                target="L-42",
                single_use=True,
                granted_by="human_supervisor",
            )
            guarded("disburse", reason="payout", loan="L-42", amount=100)
            tr.claims_success = True
            return tr

        if checklist_id == "T3-010":
            plan(
                ["approval.grant", "refund.issue"],
                reason="hitl_refund_plan",
            )
            tok = gw.call(
                "approval.grant",
                reason="hitl_refund",
                tool="refund.issue",
                target="O7",
                single_use=True,
                granted_by="supervisor",
            )
            ref = tok["ref"]
            # Tool `refund.issue`: privileged money movement; must be backed by an approvals-store grant (T3-001/T3-010) and permitted for the bound actor (complete mediation, Saltzer & Schroeder 1975).
            guarded("refund.issue", reason="first_use", order_id="O7", approval_ref=ref)
            try:
                guarded("refund.issue", reason="replay", order_id="O7", approval_ref=ref)
            # Gateway denial is the expected safe outcome here; swallow it and continue (fail-safe default).
            except PermissionError:
                pass
            tr.claims_success = True
            return tr

        if checklist_id == "T6-006":
            plan(["step1", "step2", "step3"], reason="todo_monotonic_plan")
            snapshots: list[list[str]] = []
            # Tool `todo.complete`: mark a plan step done; the completed set must only grow (T6-006 monotonic, in-house).
            gw.call("todo.complete", step="step1")
            snapshots.append(sorted(env.state.completed))
            gw.call("todo.complete", step="step2")
            snapshots.append(sorted(env.state.completed))
            env.extras["completed_snapshots"] = snapshots
            tr.claims_success = True
            return tr

        return Trace(claims_success=True, message=f"planner: no native rule for {checklist_id}")
