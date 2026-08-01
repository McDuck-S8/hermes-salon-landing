#!/usr/bin/env python3
"""
Provider connectivity test — run to check all configured LLM providers.
Usage: python test_providers.py
"""
import os, json, sys
import httpx
from pathlib import Path

HERMES_HOME = Path(__file__).resolve().parent.parent

def _load_env():
    env_path = HERMES_HOME / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

_load_env()

PROVIDERS = [
    ("cerebras",   "https://api.cerebras.ai/v1",          "gemma-4-31b",                  "CEREBRAS_API_KEY"),
    ("deepseek",   "https://api.deepseek.com/v1",         "deepseek-chat",                "DEEPSEEK_API_KEY"),
    ("groq",       "https://api.groq.com/openai/v1",      "llama-3.3-70b-versatile",      "GROQ_API_KEY"),
    ("openrouter", "https://openrouter.ai/api/v1",        "openai/gpt-4o-mini",           "OPENROUTER_API_KEY"),
]

def test(name, base_url, model, env_key):
    key = os.environ.get(env_key, "")
    if not key:
        return {"status": "skipped", "error": "no API key"}
    try:
        client = httpx.Client(verify=False, proxy=None, timeout=30)
        r = client.post(f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [{"role": "user", "content": "Say OK"}], "max_tokens": 10})
        if r.status_code == 200:
            c = r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"status": "ok", "response": c.strip()[:60]}
        return {"status": "error", "error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"status": "error", "error": str(e)[:100]}

if __name__ == "__main__":
    for name, url, model, key in PROVIDERS:
        r = test(name, url, model, key)
        print(f"  [{name}] {model}: {r['status']} -> {r.get('response') or r.get('error', '')}")
