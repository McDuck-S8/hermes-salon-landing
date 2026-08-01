# BrowserOS MCP Setup — Working Configuration (2026-07-22)

## Verified Working Setup

**Server**: BrowserOS MCP (built-in, no npm package needed)
**Port**: 9003
**Transport**: Streamable HTTP
**Tools Available**: 66 browser automation tools

## Config ( ~/.hermes/config.yaml )

```yaml
mcp_servers:
  browseros:
    type: http
    url: http://127.0.0.1:9003/mcp
```

## Starting the Server

```bash
# BrowserOS must be running with MCP enabled
# Settings → BrowserOS as MCP → Enable
# Or via CLI if available
```

## Python Client Usage

```python
import asyncio
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

async def test_browseros():
    async with streamablehttp_client('http://127.0.0.1:9003/mcp') as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f'Tools: {len(tools.tools)}')
            # navigate_page, click_element, take_snapshot, evaluate_script, etc.
```

## Key Tools for Arbitrage

| Tool | Use Case |
|---|---|
| `navigate_page` | Open FB Ad Library, TikTok Creative Center, offer pages |
| `click_element` | Click through pagination, filter dropdowns |
| `take_snapshot` | Get accessibility tree for extraction |
| `evaluate_script` | Run JS to extract SPA data (React/Vue state) |
| `take_screenshot` | Visual verification of landers/creatives |
| `new_hidden_page` | Background scraping without UI interference |

## Pitfalls

1. **POST /mcp returns "Service Unavailable"** — GET /mcp works (health check), but JSON-RPC requires proper initialization sequence. Use `streamablehttp_client` from MCP SDK.
2. **No npm package `@browseros/mcp-server`** — BrowserOS MCP is built into the BrowserOS app, not a separate npm package.
3. **Port 9010 (browserclaw) different from 9003 (browseros)** — BrowserClaw is separate browser; BrowserOS is the AI browser with built-in MCP.
4. **Must call `session.initialize()`** before `list_tools()` or `call_tool()`.

## Verified Working Tools (sample)

- `navigate_page` — Navigate to URL
- `click_element` — Click by selector/ref
- `take_snapshot` — Accessibility tree
- `take_enhanced_snapshot` — Detailed tree with structure
- `evaluate_script` — Execute JS in page context
- `take_screenshot` — PNG screenshot
- `new_page` / `new_hidden_page` — Tab management
- `get_active_page` — Current focused tab
- `list_pages` — All open tabs
- `close_page` — Close tab