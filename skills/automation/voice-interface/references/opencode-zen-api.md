# OpenCode Zen API — Endpoint Reference

From user-provided docs (June 2026). Authoritative source for "зен провайдера".

## Base URL

```
https://opencode.ai/zen/v1
```

✅ Correct endpoint — `opencode.ai/zen/v1`
❌ Wrong — `api.opencode-zen.com/v1` (common mistake)
❌ Wrong — `opengateway.gitlawb.com/v1` (different service, credit-exhausted, permanently disabled)

## Endpoints

| Purpose | Endpoint |
|---------|----------|
| Base URL | `https://opencode.ai/zen/v1` |
| List models | `https://opencode.ai/zen/v1/models` |
| Chat completions (OpenAI-compatible) | `/chat/completions` |
| Responses API (GPT series) | `/responses` |
| Messages API (Claude series) | `/messages` |
| Gemini models | `/models/gemini-{model-id}` |

## Usage

```python
from openai import OpenAI
client = OpenAI(
    base_url="https://opencode.ai/zen/v1",
    api_key=""  # optional — works without key
)
response = client.chat.completions.create(
    model="deepseek-v4-flash-free",
    messages=[{"role": "user", "content": "Hello"}]
)
```

Model IDs are used directly (e.g., `deepseek-v4-flash-free`), NOT prefixed with `opencode/`.

## Authentication

- **API key is optional** — the endpoint works without one
- If using a key, it goes in the `Authorization: Bearer <key>` header
- Provider console: https://gitlawb.com/opengateway/dashboard

## Free Models

All available at `https://opencode.ai/zen/v1/models` — returns full list.

| Model | Supply |
|-------|--------|
| `deepseek-v4-flash-free` | Fast, reliable, produces content+reasoning |
| `mimo-v2.5-free` | Very fast, Xiaomi MiMo |
| `qwen3.6-plus-free` | Qwen |
| `minimax-m3-free` | MiniMax |
| `nemotron-3-ultra-free` | NVIDIA |
| `north-mini-code-free` | Code-focused |

## Response Shape

All free models are thinking/reasoning models. They may return the response in:
- `reasoning` (mimo, deepseek-v4)
- `reasoning_content` (deepseek-v4, qwen)
- `reasoning_details` array (mimo)
- `content` (some models, but may be empty/null)

If `content` is empty/null, read from `reasoning` → `reasoning_content` → `reasoning_details[-1].text`.

## max_tokens Consideration

Thinking models consume tokens for reasoning before producing content. With `max_tokens=200`,
the model often fills the budget with reasoning and leaves `content` empty. **Set `max_tokens=300`
or higher** for simple exchanges. With 300 tokens, models complete thinking and produce content.
