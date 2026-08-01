---
name: ego-windows
description: |
  Windows analog of ego-lite: parallel browser Spaces, JS tool API for agents, Chrome profile inheritance.
  Uses existing Hermes stack: BrowserClaw MCP (localhost:9010), BrowserOS MCP (localhost:9003), 
  browser-harness (CDP 9222), ghost-surfer (Playwright stealth).
version: 1.0.0
category: automation
tags: [browser, automation, parallel, spaces, agent, cdp, playwright]
---

# ego-windows — Parallel Browser Spaces for Windows

**Analog of ego-lite for Windows** using existing Hermes browser automation stack.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      ego-windows Skill                          │
├─────────────────────────────────────────────────────────────────┤
│  Space Manager          │  JS Bridge           │  Engine Router │
│  (Playwright contexts)  │  (snapshot, click,   │  (choose best  │
│  + BrowserClaw tabs)    │   fill, wait,        │   engine per   │
│                         │   navigate, capture) │   task)        │
├─────────────────────────────────────────────────────────────────┤
│  BrowserClaw MCP (9010)  │  BrowserOS MCP (9003)  │  browser-harness (9222)  │  ghost-surfer  │
│  Standard automation     │  Extended: upload,     │  YOUR Chrome profile     │  Anti-detect   │
│  navigate, click, fill   │  JS eval, vision       │  cookies, logins         │  stealth       │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

```python
from skills.automation.ego_windows import EgoWindows

ego = EgoWindows()

# Create a Space for an agent
space = ego.create_space("agent-1")

# Agent runs JS in the space
result = space.run_js("""
  await snapshot()
  await click({ref: 'e12'})
  await fill({ref: 'e15', value: 'hello'})
  return await read({format: 'markdown'})
""")

# Clean up
ego.close_space(space.id)
```

## JS API (ego-browser compatible)

```javascript
// Page interaction
await navigate({url: "https://example.com"})
await snapshot()                    // Returns {text, refs}
await click({ref: "e12"})           // Click by ref from snapshot
await fill({ref: "e15", value: "text"})
await wait({for: "selector", value: ".loaded"})
await capture({fullPage: true})     // Screenshot

// Extraction
await read({format: "markdown"})    // Page content as markdown
await extract({selector: ".item"})  // Custom extraction

// Space management
await space.info()                  // Space metadata
```

## Engine Selection (Auto)

| Task Type | Engine |
|-----------|--------|
| Needs YOUR logins/cookies | browser-harness (CDP 9222) |
| Stealth/anti-detect needed | ghost-surfer (Playwright) |
| File upload / complex JS / vision | BrowserOS MCP (9003) |
| Standard scraping | BrowserClaw MCP (9010) |

## Installation

```bash
# 1. Playwright (for ghost-surfer & spaces)
pip install playwright && playwright install chromium

# 2. Verify MCP servers
curl http://localhost:9010/mcp   # BrowserClaw
curl http://localhost:9003/mcp   # BrowserOS

# 3. Start browser-harness (for YOUR Chrome)
cd /d/Portable_Soft/hermes/browser-harness
python -m src.browser_harness.daemon  # Connects to Chrome on 9222
```

## Files

- `scripts/space_manager.py` — Playwright contexts + BrowserClaw tab pool
- `scripts/ego_bridge.py` — JS API → MCP calls translation
- `scripts/ego_windows.py` — Main class `EgoWindows`
- `references/install.md` — This file