# Main Runtime Fallback for Auxiliary Tasks

## Problem
Auxiliary providers (openrouter, nous) often fail: payment errors (402), missing auth, rate limits. Session title generation, compression, and other auxiliary tasks silently fail, accumulating NULL titles.

## Solution
Pass `main_runtime` dict to auxiliary functions to use the main provider instead of auxiliary backends.

## Pattern

```python
import os
from agent.title_generator import generate_title
from agent.auxiliary_client import call_llm

MAIN_RUNTIME = {
    "model": os.environ.get("CUSTOM_MODEL", "mimo-v2.5-pro"),
    "provider": "custom",
    "base_url": os.environ["CUSTOM_BASE_URL"],
    "api_key": os.environ["CUSTOM_API_KEY"],
    "api_mode": "chat_completions",
}

# Title generation with main provider
title = generate_title(
    user_message=user_msg,
    assistant_response=asst_msg,
    timeout=20,
    main_runtime=MAIN_RUNTIME,
)

# Direct call_llm with main provider
response = call_llm(
    task="title_generation",
    messages=messages,
    max_tokens=500,
    temperature=0.3,
    timeout=timeout,
    main_runtime=MAIN_RUNTIME,
)
```

## How it works
`call_llm()` passes `main_runtime` to `_get_cached_client()` which uses it to create a client with the main provider's credentials instead of resolving from auxiliary task config. This bypasses the auxiliary provider chain entirely.

## When to use
- Auxiliary providers returning 402 (payment error)
- "No Nous authentication found" errors
- Any auxiliary task failing while main chat works fine
- Backfill scripts (fix_titles.py, etc.) that need to process many items

## CRITICAL GOTCHA: `_normalize_main_runtime` strips non-string fields

`_normalize_main_runtime()` in `agent/auxiliary_client.py` only passes through fields listed in `_MAIN_RUNTIME_FIELDS`:
```python
_MAIN_RUNTIME_FIELDS = ("provider", "model", "base_url", "api_key", "api_mode", "auth_mode")
```

This means `http_client` (httpx.Client), `default_headers` (dict), and any other non-string fields are **silently dropped**. If your main provider requires a custom httpx client (e.g. for proxy or custom headers), `main_runtime` alone won't work.

### Workaround: Direct httpx bypass
When `main_runtime` can't carry your httpx config, call the API directly:

```python
import httpx

proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
client = httpx.Client(proxy=proxy, timeout=30)

r = client.post(
    f"{API_BASE}/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept-Encoding": "identity",  # REQUIRED with HTTP proxy — breaks gzip
    },
    json={"model": MODEL, "messages": messages, "max_tokens": 100, "temperature": 0.3},
)
data = r.json()
title = data["choices"][0]["message"]["content"]
```

### Why `Accept-Encoding: identity` is required
v2rayN HTTP proxy corrupts gzip-compressed responses. httpx sends `Accept-Encoding: gzip` by default. The proxy passes through the compressed bytes but with incorrect headers, causing `zlib.error: Error -3 while decompressing data: incorrect header check`.

## Gotcha
The main provider may have rate limits. Add `time.sleep(0.3)` between calls in batch scripts.
