# v2rayN Proxy Configuration for Puppeteer

## Ports (typical v2rayN defaults)
- **10806**: SOCKS5 proxy
- **10807**: HTTP mixed proxy (HTTP + SOCKS5 on same port)

## What Works
- `curl --proxy http://127.0.0.1:10807 https://chat.qwen.ai` → OK
- `curl --proxy socks5://127.0.0.1:10806 https://chat.qwen.ai` → OK
- System apps (browsers, curl) respect v2rayN transparent/system proxy

## What Doesn't Work
- Puppeteer `--proxy-server=socks5://127.0.0.1:10806` → ERR_EMPTY_RESPONSE
- Puppeteer `--proxy-server=http://127.0.0.1:10807` → ERR_CONNECTION_CLOSED
- The issue: Chromium's proxy implementation doesn't play well with v2rayN's proxy ports for HTTPS/TLS connections

## Why
Puppeteer's Chromium bypasses OS proxy settings. The `--proxy-server` flag forces Chromium to use a specific proxy, but v2rayN's proxy ports may not handle Chromium's TLS fingerprint or CONNECT method the same way curl does. This is a known Chromium + v2rayN interaction issue.

## Workarounds
1. **TUN mode** (best): Enable v2rayN's TUN/transparent proxy mode — all traffic routes through v2rayN at network level, Chromium doesn't need `--proxy-server`
2. **System proxy**: Set v2rayN to "System Proxy" mode, but Puppeteer ignores this
3. **Environment proxy**: Set `HTTP_PROXY`/`HTTPS_PROXY` env vars — some HTTP clients honor these, Puppeteer does not
4. **Alternative proxy**: Use a different proxy tool (Clash, sing-box) that has better Chromium compatibility

## Detection
Test proxy with curl first:
```bash
curl -s --proxy http://127.0.0.1:10807 https://chat.qwen.ai | head -5
```
If curl works but Puppeteer doesn't → Chromium-v2rayN interaction issue, not a network problem.

## FreeQwenApi Specific
- browser.js adds `--proxy-server` to Chromium args
- Health endpoint works without browser (no proxy needed for health check)
- Chat completions need browser → need proxy → v2rayN TUN mode recommended
