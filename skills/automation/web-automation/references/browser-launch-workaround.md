# Browser Launch Workaround for Geo-Restricted Regions (Russia)

## Problem

Playwright CDN (cdn.playwright.dev) is geo-blocked in Russia (403 Access Denied), preventing automatic Chromium download.

```
Error: Download failed: server returned code 403 body '<?xml version='1.0' encoding='UTF-8'?><Error><Code>AccessDenied</Code><Message>Access denied.</Message><Details>We're sorry, but this service is not available in your location</Details></Error>'
```

## Solutions

### Solution 1: Use System Browser via Channel Parameter (Recommended)

```python
# Use installed Edge/Chrome via Playwright's channel parameter
self.browser = await self.playwright.chromium.launch(
    headless=self.config.headless,
    args=launch_args,
    channel="msedge",  # or "chrome" if Chrome installed
    # executable_path="D:\\Program Files (x86)\\Microsoft\\Edge Dev\\Application\\msedge.exe",  # explicit path
)
```

**Found on this system:**
- Edge Dev: `D:\\Program Files (x86)\\Microsoft\\Edge Dev\\Application\\msedge.exe`
- Chrome: Not installed by default

### Solution 2: Explicit Executable Path

```python
self.browser = await self.playwright.chromium.launch(
    headless=self.config.headless,
    args=launch_args,
    executable_path="D:\\Program Files (x86)\\Microsoft\\Edge Dev\\Application\\msedge.exe",
)
```

### Solution 3: HTTP Fallback via v2rayN Proxy (No Browser Needed)

Since Ozon/WB have mobile APIs, use `httpx` through v2rayN proxy:

```python
import httpx

async with httpx.AsyncClient(proxy="socks5://127.0.0.1:10806") as client:
    # Ozon API
    response = await client.get(
        "https://api.ozon.ru/composer-api.bx/page/json/v2",
        params={"url": f"/search/?text={query}&sort=price"}
    )
    
    # Wildberries API
    response = await client.get(
        "https://search.wb.ru/exactmatch/ru/common/v4/search",
        params={
            "query": query,
            "sort": "priceup",
            "page": 1,
            "curr": "rub"
        }
    )
```

## Browser Configuration for Geo-Restricted Regions

```python
config = BrowserConfig(
    headless=False,           # Visible browser for debugging
    proxy="socks5://127.0.0.1:10806",  # v2rayN proxy
    ghost_surfer=False,       # Ghost-surfer may also have CDN issues
    # Use system Edge via channel
    # channel="msedge",        # Uncomment if Edge installed
)
```

## Verified Working Setup (Russia)

| Component | Status | Details |
|-----------|--------|---------|
| v2rayN proxy | ✅ Working | socks5://127.0.0.1:10806 |
| Edge Dev | ✅ Found | `D:\\Program Files (x86)\\Microsoft\\Edge Dev\\Application\\msedge.exe` |
| Playwright + Edge channel | ✅ Works | No CDN download needed |
| v2rayN proxy for HTTP | ✅ Working | HTTP fallback mode |

## Auto-Detection in Code

The web_automation.py now auto-detects system browsers:

```python
system_browsers = [
    ("msedge", "D:\\Program Files (x86)\\Microsoft\\Edge Dev\\Application\\msedge.exe"),
    ("msedge", "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"),
    ("chrome", "D:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"),
    ("chrome", "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"),
    ("chrome", "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"),
]

for ch, path in system_browsers:
    if os.path.exists(path):
        executable_path = path
        channel = ch
        logger.info(f"Using system browser: {path}")
        break
```

Then uses `channel=ch` and `executable_path=path` in `chromium.launch()`.

## Notes

- Ghost-surfer also likely blocked by same CDN issues
- HTTP fallback via v2rayN proxy is the most reliable for marketplace scraping
- Browser mode works with Edge Dev for sites that don't block Russian IPs
- Always use v2rayN proxy for marketplace sites (Ozon, WB, Yandex Market)