# FreeDeepseekAPI — Local DeepSeek Web API Proxy (2026-07-20)

## Overview
FreeDeepseekAPI is a Node.js server that wraps DeepSeek Web chat (chat.deepseek.com) as an **OpenAI-compatible API** on `http://localhost:9655/v1`. It uses a persistent Chrome profile (`.chrome-for-testing-profile-deepseek`) for authentication via cookies/tokens.

## Installation
```bash
cd D:/Portable_Soft/FreeDeepseekAPI
npm install  # or npm ci
```

## Running
```bash
# Foreground
node server.js

# Background (survives terminal close)
# On Windows:
start /B node server.js
# Or via Hermes background process
```

## Configuration
- **Port**: 9655 (hardcoded in server.js, override with `PORT` env var)
- **Auth**: Reads from `deepseek-auth.json` (token, cookies, hif_dliq, hif_leim)
- **Chrome profile**: `.chrome-for-testing-profile-deepseek/` — persists login state
- **Models exposed**: 12 variants (deepseek-chat, deepseek-reasoner, deepseek-v3, deepseek-r1, deepseek-expert, etc.)

## API Endpoints
- `GET /v1/models` — List available models (OpenAI format)
- `POST /v1/chat/completions` — Chat completions (streaming + non-streaming)
- Tool calling: injects tool definitions into system prompt, parses `TOOL_CALL:` patterns from text response

## Proxy Requirements
- **Outbound to DeepSeek**: Needs SOCKS5 proxy (127.0.0.1:10806 via V2RayN) for `chat.deepseek.com`
- **Inbound from Hermes**: Direct localhost (no proxy needed)

## Integration with Hermes

### Chain Heartbeat
```python
# scripts/chain_heartbeat.py
EXTERNAL_SERVICES = {
    "deepseek_local": {"host": "127.0.0.1", "port": 9655, "timeout_s": 5},
    ...
}
```
Heartbeat shows `HEALTHY` when server responds, `DOWN` when not running.

### LLm Client (llm_client.py)
```python
PROVIDERS = [
    {"name": "deepseek-local", "model": "deepseek-chat", "base_url": "http://localhost:9655/v1", "env_key": "_LOCAL_DEEPSEEK"},
    ...
]
```
Uses `call_llm()` with automatic fallback across providers.

### Telegram Bot (mcduck_bot.py)
- Uses `MCDUCK_BOT_TOKEN` from `.env` (not the CrystalWatchBot token)
- Long-polling via `urllib` + `PySocks` for SOCKS5 proxy
- Every user message → Hermes LLM pipeline → real response
- Commands: `/report` (system_heartbeat.json), `/ripple` (daily_ripple_map.html)

## Startup Sequence (for full Hermes boot)
1. **V2RayN** running (port 10806 SOCKS5)
2. **FreeDeepseekAPI** running (port 9655)
3. **BrowserOS** (port 9003) + **BrowserClaw** (port 9010)
4. **Hermes Gateway** (port 9003) with `telegram.proxy_url: "socks5://127.0.0.1:10806"`
5. **Cron ticker** (gateway daemon thread) — drives scheduled jobs
6. **mcduck_bot.py** as background process

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Connection to 127.0.0.1:9655 failed` | Server not running | `cd D:/Portable_Soft/FreeDeepseekAPI && node server.js` |
| `getMe() 404 Not Found` | Wrong token | Use `MCDUCK_BOT_TOKEN` (6187967109) not CrystalWatchBot token |
| `httpx ConnectTimeout` on telegram_api | Direct connection blocked | Gateway must use `socks5://127.0.0.1:10806` proxy |
| `ModuleNotFoundError: socks` | PySocks missing | `pip install PySocks` |
| DeepSeek auth expired | Cookies/token stale | Delete `deepseek-auth.json`, re-run `node scripts/auth.js` |

## Key Files
```
D:/Portable_Soft/FreeDeepseekAPI/
├── server.js              # Main HTTP server
├── package.json           # Dependencies
├── deepseek-auth.json     # Auth tokens (gitignored)
├── .chrome-for-testing-profile-deepseek/  # Persistent Chrome profile
├── scripts/
│   ├── auth.js            # Login flow
│   └── deepseek_chrome_auth.js
└── docs/api-documentation.md
```

## Verification
```bash
# Models endpoint
curl http://127.0.0.1:9655/v1/models

# Chat completion
curl -X POST http://127.0.0.1:9655/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"Say hello in one word"}],"max_tokens":50}'
```

## Notes
- **No new API keys needed** — reuses DeepSeek Web session cookies
- **Single-file deployment** — everything in one Node.js process
- **Hermes-native** — lives inside `D:/Portable_Soft/hermes` tree, uses Hermes `.env`
- **Not a separate project** — no `mira-agent/`, no `MIRA_LLM_KEY`, no separate config