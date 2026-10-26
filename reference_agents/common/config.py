import os
LLM_BASE = os.environ.get("REF_LLM_BASE", "http://127.0.0.1:8008/v1")
LLM_MODEL = os.environ.get("REF_MODEL", "Qwen/Qwen2.5-7B-Instruct-GGUF:Q4_K_M")
LLM_KEY = "not-needed-local"

def openai_client():
    from openai import OpenAI
    return OpenAI(base_url=LLM_BASE, api_key=LLM_KEY)
