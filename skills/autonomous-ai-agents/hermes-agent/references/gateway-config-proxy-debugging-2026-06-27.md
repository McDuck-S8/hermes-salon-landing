# Gateway Telegram Proxy Debugging — Crimea/Russia Networks (2026-06-27)

## Problem

Gateway starts but Telegram adapter cannot connect: `httpx.ConnectError` / `httpx.RemoteProtocolError` / `httpcore.ConnectTimeout`.

## Root Cause Chain (3 layers)

### Layer 1: config.yaml missing `telegram:` section

`gateway/config.py` line 1049-1062: if `telegram:` key absent from config.yaml, `apply_yaml_config_fn` is SKIPPED entirely → `TELEGRAM_PROXY` env var never set → adapter connects directly → blocked in Crimea/Russia.

### Layer 2: connect_timeout=5.0 too low for SOCKS5

`adapter.py` line 2206: default `connect_timeout=5.0`. TLS handshake through SOCKS5 proxy takes longer → `httpcore.ConnectTimeout` on `stream.start_tls()`. Verified: same code with 15s → works; with 5s → ReadTimeout.

### Layer 3: Fallback IP path bypasses proxy

`adapter.py` line 2259: when `TELEGRAM_PROXY` not set, adapter discovers Telegram fallback IPs and connects directly → blocked.

### Layer 4 (2026-06-27): DUAL CONFIG FILES — gateway reads WRONG config

**CRITICAL:** There are TWO `config.yaml` files:
1. `~/.hermes/config.yaml` — **the one gateway actually reads** (`gateway/config.py` line 811: `config_yaml_path = _home / "config.yaml"`)
2. `D:/Portable_Soft/hermes/config.yaml` — project-level config, gateway IGNORES this

**Symptom:** Agent edits `D:/Portable_Soft/hermes/config.yaml` with correct `telegram.proxy_url`, gateway still connects directly. The proxy setting is in the wrong file.

**Fix:** Always edit `~/.hermes/config.yaml` (or use `hermes config set telegram.proxy_url "..."`).

### Layer 5 (2026-06-27): YAML SYNTAX ERROR → silent fallback to .env

**CRITICAL:** If `~/.hermes/config.yaml` has ANY YAML syntax error, gateway falls back to `.env` + `gateway.json` and IGNORES all config.yaml settings (including `telegram.proxy_url`).

**Example:** `personalities: jarvis: |` with bad indentation → `Failed to process config.yaml — falling back to .env / gateway.json values`.

**Symptom:** Gateway starts but `TELEGRAM_PROXY` env var is empty. Adapter connects directly. All proxy settings in config.yaml are silently lost.

**Diagnosis:**
```bash
# Check if gateway is using config.yaml at all:
grep "Failed to process config.yaml" ~/.hermes/logs/gateway.log
# If present → YAML syntax error, fix it

# Verify the env var is set after gateway starts:
python -c "import os; print(os.environ.get('TELEGRAM_PROXY', 'NOT SET'))"
```

**Fix:** Validate YAML syntax:
```bash
python -c "import yaml; yaml.safe_load(open('C:/Users/Asus/.hermes/config.yaml')); print('YAML OK')"
```

### Layer 6 (2026-06-27): httpx connection pool stale connections through SOCKS5

SOCKS5 proxies (v2rayN/xray, sing-box) can silently drop idle connections. httpcore's connection pool reuses stale pooled connections → `RemoteProtocolError: Server disconnected without sending a response`.

**Diagnostic decision tree:**
```bash
# 1. Test proxy reliability: 20 sequential requests
for i in $(seq 1 20); do
  code=$(curl -x socks5://127.0.0.1:PORT -s --connect-timeout 5 --max-time 10 \
    -o /dev/null -w "%{http_code}" "https://api.telegram.org")
  echo "attempt $i: HTTP $code"
done
# If success rate < 95%, proxy is the problem

# 2. Test standalone httpx (isolated from gateway)
python -c "import httpx, asyncio; print(asyncio.run((lambda c: (c.get('https://api.telegram.org'), c.close())[0].status_code)(httpx.AsyncClient(proxy='socks5://127.0.0.1:PORT', timeout=httpx.Timeout(connect=30)))))"
# If standalone OK but gateway FAILS → connection pool issue
```

**Fix:** Set `keepalive_expiry=0` in httpx.Limits() for proxy connections → each request gets a fresh connection.

## Fixes (cumulative)

1. config.yaml: add `telegram: proxy_url: "socks5://127.0.0.1:10806"`
2. adapter.py: increase default `connect_timeout` from 5.0 to 30.0
3. Clear `__pycache__` after editing adapter.py
4. Edit the RIGHT config: `~/.hermes/config.yaml` (not project root)
5. Fix ALL YAML syntax errors in config.yaml (gateway fails silently on any error)
6. Set `keepalive_expiry=0` for proxy connections if SOCKS5 is intermittent

## Verification

```bash
# 1. Config is valid YAML
python -c "import yaml; yaml.safe_load(open('C:/Users/Asus/.hermes/config.yaml')); print('YAML OK')"

# 2. Proxy URL is in the right file
grep "proxy_url" C:/Users/Asus/.hermes/config.yaml

# 3. Gateway log shows proxy loaded
grep "Proxy detected" ~/.hermes/logs/gateway.log

# 4. Gateway process connected to proxy
netstat -ano | grep <PID> | grep 10806

# 5. curl through proxy works
curl -x socks5://127.0.0.1:10806 "https://api.telegram.org/bot<TOKEN>/getMe"

# 6. No YAML errors in log
grep "Failed to process config.yaml" ~/.hermes/logs/gateway.log
```

## Key Commands

```bash
hermes config set telegram.proxy_url "socks5://127.0.0.1:10806"
hermes gateway stop && hermes gateway run --replace
wmic process where "Name='python.exe'" get ProcessId,CommandLine | grep gateway
cmd.exe /c "taskkill /PID <pid> /F"
```
