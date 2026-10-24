"""Wrapper: complexity-graded sample agent `reflective`.

The full scenario, agent design, tests exercised, expected pass/fail and
literature references are documented in the module docstring of
src/agentest/samples/reflective.py and in docs/SAMPLE-AGENTS.md / docs/REFERENCES.md.
"""

from agentest.samples import get_sample

_agent = get_sample("reflective")
NAME = _agent.name
TITLE = _agent.title
COMPLEXITY = _agent.complexity
handle = _agent.handle
