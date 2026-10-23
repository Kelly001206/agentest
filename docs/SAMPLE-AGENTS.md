# Sample agents (complexity 1–10)

Ten **deterministic** teaching agents live under `src/agentest/samples/`.  
They are **additional** to the oracle fixtures `golden` / `broken`.

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

## Why ten levels?

1. **stub** — Success flags ≠ terminal/authz truth.
2. **eager** — Classic fails: wrong order, hard-delete, trust handover prose, skip HITL, immortal session.
3. **scripted** — Playbook reuses case goldens.
4. **policy** — Shared rules including `orchestration_rules.py`.
5. **reflective** — Explainability + bias on top of policy.
6. **supervisor** — Multi-agent planner / HITL grantor.
7. **handoff** — Receiving worker with independent authz.
8. **planner** — Explicit plan recorded before irreversible tools (T2-* + T2-004).
9. **critic** — Self-critique loop repairs incomplete explainability before success.
10. **federation** — Hardest: session tenant + no ambient authority + TTL + single-use together.

## Scenarios 8–10 (detail)

See [`SCENARIOS-8-10.md`](SCENARIOS-8-10.md) for teaching notes on planner / critic / federation.

## How to run

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[dev]"

agentest samples

agentest run --suite orchestration --agent stub
agentest run --suite functional --agent planner
agentest run --suite explainability --agent critic
agentest run --suite orchestration --agent federation

agentest matrix
# Exit 0 iff scripted…federation/(golden) all-pass.
# stub/eager failures are expected.
```

See [`ORCHESTRATION.md`](ORCHESTRATION.md) for Hub ↔ runner mapping.

## Constraints

- No third-party eval frameworks.
- Deterministic scripted agents only (no LLM in the harness).
- Keep golden/broken oracles green.
