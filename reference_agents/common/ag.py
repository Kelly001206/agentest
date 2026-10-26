"""AutoGen AgentChat helpers shared by A16, A20, A21, A25: model client for the local server and
message-to-trace conversion."""
from __future__ import annotations
from .runtime import AgentConfig, Tracer


def ag_client(cfg: AgentConfig, max_tokens: int = 350):
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_core.models import ModelInfo
    return OpenAIChatCompletionClient(model=cfg.model, base_url=cfg.llm_base, api_key=cfg.api_key, temperature=cfg.temperature,
                                      seed=cfg.seed, max_tokens=max_tokens, timeout=cfg.timeout_s, max_retries=cfg.max_retries,
                                      model_info=ModelInfo(vision=False, function_calling=True, json_output=False, family="unknown", structured_output=False))


def trace_messages(messages, tracer: Tracer) -> list[dict]:
    out = []
    for m in messages:
        d = {"type": type(m).__name__, "source": getattr(m, "source", "?"), "content": str(getattr(m, "content", ""))[:700]}
        out.append(d); tracer.event("message", d["type"], source=d["source"], content=d["content"][:400])
    return out
