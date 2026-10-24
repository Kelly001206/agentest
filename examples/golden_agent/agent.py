"""Thin example entry — delegates to agentest.agents.golden.

The golden agent replays each case's correct reference trajectory; every
oracle must PASS it. Per-oracle algorithms and references live in the
docstrings of src/agentest/cases/*.py (see docs/REFERENCES.md).
"""

from agentest.agents.golden import run

__all__ = ["run"]
