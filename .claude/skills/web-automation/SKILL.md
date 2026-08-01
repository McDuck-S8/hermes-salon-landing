---
name: web-automation
description: "Browser automation for web interfaces using Playwright + Ghost-surfer. Anti-detect, proxy support (v2rayN), selectors config for GitHub, GitLab, YouTube, Dzen, VC.ru."
trigger: "When user asks to automate web tasks: create repo, upload file, publish article, upload video, scrape data, login, interact with UI."
usage: web-automation
argument-hint: "[craft|execute|scrape|test] [target_site] [action]"
allowed-tools:
  - Bash(npx playwright *)
  - Bash(python scripts/web_automation.py *)
  - Read(*)
  - Write(*)
  - Glob(*)
---

# Web Automation — Browser Automation Skill

Playwright-based browser automation with Ghost-surfer anti-detect integration, v2rayN proxy support, and site-specific selector configs.

## Architecture

```
web-automation/
├── SKILL.md                    # This file
├── scripts/
│   ├── web_automation.py      # Main engine: browser init, actions, logging
│   ├── config_loader.py       # Site config loader
├── configs/                   # Site-specific selectors & steps
│   ├── github.json
│   ├── gitlab.json
│   ├── youtube.json
│   ├── dzen.json
│   ├── vc_ru.json
└── references/
    └── site_structure.md      # General principles
```

## Quick Start

```bash
# Test: create GitHub repo (requires auth)
python scripts/web_automation.py --site github --action create_repo --params '{"name":"test-repo","private":false}'

# Scrape: get article from VC.ru
python scripts/web_automation.py --site vc_ru --action scrape_article --params '{"url":"https://vc.ru/..."}'

# Test browser launch
python scripts/web_automation.py --test-browser
```

## Core Engine: web_automation.py

### Browser Initialization
```python
from web_automation import BrowserAutomation

async with BrowserAutomation(proxy="socks5://127.0.0.1:10806") as bot:
    await bot.goto("https://github.com")
    await bot.click('button[data-testid="new-repo"]')
    await bot.fill('input[name="repository[name]"]', "my-repo")
    await bot.click('button[type="submit"]')
```

### Available Actions
| Action | Description |
|--------|-------------|
| `goto(url)` | Navigate to URL |
| `click(selector)` | Click element |
| `fill(selector, value)` | Fill input |
| `type(selector, text)` | Type with delay |
| `select(selector, value)` | Select dropdown |
| `wait(selector, timeout)` | Wait for element |
| `screenshot(path)` | Take screenshot |
| `scroll(direction)` | Scroll page |
| `evaluate(js)` | Execute JS |
| `cookies()` | Get/set cookies |
| `storage_state(path)` | Save auth state |

### Proxy & Anti-Detect
```python
BrowserAutomation(
    proxy="socks5://127.0.0.1:10806",  # v2rayN
    headless=False,
    ghost_surfer=True,  # Use Ghost-surfer if available
    stealth=True,       # Playwright stealth mode fallback
    user_agent="custom",  # Random UA
)
```

## Config Loader

```python
from config_loader import load_site_config

config = load_site_config("github")
selector = config["selectors"]["new_repo_button"]
steps = config["steps"]["create_repo"]
```

## Site Configs

Each site config in `configs/*.json`:
```json
{
  "base_url": "https://github.com",
  "login_required": true,
  "auth_type": "cookie",
  "selectors": { "new_repo_button": "..." },
  "steps": {
    "create_repo": [
      { "action": "goto", "url": "/new" },
      { "action": "fill", "selector": "...", "param": "name" },
      { "action": "click", "selector": "..." }
    ]
  }
}
```

## Supported Sites

| Site | Config | Actions |
|------|--------|---------|
| GitHub | `github.json` | create_repo, create_issue, create_pr, upload_file, release |
| GitLab | `gitlab.json` | create_project, merge_request, pipeline |
| YouTube | `youtube.json` | upload_video, edit_metadata, schedule |
| Dzen | `dzen.json` | publish_article, edit_post |
| VC.ru | `vc_ru.json` | publish_article, comment |

## Ghost-surfer Integration

```python
# Auto-detect Ghost-surfer
from web_automation import detect_ghost_surfer

if detect_ghost_surfer():
    # Use Ghost-surfer browser
    browser = await launch_ghost_surfer(proxy="socks5://127.0.0.1:10806")
else:
    # Fallback: Playwright stealth
    browser = await launch_playwright_stealth(proxy="socks5://127.0.0.1:10806")
```

## Anti-Detect Features

| Feature | Playwright | Ghost-surfer |
|---------|------------|--------------|
| Canvas fingerprint | ✅ | ✅ |
| WebGL fingerprint | ✅ | ✅ |
| Audio fingerprint | ✅ | ✅ |
| Font enumeration | ✅ | ✅ |
| Navigator props | ✅ | ✅ |
| Proxy rotation | ✅ | ✅ |
| Behavior simulation | ✅ | ✅ |

## Logging

```python
# All actions logged to JSONL
{"timestamp": "2026-07-31T10:00:00", "action": "click", "selector": "...", "success": true, "duration_ms": 150}
```

## Verification

```bash
# Verify skill
python scripts/subagent_verifier.py .claude/skills/web-automation/SKILL.md --strict

# Compliance check
python scripts/compliance_checker.py --check
```

## Core Mental Models

1. **Selector-first** — All interactions via config, never hardcoded
2. **Config-driven** — New sites = new JSON, no code changes
3. **Auth isolation** — Per-site cookie storage, no cross-contamination
4. **Graceful degradation** — Ghost-surfer → Playwright stealth → basic Playwright
5. **Observability** — Every action logged, retryable, auditable

## Key Frameworks & Decision Rules

| Framework | Purpose | When to Apply |
|-----------|---------|---------------|
| **Selector-first** | All interactions via config, never hardcoded | Every interaction |
| **Config-driven** | New sites = new JSON, no code changes | New site / action |
| **Auth isolation** | Per-site cookie storage, no cross-contamination | Every site |
| **Graceful degradation** | Ghost-surfer → Playwright stealth → basic Playwright | Browser init |
| **Observability** | Every action logged, retryable, auditable | Every action |

## Topic Index

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Core Engine](#core-engine-web_automationpy)
- [Config Loader](#config-loader)
- [Site Configs](#site-configs)
- [Supported Sites](#supported-sites)
- [Ghost-surfer Integration](#ghost-surfer-integration)
- [Anti-Detect Features](#anti-detect-features)
- [Logging](#logging)
- [Verification](#verification)
- [Core Mental Models](#core-mental-models)
- [Key Frameworks & Decision Rules](#key-frameworks--decision-rules)
- [Topic Index](#topic-index)

## Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Hardcode selectors | Use config JSON |
| Share cookies across sites | Per-site storage |
| Ignore proxy failures | Retry with fallback |
| Skip wait states | Wait for selectors |
| Single browser instance | Context per task |

---

**Version**: 1.0  
**Created**: 2026-07-31  
**Author**: Hermes Agent