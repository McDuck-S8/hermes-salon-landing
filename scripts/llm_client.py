#!/usr/bin/env python3
"""
Unified LLM Client for Hermes — Cerebras primary, multi-provider fallback.

Transport: httpx with SSL verify=False (workaround for Windows SSL issues).
Providers: Cerebras (primary) → DeepSeek → Groq → OpenRouter.

Usage:
    from scripts.llm_client import call_llm, call_structured, call_json

    # Simple text call (auto-fallback)
    response = call_llm("Say hello")

    # Structured output (guaranteed Pydantic model)
    from pydantic import BaseModel
    class Answer(BaseModel):
        score: float
        reason: str
    result = call_structured("Rate this 1-10", Answer)

    # JSON call
    result = call_json('{"key": "value"}')
"""

import os
import json
import time
import re
import random
from typing import Optional, Type, TypeVar
from pathlib import Path

T = TypeVar("T")

# Tracing (lazy import to avoid circular)
_tracer = None

def _get_tracer():
    global _tracer
    if _tracer is None:
        try:
            from scripts.llm_tracer import trace_llm as _trace_llm, flush as _flush
            _tracer = {"trace_llm": _trace_llm, "flush": _flush}
        except Exception:
            _tracer = False
    return _tracer if _tracer else None


def _truncate(text: str, max_len: int = 200) -> str:
    """Truncate text for logging."""
    if not text:
        return ""
    return text[:max_len] + "..." if len(text) > max_len else text


def _count_tokens_approx(text: str) -> int:
    """Approximate token count (words * 1.3)."""
    return int(len(text.split()) * 1.3) if text else 0

# ---------------------------------------------------------------------------
# Bootstrap: load .env
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Provider registry: (name, model, base_url, env_key)
# ---------------------------------------------------------------------------

PROVIDERS = [
    {
        "name": "cerebras",
        "model": "gemma-4-31b",
        "base_url": "https://api.cerebras.ai/v1",
        "env_key": "CEREBRAS_API_KEY",
    },
    {
        "name": "deepseek-local",
        "model": "deepseek-chat",
        "base_url": "http://localhost:9655/v1",
        "env_key": "_LOCAL_DEEPSEEK",
    },
    {
        "name": "deepseek",
        "model": "deepseek-chat",
        "base_url": "https://api.deepseek.com/v1",
        "env_key": "DEEPSEEK_API_KEY",
    },
    {
        "name": "groq",
        "model": "llama-3.3-70b-versatile",
        "base_url": "https://api.groq.com/openai/v1",
        "env_key": "GROQ_API_KEY",
    },
    {
        "name": "openrouter",
        "model": "openai/gpt-4o-mini",
        "base_url": "https://openrouter.ai/api/v1",
        "env_key": "OPENROUTER_API_KEY",
    },
]


def _resolve_providers(preferred: Optional[str] = None) -> list:
    """Return providers with valid keys. If preferred name given, put it first."""
    available = []
    for p in PROVIDERS:
        if p["env_key"] == "_LOCAL_DEEPSEEK":
            # Local server — always available if running
            available.append(p)
        else:
            key = os.environ.get(p["env_key"], "")
            if key and len(key) > 8:
                available.append(p)

    if preferred:
        for i, p in enumerate(available):
            if p["name"] == preferred:
                available.insert(0, available.pop(i))
                break

    return available


# ---------------------------------------------------------------------------
# Transport: httpx with SSL verify=False (Windows workaround)
# ---------------------------------------------------------------------------

_httpx_client = None


def _get_httpx():
    global _httpx_client
    if _httpx_client is None:
        import httpx
        _httpx_client = httpx.Client(verify=False, proxy=None, timeout=60)
    return _httpx_client


def _raw_completion(provider: dict, messages: list, max_tokens: int = 2000,
                    temperature: float = 0.3, api_key: str = "") -> Optional[str]:
    """Single HTTP call to an OpenAI-compatible endpoint."""
    client = _get_httpx()
    payload = {
        "model": provider["model"],
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        r = client.post(
            f"{provider['base_url']}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )
        if r.status_code == 200:
            data = r.json()
            choices = data.get("choices", [])
            if choices:
                content = choices[0].get("message", {}).get("content")
                reasoning = choices[0].get("message", {}).get("reasoning_content")
                return (content or reasoning or "").strip()
        else:
            err = r.json().get("error", {}).get("message", "")[:120]
            print(f"[LLM] {provider['name']}/{provider['model']} -> {r.status_code}: {err}")
    except Exception as e:
        print(f"[LLM] {provider['name']}/{provider['model']} -> {type(e).__name__}: {str(e)[:80]}")

    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def call_llm(
    prompt: str,
    model: Optional[str] = None,
    system: Optional[str] = None,
    max_tokens: int = 2000,
    temperature: float = 0.3,
    timeout: int = 60,
    retries: int = 2,
    fallback: bool = True,
    provider: Optional[str] = None,
) -> Optional[str]:
    """
    Call LLM with automatic fallback across providers.
    Returns text response or None on failure.
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    # Determine provider chain
    if provider:
        chain = _resolve_providers(preferred=provider)
    elif model:
        # Find provider that matches this model
        chain = [p for p in PROVIDERS if p["model"] == model] or _resolve_providers()
    else:
        chain = _resolve_providers()

    if not chain:
        print("[LLM] No providers with valid API keys")
        return None

    if not fallback:
        chain = chain[:1]

    for p in chain:
        api_key = os.environ.get(p["env_key"], "") if p["env_key"] != "_LOCAL_DEEPSEEK" else ""
        if p["env_key"] != "_LOCAL_DEEPSEEK" and not api_key:
            continue

        tracer = _get_tracer()
        if tracer:
            with tracer["trace_llm"](p["name"], p["model"], "call_llm") as ctx:
                ctx["data"]["prompt_preview"] = _truncate(prompt, 200)
                for attempt in range(retries):
                    result = _raw_completion(p, messages, max_tokens, temperature, api_key)
                    if result:
                        ctx["data"]["response_preview"] = _truncate(result, 200)
                        ctx["data"]["tokens_out"] = _count_tokens_approx(result)
                        ctx["data"]["tokens_in"] = _count_tokens_approx(prompt)
                        return result
                    if attempt < retries - 1:
                        time.sleep(1 + random.random())
        else:
            for attempt in range(retries):
                result = _raw_completion(p, messages, max_tokens, temperature, api_key)
                if result:
                    return result
                if attempt < retries - 1:
                    time.sleep(1 + random.random())

    return None


def call_structured(
    prompt: str,
    response_model: Type[T],
    model: Optional[str] = None,
    system: Optional[str] = None,
    max_retries: int = 3,
    temperature: float = 0.3,
    provider: Optional[str] = None,
) -> Optional[T]:
    """
    Call LLM and return a validated Pydantic model.
    Uses instructor to patch OpenAI client.
    """
    import instructor
    from openai import OpenAI

    # Resolve provider
    if provider:
        chain = _resolve_providers(preferred=provider)
    elif model:
        chain = [p for p in PROVIDERS if p["model"] == model] or _resolve_providers()
    else:
        chain = _resolve_providers()

    if not chain:
        print("[LLM] No providers available for structured call")
        return None

    p = chain[0]
    api_key = os.environ.get(p["env_key"], "")

    client = OpenAI(api_key=api_key, base_url=p["base_url"], timeout=60)
    client = instructor.from_openai(client)

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        return client.chat.completions.create(
            model=p["model"],
            response_model=response_model,
            messages=messages,
            max_retries=max_retries,
            temperature=temperature,
        )
    except Exception as e:
        print(f"[LLM] Structured call failed ({p['name']}): {e}")
        return None


def call_json(
    prompt: str,
    model: Optional[str] = None,
    system: Optional[str] = "You must respond with valid JSON only. No markdown, no explanation.",
    max_tokens: int = 2000,
    temperature: float = 0.2,
    provider: Optional[str] = None,
) -> Optional[dict]:
    """Call LLM and parse response as JSON dict."""
    response = call_llm(prompt, model=model, system=system,
                        max_tokens=max_tokens, temperature=temperature, provider=provider)
    if not response:
        return None

    text = response.strip()
    # Strip markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
        if text.endswith("```"):
            text = text[:-3]

    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return None


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def health_check() -> dict:
    """Check all configured providers."""
    results = {}
    chain = _resolve_providers()
    for p in chain:
        if p["env_key"] == "_LOCAL_DEEPSEEK":
            api_key = ""
        else:
            api_key = os.environ.get(p["env_key"], "")
            if not api_key:
                continue

        name = f"{p['name']}/{p['model']}"
        try:
            resp = _raw_completion(p, [{"role": "user", "content": "Reply OK"}],
                                   max_tokens=10, temperature=0, api_key=api_key)
            results[name] = {"status": "ok" if resp else "empty", "response": (resp or "")[:50]}
        except Exception as e:
            results[name] = {"status": "error", "error": str(e)[:100]}
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--health":
        print(json.dumps(health_check(), indent=2))

    elif len(sys.argv) > 1 and sys.argv[1] == "--test":
        chain = _resolve_providers()
        print(f"Available providers: {len(chain)}")
        for p in chain:
            print(f"  {p['name']}/{p['model']}")

        print("\n--- call_llm ---")
        r = call_llm("Say hello in one word", max_tokens=20)
        print(f"  Result: {r}")

        print("\n--- call_structured ---")
        from pydantic import BaseModel

        class Greeting(BaseModel):
            word: str
            language: str

        r2 = call_structured("Say hello", Greeting, max_retries=2)
        if r2:
            print(f"  Result: word={r2.word}, language={r2.language}")
        else:
            print("  Failed")

        print("\n--- call_json ---")
        r3 = call_json('{"status": "ok", "code": 200}')
        print(f"  Result: {r3}")

    else:
        print("Usage:")
        print("  python llm_client.py --health")
        print("  python llm_client.py --test")
