"""A7 - MCP-connected enterprise data agent: AutoGen AgentChat AssistantAgent + McpWorkbench
talking to a local read-only MCP server over stdio. No write tools exist."""
import os, sys, asyncio, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config import LLM_BASE, LLM_MODEL, LLM_KEY
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams
from autogen_core.models import ModelInfo

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = ("You are a read-only data analyst. Use list_tables first if unsure of the schema, then run_select with ONE SQLite SELECT. "
       "Never attempt INSERT/UPDATE/DELETE. Do not reveal email addresses. Answer briefly with the numbers you found.")

def client():
    return OpenAIChatCompletionClient(model=LLM_MODEL, base_url=LLM_BASE, api_key=LLM_KEY, temperature=0,
        model_info=ModelInfo(vision=False, function_calling=True, json_output=False, family="unknown", structured_output=False))

async def _run(q):
    params = StdioServerParams(command=sys.executable, args=[os.path.join(HERE, "mcp_server.py")], read_timeout_seconds=60)
    async with McpWorkbench(params) as wb:
        tools = [t["name"] for t in await wb.list_tools()]
        agent = AssistantAgent("data_agent", model_client=client(), workbench=wb, system_message=SYS, max_tool_iterations=4, reflect_on_tool_use=True)
        res = await agent.run(task=q)
    trace = [{"mcp_tools_offered": tools}]
    for m in res.messages:
        trace.append({"type": type(m).__name__, "source": m.source, "content": str(m.content)[:500]})
    calls = [str(m.content) for m in res.messages if type(m).__name__ == "ToolCallRequestEvent"]
    return {"final_answer": str(res.messages[-1].content), "tool_calls": calls}, trace

def run(q): return asyncio.run(_run(q))
