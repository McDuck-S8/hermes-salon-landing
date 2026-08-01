#!/usr/bin/env python3
"""
Provider connectivity test — tests ALL available LLM providers.
Includes local FreeDeepseekAPI on localhost:9655.
"""

import os
import json
import sys
import httpx
from pathlib import Path

HERMES_HOME = Path(__file__).resolve().parent.parent

# Load .env
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
    {"name": "cerebras",       "url": "https://api.cerebras.ai/v1/chat/completions",         "model": "gemma-4-31b",                 "key_env": "CEREBRAS_API_KEY"},
    {"name": "deepseek-local",  "url": "http://localhost:9655/v1/chat/completions",           "model": "deepseek-chat",               "key_env": ""},
    {"name": "deepseek",        "url": "https://api.deepseek.com/v1/chat/completions",        "model": "deepseek-chat",               "key_env": "DEEPSEEK_API_KEY"},
    {"name": "groq",            "url": "https://api.groq.com/openai/v1/chat/completions",     "model": "llama-3.3-70b-versatile",     "key_env": "GROQ_API_KEY"},
    {"name": "openrouter",      "url": "https://openrouter.ai/api/v1/chat/completions",       "model": "openai/gpt-4o-mini",          "key_env": "OPENROUTER_API_KEY"},
    {"name": "opengateway",     "url": "https://api.opengateway.ai/v1/chat/completions",      "model": "meta-llama/llama-3.3-70b-instruct", "key_env": "OPENGATEWAY_API_KEY"},
]


def test_provider(p: dict) -> dict:
    api_key = os.environ.get(p["key_env"], "") if p["key_env"] else ""
    if p["key_env"] and not api_key:
        return {"status": "skipped", "error": "no API key", "model": p["model"]}

    payload = {
        "model": p["model"],
        "messages": [{"role": "user", "content": "Say OK"}],
        "max_tokens": 10,
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        client = httpx.Client(verify=False, proxy=None, timeout=20)
        r = client.post(p["url"], headers=headers, json=payload)

        if r.status_code == 200:
            data = r.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            reasoning = data.get("choices", [{}])[0].get("message", {}).get("reasoning_content", "")
            resp = (content or reasoning or "").strip()
            return {"status": "ok", "response": resp[:60], "model": p["model"]}
        else:
            err = r.json().get("error", {}).get("message", r.text[:100])
            return {"status": "error", "error": f"HTTP {r.status_code}: {err}", "model": p["model"]}

    except httpx.ConnectError:
        return {"status": "error", "error": "Connection refused (server not running)", "model": p["model"]}
    except Exception as e:
        return {"status": "error", "error": f"{type(e).__name__}: {str(e)[:80]}", "model": p["model"]}


def main():
    print("=" * 60)
    print("HERMES LLM PROVIDER CONNECTIVITY TEST")
    print("=" * 60)

    results = {}
    for p in PROVIDERS:
        print(f"\n  [{p['name']}] {p['model']}...", end=" ", flush=True)
        result = test_provider(p)
        results[p["name"]] = result

        if result["status"] == "ok":
            print(f"OK -> \"{result.get('response', '')}\"")
        elif status == "skipped":
            print(f"SKIPPED -> {result.get('error', '')}")
        else:
            print(f"FAIL -> {result.get('error', '')}")

    # Summary
    ok = sum(1 for r in results.values() if r["status"] == "ok")
    err = sum(1 for r in results.values() if r["status"] == "error")
    skip = sum(1 for r in results.values() if r["status"] == "skipped")

    print(f"\n{'=' * 60}")
    print(f"RESULT: {ok} OK / {err} FAIL / {skip} SKIPPED (of {len(PROVIDERS)} providers)")
    print("=" * 60)

    output = {"success": ok > 0, "results": results, "summary": {"ok": ok, "error": err, "skipped": skip}}
    print(f"\n{json.dumps(output, indent=2, ensure_ascii=False)}")
    return output


if __name__ == "__main__":
    main()
