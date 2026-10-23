# M0 backlog — `v0.1.0`

Solo, one ID: **T1-001** (Terminal postconditions after a single task).

## Tasks

1. [ ] `pyproject.toml` + `agentest` CLI entrypoint
2. [ ] `Env` + mock ledger fixture (`fixtures/ledger.py`)
3. [ ] Mock tool gateway (allowlist stub)
4. [ ] Golden agent that sets expected ledger statuses
5. [ ] `examples/broken_agent` that claims success without writes
6. [ ] `tests/functional/test_t1_001.py` — Pass golden, Fail broken
7. [ ] GitHub Actions: run T1-001 on PR
8. [ ] Sync `packs/functional.csv` row T1-001 into `catalog/` (read-only pin)

## Acceptance

- `agentest run --ids T1-001` exits 0 on golden, non-zero on broken
- CI green on main
- README quick start works in <10 minutes
