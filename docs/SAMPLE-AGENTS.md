# Sample agents (complexity 1–5)

Five **deterministic** teaching agents live under `src/agentest/samples/`.  
They are **additional** to the oracle fixtures `golden` / `broken` (which remain Pass/Fail references for every Hub ID).

| name | cx | idea | expected matrix |
|:-----|---:|:-----|:----------------|
| `stub` | 1 | Claims success, **zero** tool calls; may corrupt env without tools | mostly **FAIL** (some absence-tolerant IDs still Pass) |
| `eager` | 2 | Calls tools but ignores order, fences, soft-delete, verify-before-disclose, single-shot, explanations, bias | mostly **FAIL** (some accidental passes OK) |
| `scripted` | 3 | Hardcoded playbook: `get_case(id).golden(env)` | **34/34 PASS** |
| `policy` | 4 | Rule-engine over shared `samples/policies/*` (DEPENDS_ON, write fences, privacy, bias) | **34/34 PASS** |
| `reflective` | 5 | Policy + faithful explanations, `memory_citations`, `cited_steps`, `api_success` | **34/34 PASS** |

## Why five levels?

1. **stub** — Learners see that `claims_success=True` alone is not enough. Oracles check terminal world state, tool order, and side-effect fences.
2. **eager** — Shows *how* agents fail: wrong order (T2), hard-delete (T1-016), disclose-before-verify (T2-005), missing reason codes (T5-015), demographic flip (T7-007).
3. **scripted** — Honest playbook that reuses case goldens. Guarantees Pass before you invent your own policy.
4. **policy** — Extract shared rules (`samples/policies/`) instead of a giant if/elif of golden copies.
5. **reflective** — Add explainability fields and bias-aware decisions on top of policy.

## How to run

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[dev]"

# List the five
agentest samples

# Run one suite against one sample
agentest run --suite functional --agent stub          # expect many FAIL / exit 1
agentest run --suite privacy --agent scripted         # exit 0
agentest run --suite explainability --agent reflective
agentest run --suite bias_fairness --agent policy

# Full learner matrix (all suites × samples + golden)
agentest matrix
# Exit 0 iff scripted, policy, reflective, and golden are all-pass.
# stub/eager failures are expected and do NOT fail the process.
```

Oracle agents still work:

```bash
agentest run --suite functional --agent golden
agentest run --suite functional --agent broken   # exit 1
```

## Architecture hook

`CaseSpec.run(agent_name)` accepts `golden|broken|stub|eager|scripted|policy|reflective`.

- `golden` / `broken` → case-local agent fns (existing path).
- Sample names → `get_sample(name).handle(checklist_id, env)` then the case oracle.
- Multi-run IDs (`T1-002`, `T1-003`): `handle` runs **one** episode; `cases.multi_run` loops `k` times.

## How to add a sixth sample

1. Subclass `SampleAgent` in `src/agentest/samples/my_agent.py` with `name`, `title`, `complexity`, `description`, and `handle`.
2. Register it in `samples/__init__.py` (`SAMPLE_AGENT_NAMES` + `_build()`).
3. Add the name to `cases.registry.SAMPLE_AGENTS` / `ALL_AGENTS`.
4. Document it here and cover it in `tests/samples/`.
5. Decide whether it belongs in `MATRIX_MUST_PASS` (full Pass) or is a deliberate fail-teaching agent like stub/eager.

## Constraints

- No third-party eval frameworks.
- Deterministic scripted agents only (no LLM in the harness).
- Keep golden/broken oracles green — they remain the Pass/Fail fixtures for pytest.
