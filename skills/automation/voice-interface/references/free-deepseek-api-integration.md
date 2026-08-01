# FreeDeepseekAPI Integration

## What

FreeDeepseekAPI (`D:/Portable_Soft/FreeDeepseekAPI`) is a local Node.js proxy server that provides an OpenAI-compatible API endpoint by routing through an authenticated DeepSeek Web Chat session. No API key cost, no rate limits — unlimited requests as long as the DeepSeek web session is valid.

## Where

- **Location**: `D:/Portable_Soft/FreeDeepseekAPI/`
- **Auth config**: `deepseek-auth.json` (already configured with session tokens)
- **Default port**: 9655
- **Server**: `server.js` (Node.js, no npm deps, stdlib only)

## Auto-detection in Voice Loop

The voice loop (`jarvis_voice_loop.py`) calls `_try_deepseek_free()` at startup:

```python
def _try_deepseek_free():
    """Check if FreeDeepseekAPI is alive on port 9655."""
    import urllib.request
    try:
        req = urllib.request.Request("http://127.0.0.1:9655/v1/models", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read())
            models = [m["id"] for m in data.get("data", [])]
            if "deepseek-chat" in models:
                return {
                    "provider": "deepseek-free",
                    "model": "deepseek-chat",
                    "base_url": "http://127.0.0.1:9655/v1",
                    "api_key": "",
                    "endpoint": "http://127.0.0.1:9655/v1/chat/completions",
                    "type": "proxy",
                }
    except Exception:
        pass
    return None
```

The 2s timeout means startup is barely delayed if FreeDeepseekAPI is down.

## Starting the Server

```bash
cd /d/Portable_Soft/FreeDeepseekAPI
NON_INTERACTIVE=true PORT=9655 node server.js
```

- `NON_INTERACTIVE=true` skips the interactive menu
- `PORT=9655` is the default, can be changed if port conflict
- Script is persistent: survives session kills, stays running as long as the parent shell lives
- Port conflict (`EADDRINUSE`) means it's already running — just use it

## Available Models

| Model ID | Description | Best for |
|----------|-------------|----------|
| `deepseek-chat` | V4-Flash, non-thinking, fast | Voice (low latency) |
| `deepseek-reasoner` | V4-Flash with thinking | Complex reasoning (slower) |
| `deepseek-expert` | Expert mode (limited) | Heavy tasks (resources limited) |
| `deepseek-v4-pro` | Expert + thinking | Best quality (limited) |

## Why It Solves the Rate Limit Problem

- **opencode-zen free tier**: 2-3 requests/min before 429
- **FreeDeepseekAPI**: unlimited requests through DeepSeek Web Chat session
- Voice mode sends 4-12 utterances/minute → opencode-zen blocks, FreeDeepseekAPI doesn't

## Session Persistence

FreeDeepseekAPI maintains per-agent sessions (keyed by the `user` field in API requests):
- Auto-resets after 50 messages or 2 hours
- The voice loop does NOT set a `user` field (uses default session)
- Sessions can be reset: `POST /reset-session?agent=all`

## When It Breaks

- DeepSeek Web Chat changes their internal API → FreeDeepseekAPI needs updates
- Session token expires → re-auth through the chrome auth script: `node scripts/deepseek_chrome_auth.js`
- Voice loop runs but "forgets" about FreeDeepseekAPI → restart the voice loop after starting the server
