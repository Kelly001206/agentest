"""SampleAgent protocol — teaching-facing API for checklist learners."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from agentest.env import Env
from agentest.types import Trace


@dataclass
class SampleAgentInfo:
    """Metadata shown by `agentest samples`."""

    name: str
    title: str
    complexity: int  # 1..15 (11–15 = expected-fail band)
    description: str


class SampleAgent(ABC):
    """Base class for teaching sample agents of increasing complexity."""

    name: str
    title: str
    complexity: int
    description: str

    def info(self) -> SampleAgentInfo:
        """Return this agent's descriptive metadata."""
        return SampleAgentInfo(
            name=self.name,
            title=self.title,
            complexity=self.complexity,
            description=self.description,
        )

    @abstractmethod
    def handle(self, checklist_id: str, env: Env) -> Trace:
        """Run one episode for ``checklist_id`` against a fresh ``env``."""


# Multi-run catalogue IDs: handle() runs a *single* episode; cases.multi_run loops k times.
MULTI_RUN_EPISODE_IDS = frozenset({"T1-002", "T1-003"})
