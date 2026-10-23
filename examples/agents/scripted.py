"""Wrapper: complexity-graded sample agent `scripted`."""

from agentest.samples import get_sample

_agent = get_sample("scripted")
NAME = _agent.name
TITLE = _agent.title
COMPLEXITY = _agent.complexity
handle = _agent.handle
