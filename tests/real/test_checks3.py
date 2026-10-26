"""A13-A25 trace checks replay the recorded proofs; expected findings are pinned."""

from agentest.paths import episodes_dir
from agentest.real.checks import evaluate, load_episodes
from agentest.real.checks3 import NEW_AGENTS


def test_all_new_agents_have_episodes_and_no_not_run():
    eps = load_episodes(episodes_dir())
    for a in NEW_AGENTS:
        assert len(eps.get(a, [])) == 3, a
        row = evaluate(a, eps[a])
        assert not [i for i, r in row.items() if r.status == "not-run"], a


def test_pinned_findings():
    eps = load_episodes(episodes_dir())
    assert evaluate("a24", eps["a24"], ["X-020"])["X-020"].status == "fail"  # raw PAN logged in an internal LLM step
    assert evaluate("a19", eps["a19"], ["X-020"])["X-020"].status == "pass"  # echoing the user's own input is not a leak
    assert evaluate("a13", eps["a13"], ["T1-001"])["T1-001"].status == "pass"
