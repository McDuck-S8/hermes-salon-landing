# opencode.ai/zen HTTP API Reference

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `https://opencode.ai/zen/v1/chat/completions` | POST | Chat completions (OpenAI-compatible) |
| `https://opencode.ai/zen/v1/models` | GET | List available models |
| `https://opencode.ai/zen/v1/messages` | POST | Messages API (alternative) |

## Auth
- Free models: no auth required
- Paid models: check .env for OPENCODE_ZEN_API_KEY

## Free Models (2026-06)
All end with `-free` or `:free`:
- `mimo-v2.5-free` — reasoning model (content=null quirk)
- `deepseek-v4-flash-free`
- `nemotron-3-ultra-free`
- `qwen3.6-plus-free`
- `minimax-m3-free`
- `nemotron-3-super-free`
- `gemma-3-1b-it:free`
- `gemma-3-4b-it:free`
- `gemma-3-12b-it:free`
- `gemma-3-27b-it:free`

## Paid Models
- `qwen3.6-plus`, `qwen3.5-plus`
- `deepseek-v4-flash`
- `kimi-k2.6`
- `qwen3-coder-plus`

## Response Format
OpenAI-compatible:
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "...",        // may be null for reasoning models
      "reasoning": "..."       // actual response when content=null
    }
  }]
}
```

## Known Quirks

### content=null (mimo-v2.5-free)
Reasoning models return `"content": null` with actual output in `"reasoning"`.
Always check both fields:
```python
answer = msg.get("content") or msg.get("reasoning") or ""
```

### Rate Limits
429 responses possible. Use retry with backoff (3 attempts, 2-5s delay).

### Timeout
Default 30-60s per request. For long prompts, set timeout=120.

## Quick Test
```bash
curl -X POST https://opencode.ai/zen/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash-free","messages":[{"role":"user","content":"Say OK"}],"max_tokens":50}'
```
