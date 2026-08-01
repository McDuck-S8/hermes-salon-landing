# BrowserClaw MCP Setup

> BrowserClaw — free, open-source (AGPL-3.0) browser that AI agents drive via MCP. Alternative to BrowserOS browser, ChatGPT Atlas, Perplexity Comet.

## Architecture

```
BrowserClaw (chrome.exe, port 9010) ←→ Hermes Agent
       ↕
claw-server (port 9210) — backend service
```

- **Port 9010**: BrowserClaw browser's MCP endpoint (Streamable HTTP). This is what agents connect to.
- **Port 9210**: `browseros-claw-server` (v0.0.7) — backend that manages browser sessions, screenshots, CDP.

## Installation

The installer is a 7-Zip SFX (PE32+ GUI executable):

```bash
# Silent install
"/path/to/BrowserClaw_installer.exe" /S
```

Installs to `%LOCALAPPDATA%\BrowserClaw`:
- `Application\chrome.exe` — Chromium-based browser (v148+)
- `Application\BrowserClawServer\` — server component

After install, claw-server auto-starts. The browser (chrome.exe) must be launched separately to open the MCP endpoint.

## MCP Protocol Details

Transport: **Streamable HTTP** (MCP 2024-11-05)

Key difference from standard MCP: **Session-based via HTTP header**

### Connection Flow

1. **Initialize** — POST `/mcp` with `initialize` method
2. **Capture `mcp-session-id`** from response headers
3. **Set `mcp-session-id` header** on ALL subsequent requests
4. Call `tools/list`, `tools/call`, etc.

### Session Header

```yaml
# Every request EXCEPT initial initialize needs this header
mcp-session-id: "<uuid from initialize response>"
```

Without the session header, the server returns `400 Bad Request: Server not initialized`.

### Python Implementation Pattern

```python
import urllib.request, json

base = "http://127.0.0.1:9010"
session_id = None

def mcp_call(method, params=None, id=1):
    global session_id
    payload = {"jsonrpc": "2.0", "method": method, "id": id}
    if params:
        payload["params"] = params
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    if session_id:
        headers["mcp-session-id"] = session_id
    
    req = urllib.request.Request(f"{base}/mcp",
        data=json.dumps(payload).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        if 'mcp-session-id' in resp.headers:
            session_id = resp.headers['mcp-session-id']
        return json.loads(resp.read().decode())

# Usage:
init = mcp_call("initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "hermes-agent", "version": "1.0.0"}
}, id=1)

tools = mcp_call("tools/list", id=2)
tabs = mcp_call("tools/call", {
    "name": "tabs", "arguments": {"action": "list"}
}, id=3)
```

### Hermes Config Registration

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  browserclaw:
    type: http
    url: http://127.0.0.1:9010/mcp
```

After restart, tools appear as `mcp_browserclaw_*`.

## Available Tools (16 total)

| Tool | Description | Key Params |
|------|-------------|------------|
| `tabs` | List/active/new/close tabs | `action`, `url`, `background`, `hidden` |
| `tab_groups` | Group/ungroup tabs | `action`, `pages`, `groupId`, `title`, `color` |
| `navigate` | Load URL, back/forward/reload | `page` (req), `action`, `url` |
| `snapshot` | Accessibility tree with [ref=eN] | `page` (req) |
| `diff` | Changes since last snapshot | `page` (req) |
| `act` | Click, type, fill, scroll, drag | `page`(req), `kind`(req), `ref`, `text`, `value`, `fields`, `key`, `x`, `y` |
| `download` | Click to trigger download | `page`(req), `ref`(req) |
| `upload` | Set file path on input[type=file] | `page`(req), `ref`(req), `file`, `files` |
| `read` | Extract content as markdown/text/links | `page`(req), `format`, `selector`, `viewportOnly` |
| `grep` | Search page text | `page`(req), `pattern`(req), `over`, `limit` |
| `screenshot` | Screenshot (JPEG default) | `page`(req), `format`, `quality`, `size`, `fullPage`, `annotate` |
| `pdf` | Print to PDF | `page`(req), `landscape`, `background` |
| `wait` | Wait for condition | `page`(req), `for`, `value`, `timeout` |
| `windows` | List/create/close/show/hide windows | `action`, `windowId`, `hidden`, `activate` |
| `evaluate` | Run JS in page context (CDP) | `page`(req), `code`(req), `timeout` |
| `run` | Run JS with browser SDK on server | `code`(req), `timeout` |

### Required params marked (req).

## BrowserClaw vs BrowserOS

| Feature | BrowserClaw | BrowserOS |
|---------|-------------|-----------|
| Product type | Agent-first browser | MCP proxy server |
| MCP port | 9010 | 9003 |
| Tools | 16 browser tools | 53 browser tools + 40+ app integrations |
| Server version | browseros-claw-server v0.0.7 | BrowserOS v0.0.79+ |
| License | AGPL-3.0 | Proprietary |
| Install location | `%LOCALAPPDATA%\BrowserClaw` | `%PROGRAMFILES%\BrowserOS` |
| Auto-start | claw-server daemon | browseros-server.exe |

## Pitfalls

- **Session expires if not used** — re-initialize if calls start returning "Server not initialized"
- **Navigation may timeout on slow sites** — increase `timeout` parameter or navigate to simpler pages first
- **BrowserClaw uses real profiles** — actions affect the user's actual browser state (cookies, sessions). Not a sandbox.
- **Need to launch BrowserClaw browser** for MCP endpoint to start. The claw-server (port 9210) auto-starts on install.
- **Port 9010 is occupied by chrome.exe** — only one BrowserClaw instance can listen at a time.
