# Telegram API Proxy Configuration

## Problem
Telegram API (`api.telegram.org`) is blocked in Russia/Crimea and requires proxy access.

## V2RayN Ports (verified 2026-06-27)
- HTTP proxy: `http://127.0.0.1:10809` ✓ WORKING
- SOCKS5: `127.0.0.1:10806` — UNRELIABLE (connections time out)
- Mixed: `127.0.0.1:10807` — for Puppeteer/Chromium

## curl Test
```bash
# Direct (FAILS - times out):
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 https://api.telegram.org

# Via HTTP proxy (WORKS - returns 302):
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --proxy http://127.0.0.1:10809 https://api.telegram.org
```

## Status Codes
- `302` = SUCCESS (redirect to login page = API reachable)
- `200` = SUCCESS
- `401` = SUCCESS (unauthorized but reachable)
- `404` = SUCCESS (not found but reachable)
- `000` or timeout = FAILURE (proxy down or blocked)

## Integration with Procedural Executor
In `scripts/procedural_executor.py`, Telegram API check must use:
```python
subprocess.run([
    "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
    "--connect-timeout", "5",
    "--proxy", "http://127.0.0.1:10809",
    "https://api.telegram.org"
])
```

## Common Mistake
Checking Telegram API WITHOUT proxy = guaranteed timeout. Always add `--proxy http://127.0.0.1:10809`.
