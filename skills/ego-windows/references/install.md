# Install ego-windows

**ego-windows** — Windows analog of ego-lite using existing Hermes browser stack.

## Prerequisites

```bash
# 1. Playwright (for ghost-surfer & spaces)
pip install playwright && playwright install chromium

# 2. httpx (for MCP calls)
pip install httpx

# 3. Verify MCP servers running
curl http://localhost:9010/mcp   # BrowserClaw
curl http://localhost:9003/mcp   # BrowserOS
```

## MCP Servers (Required)

### BrowserClaw (port 9010)
```bash
# Start BrowserClaw MCP server
# Config in ~/.hermes/config.yaml:
mcp:
  servers:
    browserclaw:
      type: http
      url: http://127.0.0.1:9010/mcp
```

### BrowserOS (port 9003)
```bash
# Config:
mcp:
  servers:
    browseros:
      type: http
      url: http://127.0.0.1:9003/mcp
```

### browser-harness (YOUR Chrome, CDP 9222)
```bash
# 1. Start Chrome with CDP:
chrome.exe --remote-debugging-port=9222 --user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data"

# 2. Start browser-harness daemon:
cd /d/Portable_Soft/hermes/browser-harness
python -m src.browser_harness.daemon
```

## Verify Installation

```bash
# Quick test
python -c "
import sys
sys.path.insert(0, 'skills/ego-windows')
from scripts.ego_windows import EgoWindows

ego = EgoWindows()
print('Engines:', list(ego.engine_endpoints.keys()))

space = ego.create_space('test', engine='browserclaw', chrome_profile=False)
print(f'Space created: {space.id} ({space.engine})')

ego.close_space(space.id)
print('✅ ego-windows ready')
"
```

## Usage

```python
from skills.ego_windows import EgoWindows

ego = EgoWindows()

# Create Space for an agent
space = ego.create_space(
    name="my-agent",
    engine="auto",        # auto-select: browser-harness (with profile) or browserclaw
    chrome_profile=True,  # inherit YOUR Chrome cookies/logins
    stealth=False         # True = ghost-surfer anti-detect
)

# Agent runs JS in the Space (ego-browser compatible API)
result = ego.run_js(space.id, """
  await navigate({url: 'https://example.com'})
  const snap = await snapshot()
  const btn = snap.refs.find(r => r.text.includes('Login'))
  await click({ref: btn.ref})
  return await read({format: 'markdown'})
""")

print(result)

# Cleanup when done
ego.close_space(space.id)
```

## Engine Selection Guide

| Need | Engine | MCP/Port |
|------|--------|----------|
| YOUR logins/cookies | browser-harness | CDP 9222 |
| Stealth/anti-detect | ghost-surfer | Playwright |
| File upload / complex JS / vision | browseros | 9003 |
| Standard scraping | browserclaw | 9010 |

## Troubleshooting

- **Playwright not found**: `pip install playwright && playwright install chromium`
- **MCP connection failed**: Check server running, ports 9010/9003/9222
- **Chrome profile not inherited**: Ensure Chrome started with `--remote-debugging-port=9222`
- **Permission errors**: Run terminal as Administrator if needed