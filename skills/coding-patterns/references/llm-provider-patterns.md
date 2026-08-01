# LLM Provider Integration Reference

## Provider Availability (Windows, 2026-07-09)

Tested from `D:\Portable_Soft\hermes` on Windows 11:

| Provider | Model | Status | Notes |
|----------|-------|--------|-------|
| Cerebras | gemma-4-31b | ✅ OK | Primary. ~400ms. Rate limits at 429. |
| DeepSeek Local | deepseek-chat | ✅ OK | localhost:9655 via FreeDeepseekAPI. ~5s. |
| DeepSeek Cloud | deepseek-chat | ❌ 402 | "Insufficient Balance" — key valid, no funds. |
| Groq | llama-3.3-70b | ❌ 403 | "Access denied" — regional/network block. |
| OpenRouter | gpt-4o-mini | ❌ 404 | "No allowed providers" from this network. |
| OpenGateway | llama-3.3-70b | ❌ SSL | Connection refused / SSL timeout. |

## Fallback Chain Pattern

```python
PROVIDERS = [
    {"name": "cerebras", "model": "gemma-4-31b", "base_url": "https://api.cerebras.ai/v1", "env_key": "CEREBRAS_API_KEY"},
    {"name": "deepseek-local", "model": "deepseek-chat", "base_url": "http://localhost:9655/v1", "env_key": "_LOCAL_DEEPSEEK"},
    {"name": "deepseek", "model": "deepseek-chat", "base_url": "https://api.deepseek.com/v1", "env_key": "DEEPSEEK_API_KEY"},
    # ... more providers
]

def _resolve_providers(preferred=None):
    """Return providers with valid keys. Local servers always available."""
    available = []
    for p in PROVIDERS:
        if p["env_key"] == "_LOCAL_DEEPSEEK":
            available.append(p)  # Local server — always available
        else:
            key = os.environ.get(p["env_key"], "")
            if key and len(key) > 8:
                available.append(p)
    if preferred:
        # Move preferred to front
        for i, p in enumerate(available):
            if p["name"] == preferred:
                available.insert(0, available.pop(i))
                break
    return available
```

## httpx Transport (Windows SSL Fix)

All LLM calls use httpx with SSL disabled:

```python
_httpx_client = None
def _get_httpx():
    global _httpx_client
    if _httpx_client is None:
        import httpx
        _httpx_client = httpx.Client(verify=False, proxy=None, timeout=60)
    return _httpx_client
```

**Why**: Windows Python SSL fails on external HTTPS. `verify=False` + `proxy=None` bypasses both system proxy and certificate validation.

**litellm note**: litellm's default aiohttp transport does NOT respect httpx settings. Use direct httpx calls for reliability.

## Structured Output with instructor

```python
import instructor
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI(api_key=api_key, base_url=base_url, timeout=60)
client = instructor.from_openai(client)

class Result(BaseModel):
    answer: str
    confidence: float

result = client.chat.completions.create(
    model=model,
    response_model=Result,
    messages=[{"role": "user", "content": prompt}],
    max_retries=3,
)
```

## FreeDeepseekAPI Local Server

Location: `D:/Portable_Soft/FreeDeepseekAPI/server.js`

Start:
```bash
cd /d/Portable_Soft/FreeDeepseekAPI && node server.js
# In menu, select option 3 (start proxy)
# Or use pty mode for interactive menu
```

Auth tokens: `D:/Portable_Soft/FreeDeepseekAPI/deepseek-auth.json`

Endpoint: `http://localhost:9655/v1/chat/completions` (OpenAI-compatible)

**Pitfall**: Server needs `isTTY` for interactive menu. Use `pty=true` in terminal tool, or set `NON_INTERACTIVE=1` env var.
