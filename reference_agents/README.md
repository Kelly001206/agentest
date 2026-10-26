# Reference agents (vendored)

Twelve small, runnable agents used as **real systems under test** for the 41 real
checks in `src/agentest/real/`. They are vendored here so this repository is
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

All data is fictional (`.example` domains, canary strings such as `CANARY-7Q`).

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
a08 additionally needs Node 22 and a local `n8n` install (`N8N_DIR`).
a10 executes model-written code with a deny-list executor in a temp dir - this is
**not** a strong sandbox; run it only on a throw-away machine.
