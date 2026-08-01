# Voice Bridge Setup

## What

`scripts/voice_bridge.py` — lightweight OpenAI-compatible HTTP server that proxies voice-loop
requests through FreeDeepseekAPI with a JARVIS system prompt. No gateway, no Telegram dependency.

**This is now the PRIMARY option** for voice→LLM routing. The Gateway API Server (Option B)
cannot start reliably when `TELEGRAM_ENABLED=true` and Telegram is unreachable from Crimea.

## Quick Start

```bash
# Start the bridge (port 8642)
python D:/Portable_Soft/hermes/scripts/voice_bridge.py

# → Listens on http://127.0.0.1:8642
# → Endpoints: /v1/chat/completions, /health, /v1/models
# → Backend: FreeDeepseekAPI (deepseek-chat) — auto-checked on startup
```

## Port Convention

Port **8642** is reserved for voice bridge / Gateway API Server. Don't use it for other services.

## Provider Detection (order)

1. FreeDeepseekAPI on localhost:9655 — checked on startup, prints `[Bridge] FreeDeepseekAPI: deepseek-chat ✅`
2. `model_registry.get_working_model()` — any alive provider
3. LM Studio absolute fallback (qwen3.5-4b)

If FreeDeepseekAPI is not running, the bridge falls through to model_registry.

## Connection from Voice Loop

The voice loop's `_try_deepseek_free()` now checks the bridge first (port 8642), then
falls back to direct FreeDeepseekAPI (port 9655):

```python
def _try_deepseek_free():
    """Check voice bridge first (port 8642), then direct FreeDeepseekAPI (port 9655)."""
    # ... tries http://127.0.0.1:8642/v1/models first,
    #     then http://127.0.0.1:9655/v1/models as fallback
```

This is already built into the voice loop. To connect manually:
```python
config = {
    "provider": "voice-bridge",
    "model": "deepseek-chat",
    "endpoint": "http://127.0.0.1:8642/v1/chat/completions",
    "api_key": "",
}
```

## System Prompt

The bridge uses the JARVIS voice personality:
- Respond "Сэр" / "Sir"
- 1-3 sentences max (voice channel)
- No markdown, no backticks, no asterisks — plain text for TTS
- Respond in the user's language
- Character: respectful, brief, dry British humor when appropriate

## Testing

```bash
# Health check
curl -s http://127.0.0.1:8642/health

# Chat (English — avoid Russian in curl from git-bash, encoding issues)
curl -s http://127.0.0.1:8642/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"Say hello in 2 words"}],"max_tokens":100}'

# Expected response: {"id": "vb-...", "choices": [{"message": {"content": "Good day, Sir."}}]}
```

**⚠️ curl encoding issue**: When using git-bash on Russian Windows, curl sends Russian
text in CP1251 encoding, not UTF-8, causing the bridge's aiohttp to 500 with
`UnicodeDecodeError`. Always test with English text from the command line.
The voice loop (Python → urllib/requests) sends proper UTF-8 — no issue in production.

## Dependencies

- aiohttp (`pip install aiohttp`) — only dependency not in system Python

## Upgrade Path

When Gateway API Server becomes available (Telegram issue resolved):
1. Stop bridge (Ctrl+C or kill the process)
2. Start gateway with API server on same port:
   ```bash
   unset TELEGRAM_ENABLED
   export TELEGRAM_ENABLED=false
   API_SERVER_ENABLED=true API_SERVER_KEY="your-32-char-key" hermes gateway run
   ```
3. Voice loop needs no URL change — port 8642 stays the same
4. Add `x-api-key` header to voice loop's requests
5. Add `X-Hermes-Session-Id` header for conversation continuity
