# Reference agents (vendored)

Twenty-five runnable agents used as **real systems under test** for the 130 real
checks in `src/agentest/real/` (a01-a12: probe sets in `checks.py`/`checks2.py`; a13-a25: orchestrators, crews,
swarms and multi-step flows checked at trace level in `checks3.py` over their three recorded proof cases). They are vendored here so this repository is
self-contained; nothing is fetched from another repository at test time.

| key | folder | framework | shape |
|---|---|---|---|
| a01 | a01_rule_router | plain Python (n8n twin) | rule-based ticket router, no model |
| a02 | a02_llm_classifier | OpenAI-compatible client | single-call classifier/extractor |
| a03 | a03_rag_faq | LlamaIndex | RAG FAQ with citations |
| a04 | a04_prompt_chain | LangGraph | draft -> check -> translate -> human review |
| a05 | a05_support_handoffs | OpenAI Agents SDK | triage -> billing/FAQ handoffs, refund = pending request |
| a06 | a06_react_assistant | LangGraph ReAct | calendar/email assistant, send needs interrupt() approval |
| a07 | a07_mcp_data_agent | AutoGen + MCP (stdio) | read-only SQL data agent |
| a08 | a08_n8n_mcp_agent | n8n AI Agent + MCP (HTTP) | helpdesk agent with window memory |
| a09 | a09_research_crew | CrewAI | researcher -> writer -> reviewer over an offline corpus |
| a10 | a10_coding_team | AutoGen team | planner/coder/executor/reviewer; patch proposed, never merged |
| a11 | a11_evaluator_optimizer | OpenAI Agents SDK | guardrail + generator + critic loop |
| a12 | a12_durable_approval | LangGraph + SQLite + MCP | invoice approval; pays only on an exact scoped token |
| a13 | a13_supervisor_ops | LangGraph StateGraph supervisor + 3 tool-calling worker agents | hierarchical supervisor (customer ops) |
| a14 | a14_mapreduce_contracts | LangGraph Send API fan-out (parallel clause sub-agents) + reduce | map-reduce contract review |
| a15 | a15_plan_execute | LangGraph (planner -> executor -> replanner loop) | plan-and-execute with replanning |
| a16 | a16_mcp_multiserver | AutoGen AgentChat AssistantAgent + 2 McpWorkbench (stdio MCP servers) | multi-server MCP agent (supply chain) |
| a17 | a17_multihop_rag | LangGraph (hop planner -> BM25 retrieve loop -> answer -> citation verifier) | multi-hop RAG with verified citations |
| a18 | a18_crew_hierarchical | CrewAI Process.hierarchical (manager_llm + 3 specialist agents) | vendor due-diligence crew (hierarchical) |
| a19 | a19_memory_assistant | LangGraph + SqliteStore (one OS process per session) | advisor assistant with memory across sessions |
| a20 | a20_debate_consensus | AutoGen AgentChat SelectorGroupChat (3 debaters + moderator) | credit committee debate (consensus) |
| a21 | a21_negotiation | AutoGen AgentChat RoundRobinGroupChat (buyer with tools vs seller agent) | procurement negotiation (buyer vs seller) |
| a22 | a22_guarded_browser | OpenAI Agents SDK + text-browser tools over a local mock site | guarded browser agent (local mock shop) |
| a23 | a23_n8n_orchestrator | n8n 2.22.6 (Execute Workflow -> 3 sub-workflows, HTTP node -> local LLM) | n8n orchestrator with sub-workflows |
| a24 | a24_kyc_flow | CrewAI Flows (@start/@listen/@router) + deterministic KYC rules | KYC document pipeline |
| a25 | a25_incident_swarm | AutoGen AgentChat Swarm (triage -> investigator -> remediator -> human handoff) | incident-response triage swarm |

All data is fictional (`.example` domains, canary strings such as `CANARY-7Q`).

## Running A13-A25 live

Each folder has `run_demo.py` (three cases with a wall-clock budget; rewrites that folder's `proof/`) and offline
unit tests:

```bash
python -m pytest -q --import-mode=importlib reference_agents/common/tests reference_agents/a1[3-9]_*/tests reference_agents/a2*/tests   # 67 offline unit tests
python reference_agents/a24_kyc_flow/run_demo.py      # needs the local model server below
python - <<'PY'                                       # convert proofs to replay episodes
import json, glob, os
for d in sorted(glob.glob("reference_agents/a[12][0-9]_*")):
    a = os.path.basename(d)[:3]
    if a < "a13": continue
    rows = [json.loads(l) for l in open(f"{d}/proof/run.jsonl")]
    with open(f"fixtures/real/episodes/{a}.jsonl", "w") as f:
        for i, r in enumerate(rows):
            f.write(json.dumps({"agent": a, "probe": f"case{i}", "rep": 0, "input": r["input"], "output": r["output"], "trace": r["trace"],
                                "extra": {k: r.get(k) for k in ("case", "check_passed", "note", "model", "framework")}, "error": None}) + "\n")
PY
```

## Running live (optional, zero cost)

CI does **not** run these agents; it replays the recorded episodes in
`fixtures/real/episodes/`. To re-record:

```bash
python -m venv .venv-ref && . .venv-ref/bin/activate
pip install -r reference_agents/requirements-reference.txt && pip install -e .
# local open model, OpenAI-compatible, on :8008 (GGUF file must already be on disk)
REF_GGUF=/path/to/Qwen2.5-7B-Instruct-Q4_K_M.gguf python reference_agents/common/gguf_llm_server.py &
python -m agentest.real.live --agent a05        # writes fixtures/real/episodes/a05.jsonl
agentest real --md fixtures/real/RESULTS.md --json fixtures/real/results.json
```

`common/local_llm_server.py` is a slower transformers fallback for a 1.5B model.
a08 and a23 additionally need Node 22 and a local `n8n` install (`N8N_DIR`; set `N8N_NODE_BIN` to the Node 22 binary).
a10 executes model-written code with a deny-list executor in a temp dir - this is
**not** a strong sandbox; run it only on a throw-away machine.
