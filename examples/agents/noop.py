"""Wrapper: complexity-graded sample agent `noop`.

The full scenario, agent design, tests exercised, expected pass/fail and
literature references are documented in the module docstring of
src/agentest/samples/noop.py and in docs/SAMPLE-AGENTS.md / docs/REFERENCES.md.
"""

from agentest.samples import get_sample

# Resolve the sample agent from the registry; scenario, design and references are in its module docstring.
_agent = get_sample("noop")
NAME = _agent.name
TITLE = _agent.title
COMPLEXITY = _agent.complexity
# Expose handle(checklist_id, env) -> Trace so this file can be used as a stand-alone example agent.
handle = _agent.handle
