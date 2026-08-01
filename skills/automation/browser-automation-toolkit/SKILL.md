---
name: browser-automation-toolkit
description: "Unified browser automation toolkit for Hermes: browser-automation + browser-patterns + cpa-browser-scraper + ghost-surfer + browserclaw-mcp-setup + browseros + browser-harness. One skill to load, all browser engines at hand."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [browser, automation, cdp, playwright, cpa, scraping, ghost-surfer, mcp]
    related_skills: [browser-automation, browser-patterns, cpa-browser-scraper, ghost-surfer, browserclaw-mcp-setup, browseros, browser-harness]
  skill_updated: "2026-07-24"
  created_by: "auto_patch_g007"
  component_skills:
    - browser-automation
    - browser-patterns
    - cpa-browser-scraper
    - ghost-surfer
    - browserclaw-mcp-setup
    - browseros
    - browser-harness
    - ego-windows
---

# Browser Automation Toolkit — Unified Interface

**One skill to load. All browser automation engines. Zero context switching.**

This meta-skill wraps all core browser automation skills into a single loadable unit with a unified workflow interface.

## Quick Start

```python
# Load once, get all engines
from hermes_tools import skill_view
skill_view("automation/browser-automation-toolkit")

# Now you have:
# - browser-automation (BrowserClaw MCP: 16 tools)
# - browser-patterns (auto-generated from KC)
# - cpa-browser-scraper (YOUR logged-in Chrome via CDP 9222)
# - ghost-surfer (anti-detect: fingerprint, proxy, stealth)
# - browserclaw-mcp-setup (MCP server config)
# - browseros (66+ tools, file upload, JS eval, vision)
# - browser-harness (CDP daemon for YOUR Chrome)
```

## Component Skills Map

| Skill | Server/Port | Purpose | When to Use |
|-------|-------------|---------|-------------|
| **browser-automation** | BrowserClaw MCP 9010 | General automation: navigate, click, fill, extract, screenshot | Standard web automation, form filling, scraping |
| **browser-patterns** | Auto-generated | 35 KC patterns for browser tasks | Quick reference for common patterns |
| **cpa-browser-scraper** | browser-harness (CDP 9222) | CPA intelligence: YOUR logged-in Chrome | AdCombo, CPAlead, FB Library, TikTok CC, Google Maps |
| **ghost-surfer** | Playwright + stealth | Anti-detect: fingerprint, proxy rotation, evasion | When sites block automation |
| **browserclaw-mcp-setup** | BrowserClaw MCP 9010 | MCP server config + tool reference | Initial setup, troubleshooting |
| **browseros** | BrowserOS MCP 9003 | 66+ tools, file upload, JS eval, vision | Extended: upload, complex JS, vision fallback |
| **browser-harness** | CDP daemon | Connects to YOUR Chrome (port 9222) | Authenticated scraping, YOUR cookies |

## Architecture Decision Matrix

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        WHICH ENGINE?                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Need auth (cookies/logins)?          → browser-harness (YOUR Chrome)   │
│  Need stealth/anti-detect?            → ghost-surfer                    │
│  Need file upload / complex JS?       → browseros                       │
│  Need vision analysis fallback?       → browseros                       │
│  Standard automation (no auth)?       → browser-automation (BrowserClaw)│
│  CPA/arbitrage intelligence?          → cpa-browser-scraper             │
│  Quick pattern reference?             → browser-patterns                │
│                                                                          │
│  MULTI-ENGINE WORKFLOW:                                                    │
│  1. ghost-surfer → stealth landing                                        │
│  2. browseros → complex interaction / upload                              │
│  3. browser-harness → authenticated actions                               │
│  4. browser-automation → standard extraction                              │
└─────────────────────────────────────────────────────────────────────────┘
```

## Unified Browser Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. RECON (browser-patterns + ghost-surfer)                      │
│    • Check patterns for target site                             │
│    • Stealth probe: fingerprint, headers, TLS                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. CHOOSE ENGINE                                                │
│                                                                  │
│    Authenticated (CPA, social, email)?                          │
│      → browser-harness (YOUR Chrome, CDP 9222)                  │
│                                                                  │
│    Anonymous + stealth needed?                                  │
│      → ghost-surfer (Playwright + stealth)                      │
│                                                                  │
│    Standard scraping (no auth)?                                 │
│      → browser-automation (BrowserClaw MCP 9010)                │
│                                                                  │
│    Need upload / complex JS / vision?                           │
│      → browseros (MCP 9003, 66+ tools)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. EXECUTE (engine-specific patterns)                           │
│                                                                  │
│    BrowserClaw (16 tools):                                      │
│      tabs new → navigate → snapshot → act → read → diff         │
│                                                                  │
│    BrowserOS (66 tools):                                        │
│      new_page → click → fill → upload_file → evaluate_script   │
│      → take_screenshot → extract_content → search_dom           │
│                                                                  │
│    Browser-harness (YOUR Chrome):                               │
│      goto_url → js() → capture_screenshot → wait_for_load       │
│                                                                  │
│    Ghost-surfer (Playwright):                                   │
│      chromium.launch(stealth) → context → page → anti-detect    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. EXTRACT & STORE                                              │
│    • read/extract_content → markdown/JSON                       │
│    • on_task_complete() → Knowledge Cube                        │
│    • Screenshots/PDFs for evidence                              │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Commands Reference

### BrowserClaw (Standard Automation)
```bash
# Check MCP status
curl http://127.0.0.1:9010/mcp

# List tabs
hermes mcp call browserclaw:tabs '{"action": "list"}'

# Create tab & navigate
hermes mcp call browserclaw:tabs '{"action": "new", "url": "https://example.com"}'
hermes mcp call browserclaw:navigate '{"page": 1, "action": "url", "url": "https://example.com"}'

# Snapshot → Act → Read
hermes mcp call browserclaw:snapshot '{"page": 1}'
hermes mcp call browserclaw:act '{"page": 1, "kind": "click", "ref": "e12"}'
hermes mcp call browserclaw:read '{"page": 1, "format": "markdown"}'
```

### BrowserOS (Extended)
```bash
# Check MCP status
curl http://127.0.0.1:9003/mcp

# New page with extended tools
hermes mcp call browseros:new_page '{"url": "https://example.com"}'

# File upload
hermes mcp call browseros:upload_file '{"page": 1, "file": "/path/to/file.png"}'

# Complex JS evaluation
hermes mcp call browseros:evaluate_script '{"page": 1, "script": "return document.querySelectorAll('a').length"}'

# Vision fallback
hermes mcp call browseros:take_screenshot '{"page": 1, "fullPage": true}'
```

### Browser-Harness (YOUR Chrome)
```bash
# Start daemon (connects to YOUR Chrome on 9222)
cd /d/Portable_Soft/hermes/browser-harness
python -m src.browser_harness.daemon

# Test connection
browser-harness <<<'print(page_info())'

# Navigate & extract
browser-harness <<<'
goto_url("https://www.adcombo.com/offers")
wait_for_load()
offers = js("""
  return Array.from(document.querySelectorAll('.offer-card')).map(c => ({
    id: c.dataset.offerId,
    name: c.querySelector('.offer-name')?.textContent,
    payout: c.querySelector('.payout')?.textContent
  }))
""")
print(offers)
'
```

### Ghost-Surfer (Anti-Detect)
```python
from skills.automation.ghost_surfer import GhostSurfer

surfer = GhostSurfer()
page = surfer.new_page(stealth=True, proxy="socks5://user:pass@host:port")

# Anti-detect built-in:
# - Canvas fingerprint noise
# - WebGL vendor spoofing
# - Navigator properties (webdriver=false, languages, platform)
# - TLS fingerprint (JA3) matching Chrome
# - Mouse movement humanization
# - Request header ordering

page.goto("https://target-site.com")
# ... extract
```

### CPA Browser Scraper (Authenticated)
```python
from skills.automation.cpa_browser_scraper import CPAOfferScanner, CreativeScanner

# CPA Networks
scanner = CPAOfferScanner()
offers = scanner.scan_network(
    network="adcombo",      # adcombo, cpalead, alfaleads, cpatrend
    geo="IN",
    verticals=["gambling", "dating"],
    min_payout=3.0,
    min_cap=1000
)

# Creative Intelligence
creative = CreativeScanner()
fb_ads = creative.scan_fb_library(query="cricket betting India", country="IN")
tt_ads = creative.scan_tiktok_cc(region="IN", category="gaming")
```

## Configuration (Required)

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

platforms:
  webhook:
    enabled: true
    extra:
      host: "0.0.0.0"
      port: 8644
```

```bash
# Start both MCP servers
hermes gateway run  # or systemctl --user start hermes-gateway

# Start browser-harness daemon
cd /d/Portable_Soft/hermes/browser-harness
python -m src.browser_harness.daemon
```

## Anti-Patterns (from 96 browser entries, 57 failures = 59% failure rate)

| Anti-Pattern | Guard |
|--------------|-------|
| Using wrong engine for auth | **Decision matrix**: auth → browser-harness |
| No stealth on protected sites | **ghost-surfer** mandatory for Cloudflare/Akamai |
| Single engine for all tasks | **Multi-engine workflow**: recon → choose → execute |
| Element refs stale | **Re-snapshot after EVERY navigation** |
| No error handling | **safe_mcp_call** with retries + backoff |
| Cookie/session not persisted | **browser-harness** uses YOUR Chrome profile |
| Vision fallback missing | **browseros** has vision_analyze tool |

## Verification Checklist

After using this toolkit:
- [ ] Correct engine chosen per decision matrix
- [ ] MCP servers running (BrowserClaw 9010, BrowserOS 9003)
- [ ] browser-harness daemon connected to YOUR Chrome (9222)
- [ ] Re-snapshot after every navigation
- [ ] Data extracted via read/extract_content
- [ ] Screenshots/PDFs saved for evidence
- [ ] on_task_complete() logged to KC with tags

---

**Origin:** g-007 Unlock: browser (57 entries, 57 failures)
**Created:** 2026-07-24 via auto_patch_g007
**Source:** Knowledge Cube domain `browser` + all 7 component skills