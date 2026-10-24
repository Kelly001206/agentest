"""Complexity 12 — hallucinator (expected-fail): explainability anti-pattern.

Passes most suites via goldens. Fails every explainability ID: claims API
success without db.write, fake citations, missing tool reasons, silent
memory use, invented tools in explanations.

Scenario
--------
EXPECTED-FAIL: explainability anti-pattern.

Agent design
------------
play_selective with broken sequences on EXPLAINABILITY_IDS: api_success without the DB write, missing reason codes, silent memory use, explanation inventing tools.

Tests exercised / expected outcome
----------------------------------
fails T1-018, T3-006, T5-015, T6-007, T7-009 (T3-006 also counted in orchestration); others pass.

Why
---
Why it must fail: unfaithful explanations are detected against the trace, not by fluency.

Attribution / References
------------------------
- In-house teaching design; references are for the general agent pattern it imitates (no LLM is used - the agent is deterministic).
- Jacovi, A., Goldberg, Y. (2020). Towards Faithfully Interpretable NLP Systems: How Should We Define and Evaluate Faithfulness? ACL 2020. https://doi.org/10.18653/v1/2020.acl-main.386
- Kim, W., Park, S., In, Y., Kim, S., Lee, D., Park, C. (2025). Beyond the Final Answer: Evaluating the Reasoning Trajectories of Tool-Augmented Agents (proposes the TRACE framework). arXiv:2510.02837. https://arxiv.org/abs/2510.02837
- Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., Cao, Y. (2023). ReAct: Synergizing Reasoning and Acting in Language Models. ICLR 2023. arXiv:2210.03629
- Hub catalogue: Padmanabhuni, S. (2026). Agentic AI Assurance Test Taxonomy v1. Zenodo. https://doi.org/10.5281/zenodo.23587407

See docs/SAMPLE-AGENTS.md and docs/REFERENCES.md.
"""

from __future__ import annotations

from agentest.cases.registry import EXPLAINABILITY_IDS
from agentest.env import Env
from agentest.samples.base import SampleAgent
from agentest.samples.playbook import play_selective
from agentest.types import Trace

FAIL_IDS = frozenset(EXPLAINABILITY_IDS)


class HallucinatorAgent(SampleAgent):
    name = "hallucinator"
    title = "Hallucinator (explainability anti-pattern)"
    complexity = 12
    description = (
        "EXPECTED-FAIL: golden except explainability IDs — fake citations, "
        "api_success without tools, silent memory. Teaches faithfulness oracles."
    )

    def handle(self, checklist_id: str, env: Env) -> Trace:
        # Golden trajectory for most IDs, broken trajectory for FAIL_IDS: a deterministic expected-fail profile.
        return play_selective(checklist_id, env, fail_ids=FAIL_IDS)
