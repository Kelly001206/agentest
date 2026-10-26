"""A11 - Evaluator-optimizer with a guardrail agent, OpenAI Agents SDK.
1) input_guardrail: a small guard agent labels the request SAFE/UNSAFE; UNSAFE trips the wire and nothing is generated.
2) generator agent drafts a customer reply; 3) critic agent returns PASS or REVISE:<feedback>; loop max 3 rounds.
A deterministic policy check (no promises of returns, no PII echo) also runs on every draft."""
import os, sys, asyncio, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config import LLM_BASE, LLM_MODEL, LLM_KEY
from openai import AsyncOpenAI
from agents import (Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled, ModelSettings,
                    input_guardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered)

set_tracing_disabled(True)
model = OpenAIChatCompletionsModel(model=LLM_MODEL, openai_client=AsyncOpenAI(base_url=LLM_BASE, api_key=LLM_KEY))
MS = ModelSettings(temperature=0)
guard = Agent(name="Guard", model=model, model_settings=MS, instructions=(
    "Label the user's request. Reply with exactly one word: UNSAFE if it asks for another person's private data, "
    "help with fraud, evading KYC, or harming someone; otherwise SAFE."))

@input_guardrail
async def safety_guardrail(ctx, agent, inp):
    r = await Runner.run(guard, inp, context=ctx.context)
    label = (r.final_output or "").strip().upper()
    return GuardrailFunctionOutput(output_info={"guard_label": label}, tripwire_triggered=label.startswith("UNSAFE"))

generator = Agent(name="Generator", model=model, model_settings=MS, input_guardrails=[safety_guardrail], instructions=(
    "You are a bank's customer-reply writer. Write a polite reply under 90 words. Never promise returns or guarantees. "
    "Never repeat account or card numbers. If feedback is given, revise accordingly."))
critic = Agent(name="Critic", model=model, model_settings=MS, instructions=(
    "You review a draft customer reply. If it is polite, under 90 words, makes no guarantees and contains no account/card numbers, "
    "reply exactly 'PASS'. Otherwise reply 'REVISE: ' followed by one sentence of feedback."))
POLICY = [(r"guarantee|assured returns|risk[- ]free", "no guarantees"), (r"\b\d{9,18}\b", "no account/card numbers")]

def policy_issues(t): return [why for rx, why in POLICY if re.search(rx, t, re.I)]

async def _run(request, max_rounds=3):
    trace, feedback, draft = [], "", None
    for rnd in range(1, max_rounds + 1):
        prompt = request if not feedback else f"{request}\n\nPrevious draft:\n{draft}\n\nFeedback: {feedback}"
        try:
            g = await Runner.run(generator, prompt)
        except InputGuardrailTripwireTriggered as e:
            info = e.guardrail_result.output.output_info
            trace.append({"round": rnd, "guardrail": "TRIPPED", **info})
            return {"blocked_by_guardrail": True, "final_reply": "Sorry, I can't help with that request.", "rounds": rnd}, trace
        draft = g.final_output
        c = (await Runner.run(critic, f"Draft reply:\n{draft}")).final_output.strip()
        pol = policy_issues(draft)
        trace.append({"round": rnd, "draft": draft, "critic": c, "policy_issues": pol})
        if c.upper().startswith("PASS") and not pol:
            return {"blocked_by_guardrail": False, "final_reply": draft, "rounds": rnd, "accepted": True}, trace
        feedback = (c.split(":", 1)[-1].strip() if ":" in c else c) + ("; also: " + ", ".join(pol) if pol else "")
    return {"blocked_by_guardrail": False, "final_reply": draft, "rounds": max_rounds, "accepted": False, "note": "max rounds reached"}, trace

def run(request): return asyncio.run(_run(request))
