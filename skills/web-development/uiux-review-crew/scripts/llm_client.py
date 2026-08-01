"""LLM Client - uses existing Hermes stack (OpenRouter/Groq/DeepSeek)."""
import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

# Provider configs - OpenRouter first (most reliable), then Groq, then DeepSeek
PROVIDERS = {
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": os.getenv("OPENROUTER_API_KEY"),
        "default_model": "anthropic/claude-3.5-sonnet",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": os.getenv("GROQ_API_KEY"),
        "default_model": "llama-3.1-70b-versatile",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "api_key": os.getenv("DEEPSEEK_API_KEY"),
        "default_model": "deepseek-chat",
    },
    "cerebras": {
        "base_url": "https://api.cerebras.ai/v1",
        "api_key": os.getenv("CEREBRAS_API_KEY"),
        "default_model": "llama3.1-70b",
    },
}

# Pick provider - PREFER GROQ > OPENROUTER > DEEPSEEK (skip cerebras - Cloudflare blocks)
ACTIVE_PROVIDER = None
for name in ["groq", "openrouter", "deepseek"]:
    if name in PROVIDERS and PROVIDERS[name]["api_key"]:
        ACTIVE_PROVIDER = name
        print(f"[llm_client] Selected provider: {ACTIVE_PROVIDER}")
        break

if not ACTIVE_PROVIDER:
    raise RuntimeError("No LLM provider configured. Set GROQ_API_KEY, OPENROUTER_API_KEY, or DEEPSEEK_API_KEY")

PROVIDER_CFG = PROVIDERS[ACTIVE_PROVIDER]
BASE_URL = PROVIDER_CFG["base_url"]
API_KEY = PROVIDER_CFG["api_key"]
DEFAULT_MODEL = PROVIDER_CFG["default_model"]

# Override via env
MODEL = os.getenv("UIUX_REVIEW_MODEL", DEFAULT_MODEL)

async def call_llm(messages: List[Dict[str, str]], temperature: float = 0.2, 
                   max_tokens: int = 4000, response_format: str = "json") -> str:
    """Call LLM via OpenRouter/Groq/DeepSeek."""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/hermes-agent/uiux-review-crew",
        "X-Title": "UI/UX Review Crew",
    }
    
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    
    if response_format == "json":
        payload["response_format"] = {"type": "json_object"}
    
    async with aiohttp.ClientSession() as session:
        for attempt in range(3):
            try:
                async with session.post(
                    f"{BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["choices"][0]["message"]["content"]
                    elif resp.status == 429:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        text = await resp.text()
                        raise RuntimeError(f"LLM API error {resp.status}: {text}")
            except asyncio.TimeoutError:
                if attempt == 2:
                    raise RuntimeError("LLM request timed out after 3 attempts")
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                if attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)
    
    raise RuntimeError("LLM call failed after retries")

async def call_llm_json(messages: List[Dict[str, str]], model: str = None, 
                        temperature: float = 0.2, max_tokens: int = 4000) -> dict:
    """Call LLM and parse JSON response."""
    content = await call_llm(messages, temperature=temperature, max_tokens=max_tokens, response_format="json")
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return json.loads(content)