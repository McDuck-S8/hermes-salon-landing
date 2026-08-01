# FreeDeepseekAPI — Recovery & Startup

## Location
`D:\\Portable_Soft\\FreeDeepseekAPI\\`

## What it is
OpenAI-compatible local API proxy for DeepSeek Web Chat. Uses authenticated browser session to proxy requests to `chat.deepseek.com`. Zero npm dependencies (pure Node.js built-ins).

## Port
`127.0.0.1:9655`

## Detection (DOWN check)
```bash
curl -s http://127.0.0.1:9655/v1/models
```
Returns JSON list of ~11 models when alive. Empty/timeout = dead.

## Startup
```bash
env NON_INTERACTIVE=1 node "D:/Portable_Soft/FreeDeepseekAPI/server.js"
```
**`env NON_INTERACTIVE=1` is REQUIRED** — without it, server.js enters an interactive terminal menu (readline prompts) that wedges in non-TTY shell.

## Proxy requirement (from Crimea)

FreeDeepseekAPI uses `fetch()` to reach `https://chat.deepseek.com` — this call BLOCKS without a proxy from Crimea. **Start with ALL_PROXY set:**

```bash
env NON_INTERACTIVE=true ALL_PROXY=socks5://127.0.0.1:10806 node "D:/Portable_Soft/FreeDeepseekAPI/server.js"
```

## Background process pattern (Windows, MSYS bash)
```python
from hermes_tools import terminal

terminal(
    command='cd /d/Portable_Soft/FreeDeepseekAPI && '
            'export NON_INTERACTIVE=true && '
            'export ALL_PROXY=socks5://127.0.0.1:10806 && '
            'export HTTP_PROXY=socks5://127.0.0.1:10806 && '
            'export HTTPS_PROXY=socks5://127.0.0.1:10806 && '
            'node server.js',
    background=True,
    timeout=999999
)
```
**Background notes:**
- Do NOT use `&` — bash in non-TTY can't do job control
- `export` is safer than `env VAR=val` prefix in background shell: bash unrolls exports but env prefix sometimes gets swallowed at fork
- `cd` ensures server.js resolves paths relative to project dir

## Auth
Pre-configured in `deepseek-auth.json`:
- `token` — Bearer token
- `cookie` — session cookie (`ds_session_id=...`)
- `hif_dliq`, `hif_leim` — DeepSeek-specific headers

Auth is loaded automatically at startup via `loadDeepSeekConfig()`.

## Models available
- `deepseek-chat` / `deepseek-default` — V4-Flash non-thinking
- `deepseek-reasoner` / `deepseek-r1` — V4-Flash thinking mode
- `deepseek-expert` / `deepseek-v4-pro` — DeepSeek "Эксперт" tier
- `*-search` variants — same models with web search enabled

## API endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/models | List supported models |
| POST | /v1/chat/completions | OpenAI Chat Completions (stream=true/false) |
| POST | /v1/messages | Anthropic Messages shim |
| POST | /v1/responses | OpenAI Responses API shim |
| GET | /v1/model-capabilities | Real model mapping |
| POST | /reset-session?agent=<id> | Reset agent session |

## When to restart
- After DeepSeek Web API changes (session invalidated)
- After auth refresh (rerun deepseek_chrome_auth.js)
- Port 9655 shows DOWN in chain_heartbeat for >1 cycle
- After network proxy change (v2rayN port changed or proxy restarted)

## Pitfalls
- DO NOT run bare `node server.js` without `NON_INTERACTIVE=1` — it hangs on stdin
- `&` backgrounding in MSYS bash prints "stdin is not a tty" and kills the process
- Always use `export VAR=val` chain in background terminal(), not env-prefix
- Without ALL_PROXY, `fetch()` to chat.deepseek.com returns "fetch failed" from Crimea
- Node.js process survives shell session close on Windows (background=true), but need taskkill /F /IM node.exe to force-kill stale instances before restart
