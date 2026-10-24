"""Thin example entry — delegates to agentest.agents.broken.

The broken agent replays each case's seeded-defect trajectory; every oracle
must FAIL it (proves oracles are not vacuous). See docs/REFERENCES.md.
"""

from agentest.agents.broken import run

__all__ = ["run"]
