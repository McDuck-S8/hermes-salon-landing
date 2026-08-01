# opencode-zen HTTP API Reference

## Working Endpoint (No Auth Required for Free Models)

**Base URL:** `https://opencode.ai/zen/v1/chat/completions`
**Method:** POST
**Content-Type:** application/json

## Request Format

```json
{
    "model": "mimo-v2.5-free",
    "messages": [{"role": "user", "content": "Your prompt here"}],
    "max_tokens": 2000,
    "temperature": 0.3
}
```

## Response Format

**Standard response:**
```json
{
    "choices": [{
        "message": {
            "content": "Response text here",
            "reasoning": null
        }
    }]
}
```

**Quirk (some models):** `content: null`, reasoning in separate field:
```json
{
    "choices": [{
        "message": {
            "content": null,
            "reasoning": "Model's thinking process..."
        }
    }]
}
```

**Always use:**
```python
content = msg.get("content") or msg.get("reasoning") or ""
```

## Free Models

| Model | Priority | Speed | Notes |
|-------|----------|-------|-------|
| nemotron-3-ultra-free | 1 | Slow | Best reasoning |
| deepseek-v4-flash-free | 2 | Fast | Good for coding |
| mimo-v2.5-free | 3 | Fast | Quick responses |
| qwen3.6-plus-free | 4 | Medium | Complex reasoning |
| minimax-m3-free | 5 | Medium | Alternative |

## Rate Limiting

- 3-5 seconds between consecutive requests
- HTTP 401/429 if too fast
- Auto-rotate models on failure

## Working Implementation (Python)

```python
import requests
import time
import random

API_URL = "https://opencode.ai/zen/v1/chat/completions"
FREE_MODELS = ["nemotron-3-ultra-free", "deepseek-v4-flash-free", "mimo-v2.5-free", "qwen3.6-plus-free"]

def call_llm(prompt, model=None, max_tokens=2000):
    """Call opencode-zen with auto-rotation."""
    models = [model] if model else FREE_MODELS
    
    for m in models:
        try:
            r = requests.post(API_URL, json={
                "model": m,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.3
            }, timeout=60)
            
            if r.status_code == 200:
                msg = r.json()["choices"][0]["message"]
                return msg.get("content") or msg.get("reasoning") or ""
            elif r.status_code in (401, 429):
                time.sleep(random.uniform(3, 5))
                continue
        except Exception:
            continue
    
    return None
```

## What NOT to Do

1. **Do NOT use OpenRouter** — user explicitly forbids it (no credits)
2. **Do NOT use subprocess to call opencode CLI** — hangs on Windows due to TTY detection
3. **Do NOT use litellm** — direct HTTP requests work fine
4. **Do NOT send requests faster than 3s apart** — triggers rate limiting

## Historical Note

Earlier sessions tried dialagram.me backend and OpenRouter. Both were incorrect:
- dialagram.me was the old backend (now HTTP API works directly)
- OpenRouter has 0 credits and is user-forbidden
- The correct approach is direct HTTP to opencode.ai/zen/v1/chat/completions
