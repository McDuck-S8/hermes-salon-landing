# Proxy Fallback Pattern — Crimea/Russia Telegram Access

## Architecture
v2rayN runs TWO xray processes simultaneously:
- **PID A** (SOCKS5): port 10806 — UNRELIABLE (60-80% uptime)
- **PID B** (HTTP): ports 10808, 10809 — MORE RELIABLE

## Fallback Strategy
1. Test SOCKS5 (10806): `curl -x socks5://127.0.0.1:10806 -s --connect-timeout 8 https://api.telegram.org`
2. If fails, test HTTP (10809): `curl -x http://127.0.0.1:10809 -s --connect-timeout 8 https://api.telegram.org`
3. If both fail, direct connection won't work (Telegram blocked in RF)
4. Switch config.yaml `telegram.proxy_url` to working proxy, restart gateway

## Config Location
- `~/.hermes/config.yaml` — `telegram.proxy_url` field
- Gateway reads it and sets `TELEGRAM_PROXY` env var
- Adapter at `hermes-agent/plugins/platforms/telegram/adapter.py` uses it

## Gateway Requirements
- `~/.hermes/.env` must contain `TELEGRAM_BOT_TOKEN`
- `config.yaml` must have valid `telegram:` section with `proxy_url`
- Both are required — missing either = "No messaging platforms enabled"

## httpx Proxy Fixes (adapter.py)
- `keepalive_expiry=0` — force fresh connections per request (prevents stale SOCKS5 connections)
- `connect_timeout=30` — generous timeout for unreliable proxy
- Use `proxy=proxy_url` kwarg on HTTPXRequest, not transport-level proxy

## CRITICAL: Python httpx CANNOT use SOCKS5 proxy reliably (discovered 2026-06-27)

**Problem:** httpx + socksio/httpx_socks raises `anyio.EndOfStream` during TLS handshake through SOCKS5 tunnel. curl works 8/8, Python httpx fails 100%.

**Root cause:** TLS wrapping through SOCKS5 CONNECT tunnel fails in Python's async stack. The proxy accepts the connection but TLS handshake drops.

**Verified:**
```python
# FAILS — anyio.EndOfStream during TLS
async with httpx.AsyncClient(proxy='socks5://127.0.0.1:10806', timeout=15) as client:
    await client.get('https://api.telegram.org')

# WORKS — HTTP proxy handles TLS differently
async with httpx.AsyncClient(proxy='http://127.0.0.1:10809', timeout=15) as client:
    await client.get('https://api.telegram.org')  # 302 OK
```

**Rule:** For Python/Telegram gateway, ALWAYS use HTTP proxy (10809), NEVER SOCKS5 (10806).

## Config Override via Environment Variable

When config.yaml is unwritable (e.g. C: drive full at 100%):
```bash
TELEGRAM_PROXY="http://127.0.0.1:10809" hermes-agent/.venv/Scripts/python.exe -m hermes_cli.main gateway run
```
The adapter checks `TELEGRAM_PROXY` env var first (line 7406-7407 in adapter.py):
```python
if "proxy_url" in telegram_cfg and not os.getenv("TELEGRAM_PROXY"):
    os.environ["TELEGRAM_PROXY"] = str(telegram_cfg["proxy_url"]).strip()
```
Env var takes precedence — no config file edit needed.

## v2rayN Server Switching
Config at `D:\v2rayN-windows-64\guiNConfig.json`:
- `activeServer` index → current server
- `vmess` array → list of servers
- Change index, restart xray to switch

## Diagnosis Checklist
1. `netstat -ano | grep LISTENING | grep -E "1080[6-9]"` — which ports alive?
2. `curl -x http://127.0.0.1:10809 ...` — HTTP proxy test
3. `curl -x socks5://127.0.0.1:10806 ...` — SOCKS5 proxy test (curl works, Python won't!)
4. `hermes gateway list` — gateway running?
5. `netstat -ano | grep <gateway_pid> | grep 10809` — gateway connected to proxy?
