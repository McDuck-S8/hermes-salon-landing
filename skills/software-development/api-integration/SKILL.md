---
name: api-integration
description: "Pattern for integrating external API/SDK services into Hermes as usable scripts/tools. Covers: install SDK, configure credentials, explore API structure, create wrapper with error handling, test endpoints, register for reuse."
trigger: When the user asks to integrate/set up/connect an external service, API, SDK, or cloud platform (e.g., 'set up EverOS', 'connect Mistral', 'integrate X'). Also when exploring a new `pip install <package>` to bring functionality into Hermes.
usage: Load with skill_view(name='api-integration') before starting any external service integration to get the proven workflow, pitfall list, and reference templates.
tags: [api, integration, sdk, hermes-tool, service-wrapper]
---

# API Integration Pattern

Integrate an external API/SDK into Hermes as a callable script tool.

## Workflow

### Phase 1: Install & Validate

```python
# Install the SDK
pip install <package-name>

# Quick import check
python -c "import <package>; print(<package>.__version__)"
```

**Pitfall:** If `pip install` fails, try the system python (not venv):
```bash
python -m pip install <package>
```

### Phase 2: Explore API surface

Explore the SDK before writing the wrapper:

```python
import <package>
client = <package>.Client(api_key="...")
print("Resources:", [r for r in dir(client) if not r.startswith('_')])

# List methods of each resource
print(dir(client.v1.memories))  # or whatever the resource is
```

**Key:** Don't guess parameters. Use `inspect.signature()` to check method args:

```python
import inspect
sig = inspect.signature(client.v1.memories.search)
print(list(sig.parameters.keys()))
```

### Phase 3: Create wrapper class

Location: `scripts/<service_name>.py`

Structure:
```python
"""<Service> client — Hermes integration.

Install: pip install <package>
API key: <env_var_name> in .env
API: <base_url>

Usage:
    from scripts.<service> import <ClientClass>
    c = <ClientClass>()
    c.add(...)
"""

import os
import time
from typing import Any

import <package>


class <ClientClass>:
    def __init__(self, api_key: str | None = None):
        api_key = api_key or os.environ.get("<API_KEY_ENV_VAR>")
        if not api_key:
            raise ValueError(
                f"<API_KEY_ENV_VAR> not set. Pass api_key= or export <API_KEY_ENV_VAR>"
            )
        self._client = <package>.EverOS(api_key=api_key)

    # ── Primary actions ──────────────────────────────────────────
    def add(self, ...) -> dict:
        """Docstring describing what and why."""
        ...

    # ── Queries ──────────────────────────────────────────────────
    def search(self, ...) -> dict:
        """Docstring."""
        ...

    # ── Status / helpers ─────────────────────────────────────────
    def _serialize(self, obj: Any) -> dict:
        """Convert pydantic model to plain dict."""
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        ...
```

### Phase 4: Test all endpoints

Test flow for any memory/api service:

```python
# 1. ADD — create data
r = client.add(...)
assert r["status"] == "queued" or "accumulated"

# 2. TASK STATUS — wait for async processing
task_id = r.get("task_id")
if task_id:
    import time
    for i in range(6):
        time.sleep(2)
        s = client.task_status(task_id)
        if s == "success": break

# 3. SEARCH — verify retrievable
r = client.search(...)
assert len(r.get("raw_messages", [])) > 0 or ...
```

**Types of responses to expect:**
- **Synchronous:** immediate result
- **Async (queued):** returns task_id → poll for completion
- **Accumulated:** message buffered, flush needed later

### Phase 5: Register credentials

Add the API key to Hermes `.env`:

```python
with open("D:/Portable_Soft/hermes/.env") as f:
    content = f.read()
if '<ENV_VAR>' not in content:
    content += f'\n# <Service> key\n<ENV_VAR>=<key>\n'
    with open("D:/Portable_Soft/hermes/.env", "w") as f:
        f.write(content)
```

## Pitfalls

### 1. OpenRouter provider routing
OpenRouter uses `x-stainless-*` headers from the OpenAI Python SDK to determine which providers to route through. If the requested providers don't include any provider that hosts the selected model, you get:
```
"No allowed providers are available for the selected model."
```
**Fix:** Switch to a direct provider API (Mistral, etc.) instead of OpenRouter, or configure the OpenRouter headers to include the right providers.

### 2. .env loading scope
SDK config values (like `ENV=DEV`) set in `.env` are only read by tools/libraries that explicitly parse `.env` files. The *process environment* (`os.environ`) is separate. If a feature is controlled by an environment variable check (`os.environ.get("VAR")`), setting it in `.env` won't work unless the app loads `.env` at startup.

**Fix:** Either:
- Add the env var in the launch script before imports: `os.environ.setdefault("VAR", "value")`
- Use the SDK's config mechanism that reads `.env` (if it has one)
- Set it as a real environment variable when starting the process

### 3. Background process output invisibility
On Windows via git-bash, `background=true` processes can have zero visible output because:
- Stdout buffering differs between Windows pipes and Unix PTY
- The process may be writing to stderr which isn't captured the same way
- Exit code comes through but stdout may be empty until process fully exits

**Diagnose:** Use `process(action='log')` to check if output was captured. If the process hangs on startup, check for port-in-use or lock-file issues.

### 4. Port-in-use after kill
On Windows, `kill -9` from git-bash (`SIGKILL`) doesn't always work properly because the signal is not handled the same as on Unix. Python processes may survive.

**Fix:** Always use `taskkill //F //PID <pid>` (Windows native) instead of `kill -9`.

### 5. Windows SSL failures — use httpx with verify=False
On this Windows machine, Python's `requests` library fails with `SSLEOFError: UNEXPECTED_EOF_WHILE_READING` for most HTTPS API endpoints. This is a system-level SSL/TLS issue, not a library bug.

**Affected:** requests, urllib3, litellm (which uses aiohttp internally)
**Working:** `httpx` with `verify=False` and `proxy=None`

```python
import httpx
client = httpx.Client(verify=False, proxy=None)
r = client.post("https://api.example.com/v1/chat/completions",
    headers={"Authorization": f"Bearer {key}"},
    json={"model": "...", "messages": [...]},
    timeout=30)
```

**For litellm specifically:** litellm imports aiohttp which breaks on SSL. Either:
1. Use httpx directly as shown above (preferred)
2. Or fix aiohttp: `pip install --force-reinstall aiohttp` (may need `NO_PROXY="*" pip install aiohttp`)
3. Or set `litellm.suppress_debug_info = True` and catch import errors

**Provider-specific notes (tested 2026-07-09):**
- Cerebras: ✅ works via httpx. Models: `gemma-4-31b`, `gpt-oss-120b`
- DeepSeek: ⚠️ key valid but "Insufficient Balance"
- OpenRouter: ⚠️ free models return 404 "No allowed providers" from this network
- Groq: ❌ 403 "Access denied" (network/region block)

### 6. pip install fails with proxy errors on Windows
When `pip install` hangs or fails with proxy/SSL errors on Windows:
```
ERROR: Could not find a version that satisfies the requirement
```
**Fix:** Bypass proxy entirely:
```bash
NO_PROXY="*" HTTP_PROXY="" HTTPS_PROXY="" http_proxy="" https_proxy="" \
  python -m pip install <package>
```
If still slow, use the venv python directly:
```bash
NO_PROXY="*" HTTP_PROXY="" HTTPS_PROXY="" \
  /d/Portable_Soft/hermes/hermes-agent/venv/Scripts/python.exe -m pip install <package>
```

### 7. Playwright/Crawl4AI — reuse existing browsers
Crawl4AI needs Playwright chromium. Downloading fresh fails on SSL. **Use existing installation:**
```
ls /c/Users/Asus/AppData/Local/ms-playwright/chromium-*/
```
If the installed version doesn't match what Crawl4AI expects (e.g. 1223 vs 1228):
```bash
cmd.exe /c "mklink /D \"C:\Users\Asus\AppData\Local\ms-playwright\chromium_headless_shell-1228\" \"C:\Users\Asus\AppData\Local\ms-playwright\chromium_headless_shell-1223\""
```
Then set env before running: `PLAYWRIGHT_BROWSERS_PATH="C:/Users/Asus/AppData/Local/ms-playwright"`

### 8. FreeDeepseekAPI requires PTY (interactive terminal)
`node server.js` silently exits if `!process.stdin.isTTY` (line 50 of server.js).
**Fix:** Always start with `pty: true` in terminal tool, then select menu option (typically "3" to start server).

### 9. SDK response objects vs dicts
Newer SDKs (especially those built with pydantic/openai pattern) return typed objects, not plain dicts. Attempting `.keys()` on these will raise `AttributeError`.

**Fix:** First check `type(resp)` and `dir(resp)` to understand the object structure. Use `.model_dump()` if it's a pydantic model, or access via attributes.

## Verification checklist

- [ ] SDK installed and imports without error
- [ ] API key accessible (env var or explicit)
- [ ] At least one successful write/add call
- [ ] Data retrievable via search/get call
- [ ] Async tasks complete with 'success' status
- [ ] Credentials saved to Hermes `.env`
- [ ] Wrapper script saved in `scripts/`
- [ ] Script runs standalone (`python scripts/<name>.py`)

## When to search existing skills

Before integrating a new external service, check if a skill already exists for it:
- `skill_view(name='<service-name>')` — direct match
- `skills_list(category='<category>')` — browse by category

If the service already has a skill and it's outdated, patch it instead of creating a new wrapper.

## Known Access Issues (2026-06-27)

### Telegram channel scraping blocked
Some Telegram channels are inaccessible for automatic scraping:
- `t.me/s/openai` — blocked
- `t.me/s/binance` — blocked
- `t.me/s/securitylab` — blocked

**Root cause:** Telegram blocks automated parsing of public channel previews.

**Workarounds:**
1. Use Telegram Bot API with channel member access
2. Set up RSS-to-Telegram bridge (e.g., tgram2rss)
3. Use Telegram Bot API to forward messages to your own channel
4. Manual extraction via browser (unreliable for automation)
