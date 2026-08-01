# httpx SOCKS5 Proxy — Gateway vs Standalone (2026-06-27, updated)

## Environment
- Proxy: v2rayN/xray SOCKS5 on port 10806 (`D:\\v2rayN-windows-64\\bin\\xray\\xray.exe`)
- Gateway adapter: `hermes-agent/plugins/platforms/telegram/adapter.py`
- HTTPXRequest: python-telegram-bot v22 `telegram.request.HTTPXRequest`
- httpx 0.28.1, httpcore 1.0.9, httpx_socks (installed in venv)

## The Problem

Gateway consistently fails to connect to Telegram API through SOCKS5 proxy. All 30 reconnect attempts fail. Standalone httpx scripts work fine with the same proxy.

## What Works vs What Fails

### Works (standalone, fresh client each time):
- `curl -x socks5://` → 4/5
- `requests` library → 200 OK
- Python raw sockets → TLS handshake OK (verified manually)
- `httpx.AsyncClient(proxy='socks5://...')` → 5/5
- `httpx_socks.AsyncProxyTransport` → 5/5
- **`httpx.AsyncClient(proxy='http://127.0.0.1:10807')` (bridge)** → 5/5

### Fails (gateway, long-lived client):
- ALL SOCKS5 approaches fail: `proxy=` kwarg, `AsyncProxyTransport`, etc.
- Error: `httpx.RemoteProtocolError: Server disconnected without sending a response`
- Happens on FIRST request (`set_my_commands` / `delete_webhook`), not just long-polling
- The httpcore `socks_proxy.py` appears in traceback regardless of approach

### CRITICAL: "proxy= kwarg" does NOT fix it in gateway
Previous conclusion that `proxy=socks5://` kwarg works in gateway is **WRONG**. The traceback from the gateway shows `httpcore/_async/socks_proxy.py:299` being called — this is the httpcore built-in SOCKS transport, not httpx_socks. It fails in gateway context every time.

## Root Cause

httpcore's built-in SOCKS5 proxy transport (`socksio` library) has an issue with long-lived async processes in the gateway context. The TLS handshake through SOCKS5 fails or the server drops the connection. The exact mechanism is not fully understood, but:

1. Standalone test creates a FRESH httpx.AsyncClient per test → works
2. Gateway creates ONE httpx.AsyncClient that's reused for many requests → fails
3. Even after `_drain_polling_connections()` (shutdown + initialize), the problem persists
4. The issue is NOT in connection pool staleness — it's in how httpcore establishes the SOCKS tunnel

## Working Solution: HTTP→SOCKS5 Bridge

Instead of fighting httpcore's SOCKS implementation, bypass it entirely with a local HTTP CONNECT proxy that forwards through SOCKS5:

### Bridge script: `scripts/http_to_socks_proxy.py`

Raw-socket-based bridge (not asyncio streams — for TLS transparency):
- Listens on `http://127.0.0.1:10807`
- Forwards HTTP CONNECT tunnels through `socks5://127.0.0.1:10806`
- Uses threading + select for bidirectional relay
- TLS passthrough works because it's transparent TCP forwarding

### Config change:
```yaml
telegram:
  proxy_url: "http://127.0.0.1:10807"  # NOT socks5://
```

### Why this works:
- httpx with `proxy=http://` uses `httpcore.AsyncHTTPProxy` which is battle-tested
- The bridge handles the SOCKS5 part via raw sockets (proven reliable)
- HTTP CONNECT tunneling is the standard approach (same as curl)
- Connection pool behavior is correct because httpcore's HTTP proxy is mature

### Verification:
```bash
# Test bridge
curl -x http://127.0.0.1:10807 -s --connect-timeout 10 "https://api.telegram.org"

# Test httpx through bridge
python -c "
import httpx, asyncio
async def t():
    async with httpx.AsyncClient(proxy='http://127.0.0.1:10807') as c:
        r = await c.get('https://api.telegram.org/bot{TOKEN}/getMe')
        print(r.status_code, r.text[:100])
asyncio.run(t())
"
```

## Proxy Reliability Diagnostic (MUST run FIRST — 2026-06-27 lesson)

**CRITICAL: Before patching ANY code, test proxy reliability with a loop:**

```bash
# Test 20 sequential requests through proxy
for i in $(seq 1 20); do
  code=$(curl -x socks5://127.0.0.1:10806 -s --connect-timeout 5 --max-time 10 \
    -o /dev/null -w "%{http_code}" "https://api.telegram.org")
  echo "attempt $i: HTTP $code"
done
```

**Decision tree:**
- ≥95% success → proxy is fine, problem is httpx in gateway (use bridge or keepalive_expiry)
- 70-95% success → proxy is intermittent, gateway will eventually connect but with delays
- <70% success → proxy is unreliable, fix the proxy (restart v2rayN, check server)
- 0% success → proxy is dead, don't touch code

**Real data (2026-06-27):** v2rayN/xray on port 10806 showed 60% success rate (12/20). This was the actual root cause — no amount of adapter.py patching could fix an unreliable proxy.

## keepalive_expiry=0 Workaround (intermediate fix)

When proxy works but gateway still fails, setting `keepalive_expiry=0` forces httpx to create fresh connections for each request instead of reusing pooled ones:

```python
import httpx
proxy_limits = httpx.Limits(
    max_connections=512,
    max_keepalive_connections=16,
    keepalive_expiry=0,  # force fresh connections
)
request = HTTPXRequest(
    proxy="socks5://127.0.0.1:10806",
    httpx_kwargs={"limits": proxy_limits}
)
```

**Effectiveness:** Reduces errors when proxy is intermittent (60-80% success). Does NOT fix when proxy is fundamentally broken or when httpcore socks has the "Server disconnected" bug.

**This is a workaround, not a fix.** The HTTP→SOCKS5 bridge is the proper solution for the httpcore socks bug.

## Previous Approaches (all failed in gateway)

| Approach | Standalone | Gateway | Notes |
|----------|-----------|---------|-------|
| `proxy=socks5://` kwarg | ✅ 5/5 | ❌ 0/100 | httpcore socks_proxy.py fails in long-lived process |
| `httpx_socks.AsyncProxyTransport` | ✅ 5/5 | ❌ 0/100 | Same httpcore transport underneath |
| `_drain_polling_connections()` | N/A | ❌ | Only drains polling request, not general |
| `connect_timeout=30` | N/A | ❌ | Helps with connect, not with "Server disconnected" |
| `keepalive_expiry=0` | ✅ 5/5 | ⚠️ 60-80% | Forces fresh connections; helps when proxy is intermittent but doesn't fix httpcore socks bug |
| **HTTP→SOCKS5 bridge** | ✅ 5/5 | ✅ 5/5 | Uses httpcore AsyncHTTPProxy (mature), bypasses SOCKS transport entirely |

## Gateway Adapter Notes

The adapter's `_drain_polling_connections()` (line 1538) only shuts down + reinitializes the **polling** HTTPXRequest (`bot._request[0]`). The **general** HTTPXRequest (`bot._request[1]`) is left untouched. This means stale connections in the general request's pool persist across reconnects. However, even fresh connections fail — the root cause is in the SOCKS transport itself, not pool management.

## Verification commands
```bash
# Test proxy works
curl -x socks5://127.0.0.1:10806 -s --connect-timeout 10 "https://api.telegram.org/bot{TOKEN}/getMe"

# Test bridge
curl -x http://127.0.0.1:10807 -s --connect-timeout 10 "https://api.telegram.org/bot{TOKEN}/getMe"

# Check gateway connections
netstat -ano | grep <GATEWAY_PID> | grep 1080

# Check which process owns proxy port
netstat -ano | grep LISTENING | grep 10806
wmic process where ProcessId=<PID> get CommandLine
```
