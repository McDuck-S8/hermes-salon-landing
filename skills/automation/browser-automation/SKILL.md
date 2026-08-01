---
name: browser-automation
description: Browser automation via BrowserClaw MCP server — navigate, click, fill forms, extract content, screenshot. Use for web scraping, testing, form submission, flight/hotel booking, any browser task.
version: 1.1.0
platforms: [linux, macos, windows]
environments: [browser]
metadata:
  hermes:
    tags: [browser, automation, mcp, browserclaw, scraping, testing]
  skill_updated: "2026-07-24"
  stale_since: "2026-06-03"
  stale_days: 1
  very_stale: false
  updated_by: "auto_patch_g009"
    related_skills: [mcp]
---

# Browser Automation with BrowserClaw MCP

## Overview

BrowserClaw provides a full browser (Chromium) controlled via MCP. The server runs at `http://127.0.0.1:9010/mcp` and exposes 16 tools for tabs, navigation, interaction, extraction, and screenshots.

## Setup

1. **Start BrowserClaw server** (if not running):
   ```bash
   # Usually runs as part of Hermes gateway or standalone
   npx @browserclaw/server --port 9010
   ```

2. **Add to Hermes config** (`config.yaml`):
   ```yaml
   mcp:
     servers:
       browserclaw:
         type: http
         url: http://127.0.0.1:9010/mcp
   ```

3. **Restart Hermes gateway** to pick up new MCP server:
   ```bash
   hermes gateway restart
   ```

4. **Verify connection**:
   ```bash
   hermes mcp list
   # Should show browserclaw with 16 tools ✓ enabled
   ```

## Core Workflow

### 1. Create a tab (MANDATORY - you only own tabs you create)
```python
mcp__browserclaw__tabs(action="new", url="https://example.com")
# Returns: {"page": 5, "url": "https://example.com", ...}
```

### 2. Snapshot the page (get ref IDs for elements)
```python
mcp__browserclaw__snapshot(page=5)
# Returns accessibility tree with [ref=e1], [ref=e2] labels
```

### 3. Act on elements using refs
```python
mcp__browserclaw__act(page=5, kind="click", ref="e23")
mcp__browserclaw__act(page=5, kind="fill", ref="e45", value="SFO")
mcp__browserclaw__act(page=5, kind="press", key="Enter")
```

### 4. Extract content
```python
mcp__browserclaw__read(page=5, format="markdown")
mcp__browserclaw__grep(page=5, pattern="price", over="content")
```

### 5. Screenshot (optional)
```python
mcp__browserclaw__screenshot(page=5, fullPage=True, annotate=True)
```

## Complete Example: Flight Search (Kayak)

```python
# 1. New tab
page = (await mcp__browserclaw__tabs(action="new", url="https://www.kayak.com/flights"))["page"]

# 2. Handle cookie consent
await mcp__browserclaw__snapshot(page=page)
await mcp__browserclaw__act(page=page, kind="click", ref="e6")  # "Accept all"

# 3. Fill origin
await mcp__browserclaw__snapshot(page=page)
await mcp__browserclaw__act(page=page, kind="fill", ref="e23", value="SFO")
await mcp__browserclaw__act(page=page, kind="press", key="Enter")

# 4. Fill destination
await mcp__browserclaw__snapshot(page=page)
await mcp__browserclaw__act(page=page, kind="fill", ref="e26", value="NYC")
await mcp__browserclaw__act(page=page, kind="press", key="Enter")

# 5. Select date (click calendar day)
await mcp__browserclaw__snapshot(page=page)
await mcp__browserclaw__act(page=page, kind="click", ref="e199")  # July 18

# 6. Search
await mcp__browserclaw__act(page=page, kind="click", ref="e30")

# 7. Wait for results
await mcp__browserclaw__wait(page=page, for="time", value=10000)

# 8. Extract results
await mcp__browserclaw__snapshot(page=page)
results = await mcp__browserclaw__read(page=page, format="markdown")
```

## Pitfalls & Gotchas

| Issue | Solution |
|-------|----------|
| **"page not owned by this agent"** | Always create tab with `tabs new` first. Never use user's existing tabs. |
| **Element refs stale after navigation** | Re-snapshot after every URL change or major DOM update. |
| **Cookie consent blocks interaction** | Handle it first: snapshot → find "Accept all" button → click. |
| **Kayak/Priceline redirect by IP** | Results reflect server IP location. Use VPN or accept non-local prices. |
| **Calendar date picker complex** | Use `grep` to find the day button ref, then click. |
| **Page loads slowly** | Use `wait` with `for="selector"` or `for="text"` instead of fixed time. |
| **Dropdown/combobox** | Fill expands it, then press Enter or click the option ref. |
| **Dialogs/alerts** | They appear in snapshot as `dialog` role — act on their buttons. |

## Tool Reference (16 tools)

| Tool | Purpose |
|------|---------|
| `tabs` | List, create, close tabs |
| `tab_groups` | Manage tab groups |
| `navigate` | Load URL, back, forward, reload |
| `snapshot` | Get accessibility tree with refs |
| `act` | Click, fill, type, press, hover, select, scroll, drag |
| `read` | Extract markdown/text/links |
| `grep` | Search page (AX tree or visible content) |
| `diff` | Show changes since last snapshot |
| `screenshot` | Capture PNG/JPEG/WebP |
| `pdf` | Save page as PDF |
| `evaluate` | Run JS in page context |
| `wait` | Wait for time/text/selector |
| `download` | Trigger file download |
| `upload` | Set file input |
| `windows` | Manage browser windows |

## Integration with Kanban

Use BrowserClaw for kanban tasks tagged `browser`:
- Web research → extract → save to KC
- Form submission → book flight, submit application
- Monitoring → screenshot + diff for change detection
- Testing → navigate, act, assert

## Debugging

```bash
# Check MCP server status
curl http://127.0.0.1:9010/mcp

# View gateway logs for MCP connection
hermes gateway logs

# List browserclaw tools
hermes mcp test browserclaw
```

## Multi-MCP Browser Automation: BrowserClaw + BrowserOS

This skill covers **both** MCP servers:

| Server | Port | Use Case |
|---|---|---|
| **BrowserClaw** | 9010 | General automation, 16 tools, tab management |
| **BrowserOS** | 9003 | 66+ tools, file upload, JS eval, vision fallback |

**When to use which:**
- **BrowserClaw** (default): Standard web automation, form filling, scraping
- **BrowserOS** (fallback/extended): File uploads, complex JS evaluation, vision analysis fallback, additional 50+ tools

### Common BrowserOS MCP Tools Reference

| Tool | Purpose | BrowserClaw Equivalent |
|------|---------|----------------------|
| `new_page` | Open URL in new tab | `tabs new` |
| `click` | Click element by ref | `act click` |
| `fill` | Type text into field | `act fill` |
| `upload_file` | Set file on input | `upload` |
| `evaluate_script` | Run JS in page | `evaluate` |
| `take_screenshot` | Screenshot page | `screenshot` |
| `take_snapshot` | Accessibility tree | `snapshot` |
| `take_enhanced_snapshot` | Rich accessibility tree (more detail) | `snapshot` (less detail) |
| `press_key` | Keyboard press | `act press` |
| `search_dom` | Find DOM nodes by query | — |
| `navigate_page` | Navigate/back/forward/reload | `navigate` |
| `list_pages` | List all tabs | `tabs list` |
| `get_active_page` | Current focused tab | — |
| `extract_content` | Extract text/HTML/attribute | `read` |

## Setup for Both Servers

```yaml
# ~/.hermes/config.yaml
mcp:
  servers:
    browserclaw:
      type: http
      url: http://127.0.0.1:9010/mcp
    browseros:
      type: http
      url: http://127.0.0.1:9003/mcp
```

Restart Hermes gateway after config change:
```bash
hermes gateway restart
```

Verify both:
```bash
hermes mcp list
# Should show both browserclaw (16 tools) and browseros (66 tools)
```

## Worker Patterns (Updated for BrowserOS)

### Pattern 1: CPA Network Scraping (AdCombo, CPAlead, Alfaleads) — BrowserOS
```python
# 1. New tab to offers page
page_result = await mcp__browseros__new_page(url="https://www.adcombo.com/offers")
page = page_result["page"]

# 2. Wait for load
await mcp__browseros__wait(page=page, for="time", value=3000)

# 3. Snapshot for refs
snapshot = await mcp__browseros__take_snapshot(page=page)

# 4. Click filters: GEO=IN, Vertical=Gambling
await mcp__browseros__click(page=page, ref=ref_geo_filter)
await mcp__browseros__click(page=page, ref=ref_gambling_vertical)

# 5. Extract offer cards via JS
offers = await mcp__browseros__evaluate_script(page=page, script="""
  return Array.from(document.querySelectorAll('.offer-card')).map(c => ({
    id: c.dataset.offerId,
    name: c.querySelector('.offer-name')?.textContent,
    payout: c.querySelector('.payout')?.textContent,
    cap: c.querySelector('.cap')?.textContent,
    flow: c.querySelector('.flow')?.textContent,
    lander: c.querySelector('.lander-url')?.href
  }))
""")
```

### Pattern 2: FB Ad Library / TikTok Creative Center — BrowserOS
```python
page = await mcp__browseros__new_page(url="https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=IN")
await mcp__browseros__wait(page=page, for="time", value=5000)

# Scroll to load more
await mcp__browseros__evaluate_script(page=page, script="window.scrollTo(0, document.body.scrollHeight)")
await mcp__browseros__wait(page=page, for="time", value=3000)

ads = await mcp__browseros__evaluate_script(page=page, script="""
  return Array.from(document.querySelectorAll('[data-testid="ad-card"]')).map(a => ({
    advertiser: a.querySelector('[data-testid="advertiser-name"]')?.textContent,
    cta: a.querySelector('[data-testid="cta-button"]')?.textContent,
    creative_url: a.querySelector('video, img')?.src,
    impressions: a.querySelector('[data-testid="impressions"]')?.textContent,
    lander: a.querySelector('a[href*="http"]')?.href
  }))
""")
```

### Pattern 3: Authenticated Session (User's Real Chrome via browser-harness)
```python
# BrowserOS doesn't have user's cookies. For authenticated scraping:
# Option A: Use browser-harness CDP bridge (port 9222) - separate skill
# Option B: Login manually in BrowserOS tab, then scrape

page = await mcp__browseros__new_page(url="https://www.adcombo.com/offers")
is_logged = await mcp__browseros__evaluate_script(page=page, script="!!document.querySelector('.user-menu')")

if not is_logged:
    # Manual login needed - capture screenshot for user
    await mcp__browseros__take_screenshot(page=page, fullPage=true)
    # Alert user to login, then continue
```

## Error Handling (Both Servers)

```python
async def safe_mcp_call(server: str, tool: str, args: dict, retries=2):
    """server: 'browserclaw' or 'browseros'"""
    for i in range(retries + 1):
        try:
            return await tool_call(f"mcp:{server}:{tool}", args)
        except Exception as e:
            if i == retries:
                raise
            await asyncio.sleep(2 ** i)  # exponential backoff
            # Re-snapshot if navigation occurred
            if "stale" in str(e).lower() or "detached" in str(e).lower():
                # Refresh page reference
                pass
```

## Verification Protocol

After worker returns, verify:
1. Output matches `acceptance` criteria in brief
2. Data has required fields (not empty)
3. Source URLs captured for traceability
4. Screenshots saved for visual verification

## Integration with Advisor-Orchestrator-Worker

**Worker brief must include:**
```json
{
  "tools_required": ["browser-automation"],
  "mcp_servers": ["browseros", "browserclaw"],
  "preferred_server": "browseros"
}
```

**Orchestrator validation before dispatch:**
- Check BrowserOS MCP is running: `curl http://localhost:9003/mcp`
- Check BrowserClaw MCP is running: `curl http://localhost:9010/mcp`
- Verify worker has `browser-automation` skill loaded
- Set timeout: 300s (not default 600s)

## References
- `references/ghost-surfer-browseros-testing.md`
- `references/kayak-flight-search.md`
- `references/vision-analyze-403-fallback.md`
- `references/browseros-tools.md` (NEW - full tool reference)
- `references/cpa-scraping-patterns.md` (NEW - CPA-specific patterns)
- `references/creative-intel-patterns.md` (NEW - creative intelligence patterns)