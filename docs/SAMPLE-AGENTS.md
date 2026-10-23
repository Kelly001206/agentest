# Sample agents (complexity 1–15)

Fifteen **deterministic** teaching agents live under `src/agentest/samples/`.  
They are **additional** to the oracle fixtures `golden` / `broken`.

## Green ladder (1–10)

| name | cx | idea | expected matrix |
|:-----|---:|:-----|:----------------|
| `stub` | 1 | Claims success, **zero** real tools; forges bad orch traces | mostly **FAIL** |
| `eager` | 2 | Calls tools but ignores order, fences, authz, TTL, HITL | mostly **FAIL** |
| `scripted` | 3 | Hardcoded playbook: `get_case(id).golden(env)` | **all PASS** |
| `policy` | 4 | Rule-engine over `samples/policies/*` (incl. orchestration) | **all PASS** |
| `reflective` | 5 | Policy + faithful explanations / bias | **all PASS** |
| `supervisor` | 6 | Planner: approvals, signed handoff contract, downgrade, TTL | **all PASS** |
| `handoff` | 7 | Receiver: store≠prose, authz.decide, no ambient admin, TTL | **all PASS** |
| `planner` | 8 | **Plan-then-act**: `todo.plan` / DEPENDS_ON before side effects; HITL | **all PASS** |
| `critic` | 9 | **Generate–critique–repair** before `claims_success`; faithful explain fields | **all PASS** |
| `federation` | 10 | **Multi-tenant federation**: tenant fence + downgrade + TTL + single-use | **all PASS** |

Matrix totals sum suites (`functional`+`privacy`+`explainability`+`bias_fairness`+`orchestration`).  
T3-006 appears in both explainability and orchestration thematic lists (one CaseSpec).

## Expected-fail scenarios (11–15)

Five **teaching-negative** agents: each reuses the golden playbook for most IDs,
then deliberately runs the case **broken** sequence on a category (or planning
subset). Oracles catch real mistakes while the rest of the matrix stays green.

| name | cx | teaches | fail focus | typical matrix |
|:-----|---:|:--------|:-----------|:---------------|
| `leaky` | 11 | Privacy | all `PRIVACY_IDS` (8) | ~34/42 pass |
| `hallucinator` | 12 | Explainability / faithfulness | all `EXPLAINABILITY_IDS` (5; T3-006 double-counted in matrix) | ~36/42 pass |
| `biased` | 13 | Bias / fairness | all `BIAS_FAIRNESS_IDS` (3) | ~39/42 pass |
| `overreach` | 14 | Orchestration / authz | all `ORCHESTRATION_IDS` (8; T3-006 double-counted) | ~33/42 pass |
| `flaky_plan` | 15 | Planning / handoff half-done | T2-001/003/009/013, T6-006, T2-004, T3-010 | ~35/42 pass |

These five are in `MATRIX_EXPECTED_FAIL` and **not** in `MATRIX_MUST_PASS`.  
`agentest matrix` exit status still only requires the green ladder (+ golden).

See [`SCENARIOS-EXPECTED-FAIL.md`](SCENARIOS-EXPECTED-FAIL.md).

## Why fifteen levels?

1. **stub** — Success flags ≠ terminal/authz truth.
2. **eager** — Classic fails: wrong order, hard-delete, trust handover prose, skip HITL, immortal session.
3. **scripted** — Playbook reuses case goldens.
4. **policy** — Shared rules including `orchestration_rules.py`.
5. **reflective** — Explainability + bias on top of policy.
6. **supervisor** — Multi-agent planner / HITL grantor.
7. **handoff** — Receiving worker with independent authz.
8. **planner** — Explicit plan recorded before irreversible tools (T2-* + T2-004).
9. **critic** — Self-critique loop repairs incomplete explainability before success.
10. **federation** — Hardest green: session tenant + no ambient authority + TTL + single-use together.
11. **leaky** — Privacy oracles fire while functional still passes.
12. **hallucinator** — Faithfulness oracles fire (fake citations / api_success).
13. **biased** — Metamorphic fairness oracles fire on skewed labels.
14. **overreach** — Orch/authz oracles fire (ambient authority, skip HITL).
15. **flaky_plan** — Plan/DEPENDS_ON/HITL subset fails; other suites mostly OK.

## Scenarios 8–10 (detail)

See [`SCENARIOS-8-10.md`](SCENARIOS-8-10.md) for teaching notes on planner / critic / federation.

## How to run

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[dev]"

agentest samples
agentest samples --failing   # cx 11–15 only

agentest run --suite privacy --agent leaky
agentest run --suite explainability --agent hallucinator
agentest run --suite bias_fairness --agent biased
agentest run --suite orchestration --agent overreach
agentest run --suite functional --ids T2-001 --agent flaky_plan

agentest matrix
# Exit 0 iff scripted…federation/(golden) all-pass.
# stub/eager + leaky…flaky_plan failures are expected.
```

See [`ORCHESTRATION.md`](ORCHESTRATION.md) for Hub ↔ runner mapping.

## Constraints

- No third-party eval frameworks.
- Deterministic scripted agents only (no LLM in the harness).
- Keep golden/broken oracles green.
- Do not add expected-fail agents to `MATRIX_MUST_PASS`.
