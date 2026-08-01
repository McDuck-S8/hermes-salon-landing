# Marketplace Scraping Limitations — Ozon & Wildberries

Documented from session 2026-07-31. External service anti-bot protection blocks our environment.

## Summary

| Method | Ozon | Wildberries |
|--------|------|-------------|
| HTTP API | ❌ 403 Forbidden | ❌ 429 Too Many Requests |
| Browser (proxy) | ❌ Challenge page | ❌ Challenge page |
| Browser (direct) | ❌ Challenge page | ❌ Challenge page |

**Root cause**: Both Ozon and Wildberries employ aggressive anti-bot systems that detect:
- Datacenter proxy IPs (even via v2rayN)
- Browser fingerprints (Playwright/automation signatures)
- Missing residential IP reputation
- JavaScript challenge / CAPTCHA on first request

## Working Proxy

```bash
# v2rayN proxy works for curl
curl --socks5 127.0.0.1:10806 https://api.ipify.org
# Returns: 37.193.29.147 (proxy exit IP)
```

But browser automation fails because Ozon/WB fingerprint the browser context, not just the IP.

## What Works for Other Sites

The web-automation skill works correctly for sites without aggressive anti-bot protection:
- GitHub, GitLab, YouTube, Dzen, VC.ru
- Any site that doesn't use Cloudflare/Akamai/PerimeterX level protection

## Recommended Workarounds (Future)

| Approach | Effort | Success Probability |
|----------|--------|---------------------|
| Residential proxy pool | High | High |
| Playwright stealth +undetected-chromedriver | Medium | Medium |
| Official APIs (Ozon Seller API, WB API) | Medium | High (requires credentials) |
| Selenium + undetected-chromedriver | Medium | Medium |
| Human-in-the-loop (manual auth, then cookie reuse) | Low | High |

## Code Patterns That Work

The web-automation skill implements the correct fallback chain:

```python
# 1. Try HTTP API first (fast, no browser)
results = await bot.search_and_extract_http(query, site)

# 2. If empty/error, fallback to browser with human behavior
if not results:
    results = await bot.search_and_extract(query, site)  # Uses _human_like_search()
```

Human-like behavior implemented:
- `_human_like_search()`: Types query char-by-char (80ms delay), presses Enter
- `_human_like_scroll()`: Random scroll amounts (300-800px), random pauses (0.5-1.5s)
- System browser detection: Uses Edge Dev if available on system

## Verification Status

All components verified:
- ✅ Syntax OK
- ✅ Subagent Verifier: 7/7 checks
- ✅ Compliance Checker: 3/3 rules (Zero Trust, Passive Income, Iterative Attack)
- ✅ JSON configs valid (7 sites)

## Related Files

- `scripts/web_automation.py` — Main engine with HTTP + browser modes
- `scripts/config_loader.py` — Config loader
- `configs/ozon.json`, `configs/wb.json` — Marketplace selectors & eval scripts
- `.claude/skills/web-automation/SKILL.md` — Skill documentation