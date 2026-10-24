"""Thin example entry — delegates to agentest.agents.golden.

The golden agent replays each case's correct reference trajectory; every
oracle must PASS it. Per-oracle algorithms and references live in the
docstrings of src/agentest/cases/*.py (see docs/REFERENCES.md).
"""

# Re-export: run(env) applies the correct ledger decisions (T1-001 PASS reference).
from agentest.agents.golden import run

__all__ = ["run"]
