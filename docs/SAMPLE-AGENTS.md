# Sample agents (complexity 1–7)

Seven **deterministic** teaching agents live under `src/agentest/samples/`.  
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

Matrix totals sum suites (`functional`+`privacy`+`explainability`+`bias_fairness`+`orchestration`).  
T3-006 appears in both explainability and orchestration thematic lists (one CaseSpec).

## Why seven levels?

1. **stub** — Success flags ≠ terminal/authz truth.
2. **eager** — Classic fails: wrong order, hard-delete, trust handover prose, skip HITL, immortal session.
3. **scripted** — Playbook reuses case goldens.
4. **policy** — Shared rules including `orchestration_rules.py`.
5. **reflective** — Explainability + bias on top of policy.
6. **supervisor** — Multi-agent planner / HITL grantor.
7. **handoff** — Receiving worker with independent authz.

## How to run

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[dev]"

agentest samples

agentest run --suite orchestration --agent stub
agentest run --suite orchestration --agent supervisor
agentest run --suite orch --agent handoff

agentest matrix
# Exit 0 iff scripted/policy/reflective/supervisor/handoff/(golden) all-pass.
```

See [`ORCHESTRATION.md`](ORCHESTRATION.md) for Hub ↔ runner mapping.

## Constraints

- No third-party eval frameworks.
- Deterministic scripted agents only (no LLM in the harness).
- Keep golden/broken oracles green.
