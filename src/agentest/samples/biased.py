"""Complexity 13 — biased (expected-fail): bias / fairness anti-pattern.

Passes functional / privacy / explain / orch. Fails all bias_fairness IDs
with skewed metamorphic labels (Hinglish/ES asymmetry, demographic flip).

Scenario
--------
EXPECTED-FAIL: bias / fairness anti-pattern.

Agent design
------------
play_selective with broken sequences on BIAS_FAIRNESS_IDS: Hinglish bypass (T7-004), demographic name flip (T7-007), Spanish asymmetry (T7-011).

Tests exercised / expected outcome
----------------------------------
fails the 3 bias IDs; others pass.

Why
---
Why it must fail: metamorphic / counterfactual-token oracles detect label changes under protected-attribute or language substitution.

Attribution / References
------------------------
- In-house teaching design; references are for the general agent pattern it imitates (no LLM is used - the agent is deterministic).
- Chen, T. Y., Cheung, S. C., Yiu, S. M. (1998). Metamorphic Testing: A New Approach for Generating Next Test Cases. Tech. Rep. HKUST-CS98-01; republished arXiv:2002.12543
- Garg, S., Perot, V., Limtiaco, N., Taly, A., Chi, E. H., Beutel, A. (2019). Counterfactual Fairness in Text Classification through Robustness. AIES 2019. https://doi.org/10.1145/3306618.3317950 (counterfactual token fairness)
- Kusner, M. J., Loftus, J., Russell, C., Silva, R. (2017). Counterfactual Fairness. NeurIPS 2017. arXiv:1703.06856 (conceptual motivation; we do NOT fit a causal model)
- Hub catalogue: Padmanabhuni, S. (2026). Agentic AI Assurance Test Taxonomy v1. Zenodo. https://doi.org/10.5281/zenodo.23587407

See docs/SAMPLE-AGENTS.md and docs/REFERENCES.md.
"""

from __future__ import annotations

from agentest.cases.registry import BIAS_FAIRNESS_IDS
from agentest.env import Env
from agentest.samples.base import SampleAgent
from agentest.samples.playbook import play_selective
from agentest.types import Trace

FAIL_IDS = frozenset(BIAS_FAIRNESS_IDS)


class BiasedAgent(SampleAgent):
    name = "biased"
    title = "Biased (fairness anti-pattern)"
    complexity = 13
    description = (
        "EXPECTED-FAIL: golden except bias_fairness IDs — skewed labels by "
        "locale/demographic. Teaches metamorphic fairness oracles."
    )

    def handle(self, checklist_id: str, env: Env) -> Trace:
        return play_selective(checklist_id, env, fail_ids=FAIL_IDS)
