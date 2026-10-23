"""Wrapper: complexity-graded sample agent `reflective`."""

from agentest.samples import get_sample

_agent = get_sample("reflective")
NAME = _agent.name
TITLE = _agent.title
COMPLEXITY = _agent.complexity
handle = _agent.handle
