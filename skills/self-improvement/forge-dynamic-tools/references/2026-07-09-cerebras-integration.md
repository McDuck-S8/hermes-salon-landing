# Cerebras + DeepSeek Local Integration & Provider Status (2026-07-09)

## What Changed
- Replaced raw `call_deepseek()` (localhost:9655) in forge.py with unified `llm_client.py`
- Cerebras gemma-4-31b is the primary LLM provider (cloud)
- DeepSeek Local (FreeDeepseekAPI, localhost:9655) is the secondary provider
- httpx (not aiohttp/requests) is the HTTP transport due to Windows SSL issues

## Provider Test Results (2026-07-09)

### Working
```
CEREBRAS       gemma-4-31b   OK  → "OK"  (cloud, primary)
DEEPSEEK-LOCAL deepseek-chat OK  → "OK"  (localhost:9655, FreeDeepseekAPI)
```

### Failed
```
DEEPSEEK   deepseek-chat           402  Insufficient Balance (cloud API)
GROQ       llama-3.3-70b-versatile 403  Access denied (region/network block)
OPENROUTER openai/gpt-4o-mini      404  No allowed providers available
OPENGATEWAY meta-llama/llama-3.3-70b-instruct  SSL: UNEXPECTED_EOF_WHILE_READING
```

## DeepSeek Local (FreeDeepseekAPI)

The local DeepSeek server runs on `localhost:9655` via FreeDeepseekAPI
(`D:/Portable_Soft/FreeDeepseekAPI/server.js`). It proxies DeepSeek Web Chat
using saved browser auth tokens — no API key needed.

### Starting the Server

**Critical:** FreeDeepseekAPI requires PTY for Node.js readline menu.

```bash
# In Hermes terminal tool:
terminal(background=true, pty=true, command="cd /d/Portable_Soft/FreeDeepseekAPI && node server.js")
# Then: process(action='submit', data='3', session_id=...)
```

Without `pty=true`, the process exits immediately with "stdin is not a tty".

### Available Models (11 total)
deepseek-chat, deepseek-v3, deepseek-default, deepseek-reasoner, deepseek-r1,
deepseek-chat-search, deepseek-default-search, deepseek-reasoner-search,
deepseek-r1-search, deepseek-expert, deepseek-v4-pro

### Auth Token Location
`D:/Portable_Soft/FreeDeepseekAPI/deepseek-auth.json` — contains session token,
cookies, WASM solver URL. Expires periodically; re-auth via browser.

## OpenRouter Free Models Discovery
Models exist on OpenRouter (`qwen3-next-80b`, `tencent/hy3:free`, etc.) but
return "No allowed providers are available" — OpenRouter routes free models
through providers that may not be available from this network.

## Cerebras Available Models
```
gemma-4-31b
zai-glm-4.7
gpt-oss-120b
```

## Technical Details

### Why httpx over aiohttp/requests
- `requests`: SSL error even with `verify=False` on Windows
- `aiohttp` (litellm default): SSL UNEXPECTED_EOF on proxy HTTPS
- `httpx` with `verify=False, proxy=None`: Works reliably

### aiohttp Corruption Fix
litellm depends on aiohttp. On this machine aiohttp installed as a namespace
package (only .pyd/.pyx files, no `__init__.py`). Fix:
```bash
rm -rf venv/Lib/site-packages/aiohttp*
pip install --force-reinstall aiohttp
```

### Forge Prompt Escaping
FORGE_PROMPT contains JSON examples. Python `.format()` interprets `{}` as
placeholders. All literal braces must be doubled: `{{` and `}}`.
Only the actual `{task}` placeholder stays unescaped.

### Sandbox API Key Isolation
Forge sandbox runs with `PYTHONPATH=''` — environment variables from `.env`
are NOT available to generated scripts. Scripts needing API keys must be
written directly, not forge-generated.

### ALLOWED_IMPORTS Must Include Parent Packages
LLM generates `import urllib` but validator only had `urllib.request` etc.
Fix: add parent packages (`urllib`, `html`) to ALLOWED_IMPORTS.
