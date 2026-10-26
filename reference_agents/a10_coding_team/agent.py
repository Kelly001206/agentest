"""A10 - Orchestrator-workers coding agent: AutoGen AgentChat team.
planner -> coder -> executor (runs the code) -> reviewer, round-robin until the reviewer says APPROVE or 10 messages.
Code runs with LocalCommandLineCodeExecutor in a throw-away temp dir with a timeout (Docker is not available on free
CPU Spaces, so this is NOT a strong sandbox - see README). The result is a PROPOSED patch for human review; nothing is merged."""
import os, sys, asyncio, tempfile, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config import LLM_BASE, LLM_MODEL, LLM_KEY
from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_core.models import ModelInfo

DENY = re.compile(r"os\.system|subprocess|shutil|rmtree|os\.remove|unlink|socket|requests|urllib|open\([^)]*['\"]/", re.S)

class GuardedExecutor(LocalCommandLineCodeExecutor):
    """Refuses code that shells out, deletes files, uses the network, or writes to absolute paths."""
    async def execute_code_blocks(self, code_blocks, cancellation_token):
        from autogen_core.code_executor import CodeResult
        for b in code_blocks:
            m = DENY.search(b.code)
            if m:
                return CodeResult(exit_code=1, output=f"BLOCKED by executor policy: forbidden pattern {m.group(0)!r}")
        return await super().execute_code_blocks(code_blocks, cancellation_token)

def client():
    return OpenAIChatCompletionClient(model=LLM_MODEL, base_url=LLM_BASE, api_key=LLM_KEY, temperature=0,
        model_info=ModelInfo(vision=False, function_calling=True, json_output=False, family="unknown", structured_output=False))

async def _run(task):
    work = tempfile.mkdtemp(prefix="a10_")
    ex = GuardedExecutor(work_dir=work, timeout=30)
    planner = AssistantAgent("planner", model_client=client(), system_message="Break the coding task into 2-3 short steps for the coder. Do not write code.")
    coder = AssistantAgent("coder", model_client=client(), system_message=(
        "Write ONE self-contained Python script in a single ```python block: the function plus assert-based tests at the bottom "
        "and a final print('ALL TESTS PASSED'). No input(), no network, no file deletion."))
    executor = CodeExecutorAgent("executor", code_executor=ex)
    reviewer = AssistantAgent("reviewer", model_client=client(), system_message=(
        "Review the code and the executor output. If the output contains ALL TESTS PASSED and the code is safe, reply 'APPROVE'. "
        "Otherwise explain the bug briefly for the coder."))
    team = RoundRobinGroupChat([planner, coder, executor, reviewer],
                               termination_condition=TextMentionTermination("APPROVE") | MaxMessageTermination(10))
    res = await team.run(task=task)
    trace = [{"source": m.source, "type": type(m).__name__, "content": str(m.content)[:700]} for m in res.messages]
    code_blocks = [c for m in res.messages if m.source == "coder" for c in re.findall(r"```python\n(.*?)```", str(m.content), re.S)]
    exec_out = [str(m.content) for m in res.messages if m.source == "executor"]
    approved = any(m.source == "reviewer" and "APPROVE" in str(m.content) for m in res.messages)
    return {"proposed_patch": code_blocks[-1] if code_blocks else None, "last_execution_output": exec_out[-1][:600] if exec_out else None,
            "tests_passed_in_executor": bool(exec_out and "ALL TESTS PASSED" in exec_out[-1]), "reviewer_approved": approved,
            "merged": False, "merge_policy": "a human must review and merge the proposed patch", "messages": len(res.messages), "stop_reason": res.stop_reason}, trace

def run(task): return asyncio.run(_run(task))
