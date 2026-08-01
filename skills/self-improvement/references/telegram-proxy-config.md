# Telegram Proxy Configuration

Configure a proxy for Hermes Agent's Telegram gateway when `api.telegram.org` is blocked.

## Config Key

```yaml
telegram:
  proxy_url: "http://127.0.0.1:10806"
```

Set via CLI:
```bash
hermes config set telegram.proxy_url http://127.0.0.1:10806
```

Alternatively, set `TELEGRAM_PROXY` in `.env`:
```env
TELEGRAM_PROXY=http://127.0.0.1:10806
```

Also respects `HTTPS_PROXY`, `HTTP_PROXY`, `ALL_PROXY` as fallback.

## Supported Schemes

- `http://` — HTTP proxy
- `https://` — HTTPS proxy
- `socks5://` — SOCKS5 proxy

## Required Packages

```bash
uv pip install pysocks aiohttp-socks
```

- `pysocks` — Python SOCKS client (needed for SOCKS5 proxy)
- `aiohttp-socks` — SOCKS proxy support for aiohttp (used by gateway's Telegram adapter)

## Verification

```bash
# Test proxy connectivity
curl -x http://127.0.0.1:10806 -s --connect-timeout 10 https://api.telegram.org/bot

# Expected: {"ok":false,"error_code":404,"description":"Not Found"}
# The 404 confirms the proxy forwards to Telegram API correctly
```

With bot token:
```bash
curl -x http://127.0.0.1:10806 -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"
```

## Known Pitfalls

- **SOCKS5 port may be inactive** even if HTTP port works — depends on v2rayn/proxy configuration. Test both.
- **Python urllib may timeout** through proxy while curl works — try `requests` library or `curl` for testing.
- Gateway uses aiohttp, not urllib — `aiohttp-socks` package is essential for SOCKS5 support in gateway mode.
