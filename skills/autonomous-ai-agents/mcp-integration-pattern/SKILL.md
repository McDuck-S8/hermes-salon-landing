---
name: mcp-integration-pattern
description: >
  Standardized pattern for integrating external MCP servers into Hermes agents.
  Covers: server config, tool discovery, authentication, fallback, and skill 
  wrappers that expose MCP tools as native Hermes skills.
license: Apache-2.0
metadata:
  author: "Hermes Agent"
  version: "1.0.0"
  source: "Adapted from awesome-llm-apps mcp_ai_agents + Hermes native MCP client"
self_improving: true
eval_schedule: "0 3 * * *"
eval_threshold: 0.85
gemini_model: "gemini-1.5-pro"
compatibility: >
  Works with Hermes native MCP client (config.yaml). Skills declare MCP 
  dependencies and auto-register tools at load time.
---

# MCP Integration Pattern — External Services as Native Skills

**One config → auto-discovered tools → wrapped as skills → used like any other.**

## The Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│  config.yaml                                                    │
│  mcp.servers:                                                   │
│    browserclaw:                                                 │
│      url: "http://localhost:3000/mcp"                          │
│      transport: "streamable_http"                               │
│    figma:                                                       │
│      url: "http://localhost:3001/mcp"                          │
│      transport: "streamable_http"                               │
│    vapi:                                                        │
│      command: "npx"                                             │
│      args: ["-y", "@vapi/mcp-server"]                          │
│      env: {VAPI_API_KEY: "${VAPI_API_KEY}"}                    │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Hermes Startup: auto-connect → discover tools → register      │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Skill Wrapper (e.g. browser-automation/SKILL.md)              │
│  - Declares: requires_mcp: ["browserclaw"]                     │
│  - Exposes: navigate, click, extract, screenshot               │
│  - Adds: domain logic, error handling, retries                 │
└─────────────────────────────────────────────────────────────────┘
```

## Server Categories for Arbitrage/Automation

| Server | Purpose | Key Tools | Auth |
|---|---|---|---|
| **BrowserClaw** | Headless browser, scraping, automation | navigate, click, extract, screenshot, evaluate | None (local) |
| **Figma MCP** | Design → code, component extraction | get_file, get_nodes, export_assets | Figma token |
| **Vapi** | Voice AI calls | create_call, list_calls, transcripts | Vapi API key |
| **Mobile MCP** | iOS/Android automation | tap, swipe, screenshot, install_app | USB/ADB |
| **Linear/Notion/GitHub** | Project mgmt, docs, code | create_issue, query, search | OAuth/PAT |
| **Supabase/Postgres** | Direct DB access | query, mutate, subscribe | Service role key |
| **Stripe/PayPal** | Payments, payouts | create_payment, list_payouts | Secret key |

## Skill Wrapper Template

```markdown
---
name: browser-automation
description: Browser automation via BrowserClaw MCP
requires_mcp: ["browserclaw"]
tools_exposed:
  - navigate_page
  - click_element
  - extract_content
  - take_screenshot
  - evaluate_script
---

# Browser Automation Skill

Wraps BrowserClaw MCP tools with domain logic for arbitrage tasks.

## Tools

### navigate_page(url, wait_for="networkidle")
Navigate and wait for page ready.

### extract_content(selector, attribute="textContent")
Extract text/HTML/attribute from elements.

### evaluate_script(script)
Run JS in page context (for SPA data extraction).

## Patterns

### Creative Scraping (FB Library, TikTok Creative Center)
```python
navigate_page("https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=IN")
# Scroll, extract ad cards, parse creative data
```

### Landing Page Analysis
```python
navigate_page(lander_url)
extract_content(".hero h1")  # headline
extract_content(".cta-button", "href")  # offer link
take_screenshot()  # visual record
```

### Offer Page Monitoring
```python
navigate_page(offer_url)
evaluate_script("""
  return {
    payout: document.querySelector('[data-payout]')?.dataset.payout,
    cap: document.querySelector('[data-cap]')?.dataset.cap,
    geo: document.querySelector('[data-geo]')?.dataset.geo
  }
""")
```

## Error Handling

```python
from hermes_tools import tool_call

async def safe_mcp_call(tool, args, retries=2):
    for i in range(retries + 1):
        try:
            return await tool_call(f"mcp:{server}:{tool}", args)
        except Exception as e:
            if i == retries:
                raise
            await asyncio.sleep(2 ** i)  # exponential backoff
```

## Config Management

```yaml
# ~/.hermes/config.yaml
mcp:
  servers:
    browserclaw:
      url: "http://localhost:3000/mcp"
      transport: "streamable_http"
      enabled: true
    figma:
      url: "http://localhost:3001/mcp"
      transport: "streamable_http"
      enabled: true
      env:
        FIGMA_TOKEN: "${FIGMA_TOKEN}"
```

## Declaring MCP Dependencies in Skills

```yaml
# SKILL.md frontmatter
requires_mcp: ["browserclaw", "figma"]
# OR for optional:
optional_mcp: ["vapi"]
```

At skill load time, Hermes checks:
1. Server configured in config.yaml
2. Server reachable (health check)
3. Tools discovered and registered
4. If required + missing → skill load fails with clear message
5. If optional + missing → skill loads with degraded mode warning

## Fallback Chain

```
MCP Tool Call
    │
    ├─► Primary: MCP server (fast, full features)
    │
    ├─► Fallback 1: Direct API (if available)
    │     e.g., BrowserClaw → Playwright direct
    │
    ├─► Fallback 2: Alternative MCP server
    │     e.g., Figma MCP → Figma REST API
    │
    └─► Fallback 3: Manual / degraded mode
          Return structured error with guidance
```

## Real Examples for Arbitrage

### BrowserClaw → Creative Spy
```python
# Skill: creative-intelligence
# Uses: browserclaw
# Flow: FB Library → TikTok CC → Native ad spy → extract creatives → store in KC
```

### Figma → Lander Generator
```python
# Skill: lander-from-figma
# Uses: figma
# Flow: Figma file → extract components → generate React/HTML lander → deploy to GH Pages
```

### Vapi → Call Center Automation
```python
# Skill: voice-lead-qualifier
# Uses: vapi
# Flow: Lead comes in → Vapi calls → qualifies → books appointment → updates CRM
```

### Supabase → Real-time Dashboard
```python
# Skill: live-pnl-dashboard
# Uses: supabase
# Flow: Subscribe to conversions table → update P&L in real-time → push to Telegram
```

## Testing MCP Integration

```bash
# 1. Check server health
curl http://localhost:3000/mcp/health

# 2. List discovered tools
hermes mcp tools --server browserclaw

# 3. Test tool call
hermes mcp call browserclaw navigate_page '{"url": "https://example.com"}'

# 4. Verify skill loads
hermes skill load browser-automation
```

## Security

- **Never** put secrets in config.yaml — use `${ENV_VAR}` substitution
- **Scope** MCP server permissions minimally (read-only where possible)
- **Audit** tool calls via Hermes audit log
- **Isolate** browsers per session (BrowserClaw does this)

## Files

```
mcp-integration-pattern/
├── SKILL.md
├── references/
│   ├── server-catalog.md      # Known good MCP servers for arbitrage
│   ├── tool-mapping.md        # MCP tool → Hermes skill tool mapping
│   └── fallback-strategies.md # Per-server fallback implementations
├── templates/
│   ├── skill-wrapper.md       # Template for new MCP skill wrappers
│   └── config-snippet.yaml    # config.yaml additions per server
└── scripts/
    └── verify_mcp.py          # Health check all configured servers
```