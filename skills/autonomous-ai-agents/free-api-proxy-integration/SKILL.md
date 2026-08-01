---
name: free-api-proxy-integration
description: "Integrate free browser-based API proxies (Qwen, DeepSeek, etc.) into Hermes as custom_providers. Covers repo discovery, installation, browser auth, Hermes config, and troubleshooting."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, providers, free-api, proxy, integration, qwen, deepseek]
    related_skills: [hermes-agent]
---

# Free API Proxy Integration

Integrate free browser-based LLM API proxies into Hermes as custom providers.
These proxies convert free web chat accounts (Qwen Chat, DeepSeek Web, etc.)
into local OpenAI-compatible API endpoints.

## What This Covers

- Finding and cloning free API proxy repos on GitHub
- Installing dependencies (npm install or zero-dep)
- Browser-based authorization (Chrome opens → login → token saved)
- Configuring Hermes `custom_providers` in config.yaml
- Starting/stopping proxy services
- Troubleshooting common issues

## Architecture

```
Hermes Agent  →  Local Proxy Server  →  Web Chat (browser session)
  (custom)         (port N)               (chat.qwen.ai / chat.deepseek.com)
```

The proxy emulates OpenAI-compatible API. Hermes treats it as a normal
OpenAI endpoint with `provider: "custom"`.

## Prerequisites

- Node.js >= 18
- Chrome/Chromium (for browser-based auth)
- Account on the target web chat service

## Step-by-Step Workflow

### 1. Find the Repository

When web_search is unavailable, use GitHub REST API:

```bash
# Search repos by name
curl -s "https://api.github.com/search/repositories?q=FreeQwenApi" | python -m json.tool

# Get README directly
curl -s "https://raw.githubusercontent.com/OWNER/REPO/main/README.md"
```

Key fields from search results:
- `full_name`: owner/repo
- `clone_url`: HTTPS clone URL
- `description`: what it does
- `pushed_at`: last activity (check if maintained)

### 2. Clone and Install

```bash
cd /d/Portable_Soft  # or wherever you keep tools
git clone https://github.com/OWNER/REPO.git
cd REPO
npm install  # skip if package.json has no dependencies
```

### 3. Browser Authorization

Every free proxy requires browser login. The pattern is always:

```bash
npm run auth
```

This opens Chrome. You log into the web chat service. The proxy saves
the session token to a local file. The token expires — re-auth with:

```bash
npm run auth -- --relogin   # Qwen
npm run auth                # DeepSeek (re-runs the auth flow)
```

Token locations (DO NOT commit these):
- FreeQwenApi: `session/accounts/` directory
- FreeDeepseekAPI: `deepseek-auth.json` + `.chrome-profile-deepseek/`

### 4. Configure Hermes

Add to `config.yaml` under `custom_providers:`:

```yaml
custom_providers:
  - name: provider-name
    base_url: http://localhost:PORT/api  # or /v1
    model: default-model-name
    api_key: dummy-key                   # proxies don't check keys
    context_length: 131072               # optional
```

The `name` becomes the provider identifier. Models are accessed as:
`custom/model-name` (e.g., `custom/qwen3.7-max`).

### 5. Start the Proxy

```bash
# Headless/CI mode (no interactive menu):
SKIP_ACCOUNT_MENU=true node index.js &       # Qwen
NON_INTERACTIVE=1 node server.js &           # DeepSeek (for Linux/macOS)
```

**Windows (Git Bash) note:** The `&` backgrounding exits when the terminal closes.
Use `terminal(background=true, pty=true, notify_on_complete=true)` in Hermes tool
calls to keep the process alive while the session needs it, OR use native Windows
detach:

```bash
# Windows persistent detach via cmd (for services/scripts):
cmd //c "start /B node index.js"           # Qwen
cmd //c "start /B node server.js"          # DeepSeek
```

For hermetic startup (daemon-like), create a .bat launcher and pin it with
`terminal()` — the pty=true flag provides the TTY that Node's `readline`
requires, and background keeps it running until the job's work is done.

### 6. Verify

```bash
curl http://localhost:PORT/api/health   # Qwen
curl http://localhost:PORT/             # DeepSeek
curl http://localhost:PORT/v1/models    # DeepSeek model list
```

### 7. Switch Hermes Model

```
/model custom/qwen3.7-max
/model custom/deepseek-chat
```

## Known Free API Proxies

| Project | Repo | Port | Models |
|---------|------|------|--------|
| FreeQwenApi | ForgetMeAI/FreeQwenApi | 3264 | qwen3.7-max, qwen3.7-plus, qwen3-coder-plus, qwq-32b, qwen3-235b-a22b (28 models) |
| FreeDeepseekAPI | ForgetMeAI/FreeDeepseekAPI | 9655 | deepseek-chat, deepseek-reasoner, deepseek-expert |

## Pitfalls

0. **CHECK WHAT'S ALREADY INSTALLED FIRST.** Before suggesting new providers or models, verify what's already configured in `config.yaml` and what services are running. The user has FreeQwenApi, FreeDeepseekAPI, Ollama, and LM Studio already installed. Don't suggest adding things that are already there — check ports (`netstat -ano | grep PORT`), check config, then act.

1. **Tokens expire** — if you get 401/403, re-auth with `npm run auth`
2. **Web API changes** — these are unofficial proxies; upstream can break them
3. **Rate limits** — free web chats have usage limits; multi-account proxies
   support round-robin rotation
4. **No tools in proxy** — tool calling is emulated via system prompt,
   not native; complex agent loops may not work perfectly. **However**,
   FreeQwenApi (2026-06-10+) added `toolParser.js` for agent tool-use
   compatibility — it normalizes tool calls from various formats (OpenAI,
   Anthropic, custom). If tool calling fails, check if your proxy version
   includes this parser.
5. **Disk space** — FreeQwenApi has ~333 npm packages; FreeDeepseekAPI is zero-dep
6. **Port conflicts** — check if port is already in use before starting

### DeepSeek-Specific Critical Pitfalls

7. **wasmUrl required in auth config** — DeepSeek uses a Proof-of-Work challenge
   (WebAssembly) for every chat completion. The server needs `wasmUrl` in
   `deepseek-auth.json` to download the WASM solver. Without it, ALL requests
   fail with `"Failed to parse URL from undefined"`. The auth script extracts
   this from page resources; if doing manual CDP extraction, add it:
   ```json
   {
     "wasmUrl": "https://fe-static.deepseek.com/chat/static/sha3_wasm_bg.7b9ca65ddd.wasm",
     "baseUrl": "https://chat.deepseek.com"
   }
   ```
   The WASM URL may change over time. If POW fails, check the page resources
   for a new `sha3_wasm_bg.*.wasm` URL.

8. **FreeDeepseekAPI needs PTY for non-interactive startup** — The `prompt()`
   function in server.js already has the TTY guard:
   ```js
   if (!process.stdin.isTTY) { return Promise.resolve(''); }
   ```
   Despite the guard, Node.js itself can emit "stdin is not a tty" at module
   load time when `readline` is imported without a TTY. To reliably start:
   - **Run with `pty=true` in terminal tool** (recommended)
   - **Or set `NON_INTERACTIVE=1` AND pipe stdin from a file**: `node server.js < /dev/null`
   - Without PTY, the process exits silently (exit code 1) even though prompt()
     has the guard

9. **DeepSeek auth via Comet CDP (no auth script needed)** — When the user
   is already logged into DeepSeek in Comet, extract tokens directly via
   Chrome DevTools Protocol instead of running the auth script:
   ```
   1. Kill running Comet, restart with: comet.exe --remote-debugging-port=9222 --user-data-dir="Profile Path"
   2. Use puppeteer (from FreeQwenApi's node_modules) to connect to tab
   3. Extract from localStorage: userToken, hif_dliq_cached, hif_leim_cached
   4. Extract cookies via Network.getAllCookies (domain: deepseek.com)
   5. Get wasmUrl from page resources: performance.getEntriesByType('resource')
   6. Save to deepseek-auth.json
   ```
   See `references/comet-cdp-extraction.md` for the full extraction script.

10. **Comet profile locking** — Comet cannot run two instances with the same
    `--user-data-dir`. If Comet is already running, a new launch with a
    different `--user-data-dir` either fails or shares the existing process
    (no CDP access). Must kill existing Comet first, then relaunch with
    `--remote-debugging-port`.

### Windows-Specific Pitfalls

11. **Chrome path not found** — DeepSeek auth hardcodes macOS path
    (`/Applications/Google Chrome.app/...`). Set CHROME_PATH env var:
    ```bash
    export CHROME_PATH="D:/Portable_Soft/puppeteer-cache/chrome/win64-148.0.7778.97/chrome-win64/chrome.exe"
    ```
    FreeQwenApi's `.env` already has this set.

12. **Non-TTY stdin crash** — `prompt.js` and `auth.js` use readline on
    stdin. In non-interactive terminals (git-bash, background processes),
    `process.stdin.isTTY` is undefined, causing `readline.createInterface`
    to crash or hang. Fix: add TTY guard:
    ```js
    if (!process.stdin.isTTY) { return Promise.resolve(''); }
    ```
    Both FreeQwenApi files and FreeDeepseekAPI server.js were patched.

13. **curl Cyrillic encoding on Windows** — `curl -d '{"content":"Кириллица"}'`
    on Git Bash/MSYS2 mangles UTF-8. Solution: write JSON to file, then:
    ```bash
    curl -s -H "Content-Type: application/json" -d @request.json http://...
    ```

14. **tokenManager.js TOKENS_FILE corruption** — the constant can get
    corrupted to `const TOKENS_FILE=*** 'tokens.json');`. The correct
    line is:
    ```js
    const TOKENS_FILE=path.join(ACCOUNTS_PATH, 'tokens.json');
    ```
    If the proxy starts but shows empty account list and loops in menu,
    check this file. Note: some tool environments redact `path.join(` as
    if it were a secret — use `printf` or `python` via terminal to write
    the fix.

15. **Port cleanup on Windows** — `kill <pid>` in Git Bash does NOT work
    for Windows processes. Use `taskkill //F //PID <pid>` (double-slash
    escapes MSYS path mangling). Check ports with:
    ```bash
    netstat -ano | grep <PORT>
    taskkill //F //PID <PID_FROM_NETSTAT>
    ```
    The EADDRINUSE error is common when restarting proxies — always kill
    the old process first.

16. **Token storage format** — FreeQwenApi stores tokens as JSON array:
    ```json
    [{"id": "acc_...", "token": "redacted", "resetAt": "2026-..."}]
    ```
    in `session/tokens.json`. If this file is missing or empty after auth,
    the proxy will not find any accounts.

17. **SSL blocking from Crimea/RU** — Puppeteer browser in FreeQwenApi
    may fail with `ERR_CONNECTION_CLOSED` when connecting to chat.qwen.ai.
    The health endpoint works (no browser needed), but actual chat
    completions fail. **Fix**: route Puppeteer traffic through a SOCKS5/HTTPS
    proxy. In `src/browser/browser.js`, add `--proxy-server` to Chromium args:
    ```js
    `--proxy-server=${process.env.PROXY_SERVER || 'http://127.0.0.1:10807'}`
    ```
    
    **v2rayN + Puppeteer gotcha**: v2rayN exposes:
    - SOCKS5 on port 10806
    - HTTP mixed proxy on port 10807
    
    Chromium's `--proxy-server` flag works with HTTP proxies but NOT reliably
    with `socks5://` prefix on Windows. Use the HTTP port (`http://127.0.0.1:10807`).
    Even then, Chromium may still get `ERR_CONNECTION_CLOSED` on HTTPS sites
    through v2rayN's HTTP proxy — this is a Chromium + v2rayN interaction issue.
    **Workaround**: enable v2rayN's TUN/transparent proxy mode (System Proxy mode
    won't help since Puppeteer bypasses OS proxy settings). If TUN is not available,
    test with `curl --proxy http://127.0.0.1:10807 https://chat.qwen.ai` first —
    if curl works but Puppeteer doesn't, the issue is Chromium-specific.
    
    Set proxy via env var for flexibility:
    ```bash
    PROXY_SERVER=http://127.0.0.1:10807 SKIP_ACCOUNT_MENU=true node index.js
    ```

### NEW: llm_client.py Integration (2026-07-09)

FreeDeepseekAPI is now integrated into `scripts/llm_client.py` as the
`deepseek-local` provider. The unified client uses it as a fallback when
Cerebras (primary) fails. Provider chain:

```
Cerebras (cloud) → DeepSeek Local (localhost:9655) → DeepSeek Cloud → Groq → OpenRouter
```

The `deepseek-local` provider uses a `_LOCAL_DEEPSEEK` sentinel key — it's
always included in the chain regardless of API keys. The httpx transport with
`verify=False, proxy=None` is used for all providers (Windows SSL workaround).

**forge.py** now uses `llm_client.call_llm()` instead of raw `call_deepseek()`.
Forge supports `--provider deepseek-local` to force using the local server.

### NEW: Direct Paid Providers (bypass free proxies entirely) (2026-07-09)

When free proxies are unreliable (token expiry, upstream breaks, geo-blocks),
use direct API providers. From this machine, **Cerebras** is the only provider
that reliably works via `httpx.Client(verify=False, proxy=None)`.

```python
import httpx, os
client = httpx.Client(verify=False, proxy=None)
r = client.post("https://api.cerebras.ai/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['CEREBRAS_API_KEY']}"},
    json={"model": "gemma-4-31b", "messages": [{"role": "user", "content": "..."}], "max_tokens": 200})
```

**Model names are NOT standard** — check `GET /v1/models` first.
Available: `gemma-4-31b`, `gpt-oss-120b`, `zai-glm-4.7`.

See `references/llm-providers-status.md` in `api-integration` skill for full
provider status table (DeepSeek, OpenRouter, Groq — all blocked from this network).

### NEW: LiteLLM Gateway Integration (2026-06-28)

**Architecture evolution:** Free API proxies (FreeQwenApi, FreeDeepseekAPI) are now **upstream providers** for LiteLLM gateway. LiteLLM provides unified OpenAI-compatible endpoint with fallback, load balancing, cost tracking.

```yaml
# litellm_config.yaml (created D:/Portable_Soft/hermes/litellm_config.yaml)
model_list:
  - model_name: qwen-free
    litellm_params:
      model: custom/qwen3.7-max
      api_base: http://localhost:3264/api
      api_key: dummy-key
  - model_name: deepseek-free
    litellm_params:
      model: deepseek-chat
      api_base: http://localhost:9655/v1
      api_key: dummy-key
```

**Benefits over direct custom_providers:**
- Single endpoint (`http://localhost:4000/v1`) for ALL models
- Automatic fallback when one provider fails
- Cost/budget tracking across all free tiers
- Virtual keys for different agents/workflows
- Health checks + automatic cooldown

**Run LiteLLM proxy:**
```bash
litellm --config D:/Portable_Soft/hermes/litellm_config.yaml --port 4000
```

### NEW: MCP Server Integration (2026-06-28)

MCP servers configured in `~/.hermes/config.yaml` for agent-native tool access:

| Server | Transport | Purpose |
|--------|-----------|---------|
| context7 | HTTP | 7,000+ library docs, versioned |
| duckduckgo | HTTP | Web search, no API key |
| github | HTTP | Repos, issues, PRs, code search |
| playwright | stdio (npx) | Browser automation, screenshots |
| filesystem | stdio (npx) | Local file ops |
| sequentialthinking | stdio (npx) | Structured reasoning (Anthropic) |
| supabase | HTTP | Database, realtime, auth |
| browser | stdio (npx) | Local browser profile, cookies |

**Need Hermes restart to activate.**

### NEW: x402 Agent Economy (2026-06-28)

**Agent-to-agent micropayments via USDC on Base L2** — no API keys, no accounts, HTTP 402 flow.

| Server | Install | Use Case |
|--------|---------|----------|
| @2sio/mcp | `npx -y @2sio/mcp` | 180+ tools (weather, arXiv, patents, WHOIS, court cases) |
| swarmwage | npm | MCP-native agent hiring protocol (discovery + hire + reputation) |
| x402search | `npx -y x402-index/x402search-mcp` | Search 14K+ x402 APIs ($0.01/search) |
| blockrun-mcp | npx | 30+ AI models (GPT-5, Claude, Gemini) pay-per-use |

**Arbitrage opportunity:** Buy API call at $0.001 → resell to agent at $0.01 = 10x margin.

```bash
# Search
curl -s "https://api.github.com/search/repositories?q=QUERY" | python -m json.tool

# Get repo info
curl -s "https://api.github.com/repos/OWNER/REPO" | python -m json.tool

# Get file content
curl -s "https://raw.githubusercontent.com/OWNER/REPO/main/README.md"

# List repo contents
curl -s "https://api.github.com/repos/OWNER/REPO/contents/" | python -m json.tool
```

## References

- FreeQwenApi README: https://github.com/y13sint/FreeQwenApi
- FreeDeepseekAPI README: https://github.com/ForgetMeAI/FreeDeepseekAPI
- Hermes custom_providers: https://hermes-agent.nousresearch.com/docs/user-guide/configuration

### Windows-Specific References

- `references/v2rayn-puppeteer-proxy.md` — v2rayN ports, Puppeteer compatibility issues, TUN mode workaround
- `references/windows-setup.md` — Chrome paths, TTY issues, port cleanup, Cyrillic curl fix, startup commands
- `references/windows-search.md` — Everything (voidtools) es.exe CLI for instant file search; query syntax, combining with grep for content search, exclusion patterns, and use-case table vs grep/search_files
