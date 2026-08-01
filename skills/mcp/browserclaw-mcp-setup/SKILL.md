---
name: browserclaw-mcp-setup
description: "Setup and usage guide for BrowserClaw MCP server at http://127.0.0.1:9010/mcp — free, open-source Chromium-based browser for AI agents with 16 automation tools."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [browserclaw, mcp, browser-automation, ai-agents]
    related_skills: [native-mcp]
---

# BrowserClaw MCP Setup

BrowserClaw is a free, open-source (AGPL-3.0) Chromium-based browser designed for AI agents. It provides **16 browser automation tools** through a single MCP connection.

## Server URL
```
http://127.0.0.1:9010/mcp
```

## Configuration (config.yaml)

```yaml
mcp_servers:
  browserclaw:
    type: http
    url: http://127.0.0.1:9010/mcp
    timeout: 180
    connect_timeout: 60
```

## Protocol Quirk (Critical)

BrowserClaw uses **session-based Streamable HTTP**. After `initialize`, the server returns `mcp-session-id` as an HTTP response header. **ALL subsequent requests must include this header**, or the server returns `400 Server not initialized`.

The native-mcp client handles this automatically when configured correctly.

## Available Tools (16)

| Tool | Description |
|------|-------------|
| `mcp_browserclaw_tabs` | Manage browser tabs (list, new, close, active) |
| `mcp_browserclaw_navigate` | Navigate a page (load URL, back, forward, reload) |
| `mcp_browserclaw_snapshot` | Capture page as accessibility tree with refs |
| `mcp_browserclaw_act` | Act on page (click, type, fill, press, hover, select, scroll, drag) |
| `mcp_browserclaw_screenshot` | Capture screenshot (JPEG/PNG/WebP, annotated optional) |
| `mcp_browserclaw_read` | Extract page content as markdown/text/links |
| `mcp_browserclaw_evaluate` | Evaluate JavaScript in page context via CDP |
| `mcp_browserclaw_run` | Run multi-step JS against browser SDK |
| `mcp_browserclaw_diff` | Show what changed since last snapshot |
| `mcp_browserclaw_grep` | Search page (accessibility tree or visible text) |
| `mcp_browserclaw_download` | Trigger file download via element click |
| `mcp_browserclaw_pdf` | Print page to PDF |
| `mcp_browserclaw_upload` | Upload file to `<input type="file">` |
| `mcp_browserclaw_wait` | Wait for text, selector, or time |
| `mcp_browserclaw_tab_groups` | Manage tab groups |
| `mcp_browserclaw_windows` | Manage browser windows |

## Usage Pattern

```python
# 1. Open new tab
page = mcp_browserclaw_tabs(action="new", url="https://example.com")

# 2. Navigate
mcp_browserclaw_navigate(page=page, action="url", url="https://target-site.com")

# 3. Snapshot to get refs
snap = mcp_browserclaw_snapshot(page=page)

# 4. Act using refs from snapshot
mcp_browserclaw_act(page=page, kind="fill", ref="e12", value="search term")

# 5. Extract content
content = mcp_browserclaw_read(page=page, format="markdown")
```

## Quick Test

```bash
# Verify server is running
curl -H "Accept: application/json, text/event-stream" \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' \
     http://127.0.0.1:9010/mcp
```

Expected: JSON-RPC response with `serverInfo.name = "browseros-claw-server"`

## Common Issues

| Problem | Solution |
|---------|----------|
| `400 Server not initialized` | Client must send `mcp-session-id` header on all requests after initialize |
| `Not Acceptable: Client must accept text/event-stream` | Add `Accept: application/json, text/event-stream` header |
| Tools not appearing | Restart Hermes after adding to config.yaml |
| Timeout on navigation | Increase `timeout: 180` in config |

## References

- [BrowserClaw Docs](https://docs.browseros.com/browserclaw)
- [BrowserClaw GitHub](https://github.com/browserclaw/browserclaw)
- [MCP Spec](https://modelcontextprotocol.io/specification)
- `native-mcp` skill for general MCP configuration

## Verified Working

- Server: `browseros-claw-server` v0.0.7
- Protocol: 2024-11-05
- Transport: HTTP/StreamableHTTP (session-based)
- Tools discovered: 16
- Tested with: Hermes Agent native-mcp client