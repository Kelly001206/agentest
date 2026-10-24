"""Wrapper: complexity-graded sample agent `eager`.

The full scenario, agent design, tests exercised, expected pass/fail and
literature references are documented in the module docstring of
src/agentest/samples/eager.py and in docs/SAMPLE-AGENTS.md / docs/REFERENCES.md.
"""

from agentest.samples import get_sample

_agent = get_sample("eager")
NAME = _agent.name
TITLE = _agent.title
COMPLEXITY = _agent.complexity
handle = _agent.handle
