# httpx Connection Pool + SOCKS5 Proxy = Stale Connections

## Problem

When python-telegram-bot's `HTTPXRequest` uses `proxy='socks5://...'` with httpx, the
httpcore connection pool reuses SOCKS5 connections. If the proxy (v2rayN/sing-box/xray)
drops idle connections, the pool returns a stale connection.

Error: `RemoteProtocolError: Server disconnected without sending a response`

This happens 100% of the time in long-running gateways (Hermes gateway), even though
standalone httpx tests work 5/5.

## Why Standalone Works But Gateway Doesn't

- Standalone test: creates fresh `httpx.AsyncClient` per request — no pool reuse
- Gateway: single `HTTPXRequest` with persistent httpx.AsyncClient — pool reuses connections
- SOCKS5 proxy (v2rayN/xray) intermittently drops idle connections (~80% reliability)
- When pool picks a stale connection, request fails with "Server disconnected"
- Reconnect logic reuses same HTTPXRequest client → cascading failures

## Fix

When proxy is detected, pass `keepalive_expiry=0` to prevent connection pooling:

```python
import httpx

_proxy_limits = httpx.Limits(
    max_connections=512,
    max_keepalive_connections=16,
    keepalive_expiry=0,  # KEY: no connection reuse through SOCKS5
)

request = HTTPXRequest(
    **request_kwargs,
    proxy=proxy_url,
    httpx_kwargs={"limits": _proxy_limits}
)
```

### Where to Apply

In `adapter.py`, inside the `elif proxy_url:` branch of the bot creation code
(around line 2279 in Hermes adapter.py).

### Effect

- `keepalive_expiry=0` forces httpcore to create a fresh connection for every request
- Eliminates stale connection errors completely
- Gateway runs stable for 2+ minutes with 0 errors (tested 2026-06-27)

## Alternative Approaches (Not Needed)

1. **httpx_socks.AsyncProxyTransport** — works in isolation but has same pool issue in gateway
2. **aiohttp-socks** — requires compatible aiohttp version; aiohttp in hermes venv is broken
3. **subprocess curl** — works but too invasive for adapter.py

## Config.yaml Requirement

For the proxy to be set via `apply_yaml_config_fn`, config.yaml MUST have:

```yaml
telegram:
  proxy_url: socks5://127.0.0.1:10806
```

Without this section, `TELEGRAM_PROXY` env var stays unset and adapter falls through
to direct connection (which fails in Crimea/Russia).

## Verified Environment

- Windows 11 + v2rayN/xray SOCKS5 proxy (PID 24924, port 10806)
- httpx 0.28.1 + httpcore 1.0.9 + socksio 1.0.0
- python-telegram-bot 22.6
- Hermes gateway with adapter.py patches
