#!/usr/bin/env python3
"""
OpenCode Zen API Client — прямой вызов LLM через opencode.ai/zen.
"""

# Revisit: when openrouter client logic, API integration, or fallback providers change. Last touched: 2026-07-02.
import os
import requests
import time
import random
from typing import Optional

API_URL = "https://opencode.ai/zen/v1/chat/completions"

FREE_MODELS = [
    "mimo-v2.5-free",
    "deepseek-v4-flash-free",
    "nemotron-3-ultra-free",
    "qwen3.6-plus-free",
    "minimax-m3-free",
    "nemotron-3-super-free",
]


def call_llm(prompt: str, model: str = "mimo-v2.5-free", max_tokens: int = 2000, temperature: float = 0.3) -> Optional[str]:
    """Call opencode.ai/zen API directly."""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    for attempt in range(3):
        try:
            r = requests.post(API_URL, json=payload, timeout=60)
            if r.status_code == 200:
                data = r.json()
                msg = data.get("choices", [{}])[0].get("message", {})
                # content может быть null если модель использует reasoning
                content = msg.get("content") or msg.get("reasoning") or ""
                return content.strip() if content else None
            elif r.status_code == 429:
                time.sleep(2 + random.random() * 3)
                continue
            else:
                print(f"[OpenCode Zen] Error {r.status_code}: {r.text[:200]}")
                return None
        except Exception as e:
            print(f"[OpenCode Zen] Request error: {e}")
            return None
    
    print("[OpenCode Zen] All retries exhausted")
    return None


if __name__ == "__main__":
    result = call_llm("Say OK", max_tokens=50)
    print(f"Result: {result}")
