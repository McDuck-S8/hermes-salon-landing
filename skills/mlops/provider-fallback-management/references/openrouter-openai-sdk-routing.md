# OpenRouter + openai Python SDK — Provider Routing Issue

## Problem

When using the `openai` Python SDK (v1.x) to call OpenRouter, all requests fail with:

```
404: No allowed providers are available for the selected model.
available_providers: ['streamlake', 'deepinfra', 'novita']
requested_providers: ['groq', 'mistral', 'stepfun', 'deepseek', 'perplexity', 'google-ai-studio']
```

## Root Cause

The `openai` Python SDK sends `x-stainless-*` HTTP headers (arch, lang, os, package-version, runtime, runtime-version) with every request. OpenRouter reads these headers to determine which **provider routing group** the client belongs to.

Each OpenRouter API key is configured with allowed provider groups. If the SDK's stainless headers advertise a group that doesn't include any provider hosting the requested model, OpenRouter returns 404.

**The `requested_providers` list = providers your client (via SDK headers) will accept.**
**The `available_providers` list = providers that have the model AND are available for your key.**

When these sets don't intersect → 404.

## Models and Their Available Providers (access-dependent)

| Model | Available Providers (typical) |
|-------|------------------------------|
| deepseek/deepseek-chat | streamlake, deepinfra, novita |
| mistralai/mistral-small-3.1-24b-instruct | cloudflare |
| gpt-4o-mini | azure, openai |
| nousresearch/hermes-3-llama-3.1-405b:free | venice |

## Solutions

### Option 1: Use model available through your key's provider group

Check what providers your key has access to (from the 404 error metadata). Pick a model hosted by one of those providers.

### Option 2: Direct API (recommended when OpenRouter blocks)

Bypass OpenRouter entirely — use the model provider's direct API:

```bash
# Mistral (has OpenAI-compatible endpoint, supports function calling)
EVEROS_LLM__MODEL=mistral-small-latest
EVEROS_LLM__API_KEY=<mistral_key>
EVEROS_LLM__BASE_URL=https://api.mistral.ai/v1

# DeepSeek (may require payment)
EVEROS_LLM__MODEL=deepseek-chat
EVEROS_LLM__API_KEY=<deepseek_key>
EVEROS_LLM__BASE_URL=https://api.deepseek.com

# Groq
EVEROS_LLM__MODEL=llama-3.3-70b-versatile
EVEROS_LLM__API_KEY=<groq_key>
EVEROS_LLM__BASE_URL=https://api.groq.com/openai/v1
```

**Tested working with everalgo (EverOS memorize pipeline):** Mistral API (`mistral-small-latest` via `api.mistral.ai/v1`). Passes the boundary detection LLM call (function calling) and accumulates messages successfully. DeepSeek direct returns 402 Payment Required. Groq returns 403 Forbidden with the available key.

Mistral API supports function calling — works with EverOS / everalgo. Confirmed: ADD returns `{"status":"accumulated"}`, FLUSH returns `{"status":"no_extraction"}`, /health and /metrics respond.

## Diagnostic

To quickly test if a provider works:

```python
import json, urllib.request

req = urllib.request.Request(
    'https://api.mistral.ai/v1/chat/completions',
    data=json.dumps({
        'model': 'mistral-small-latest',
        'messages': [{'role': 'user', 'content': 'hi'}],
    }).encode(),
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {key}',
    },
)
resp = urllib.request.urlopen(req, timeout=30)
```

## Pitfalls

- **Not just OpenRouter**: The `x-stainless-*` headers are sent by ALL v1.x openai SDK clients. Any OpenAI-compatible proxy that routes based on these headers (some self-hosted proxies too) may exhibit the same issue.
- **Not an auth problem**: The API key itself is valid — the issue is provider routing, not authentication.
- **`urllib.request` also hits the issue**: Even without stainless headers, OpenRouter still applies provider routing based on key configuration.
