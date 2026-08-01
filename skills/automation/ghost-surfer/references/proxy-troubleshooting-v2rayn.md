# Proxy Troubleshooting: V2RayN vs Happ VPN (Crimea/Russia)

## The Core Problem
Two VPN/proxy clients running simultaneously on the same machine, both listening on overlapping ports, causing confusion about which one actually routes Telegram/API traffic.

## Port Map (Verified 2026-07-17)

| Process | Binary | Ports | Protocol | Status |
|---------|--------|-------|----------|--------|
| **V2RayN** | `v2rayN.exe` | **10806** | SOCKS5 | ✅ WORKS for Telegram |
| **V2RayN** | `v2rayN.exe` | 10809, 10810 | HTTP | May work |
| **Happ VPN** | `xray.exe` | **10808**, 10809 | HTTP | ❌ LISTENING but NOT routing |

## How to Identify Which Process Owns Which Port

```bash
# Windows cmd (run as admin for full info)
netstat -ano | findstr "1080"

# Example output:
# TCP    127.0.0.1:10806    0.0.0.0:0    LISTENING    12340
# TCP    127.0.0.1:10808    0.0.0.0:0    LISTENING    33220
# TCP    127.0.0.1:10809    0.0.0.0:0    LISTENING    33220

# Then check process:
tasklist /FI "PID eq 12340"
tasklist /FI "PID eq 33220"
# → v2rayN.exe vs xray.exe (Happ VPN)
```

## V2RayN Config Location
```
D:\v2rayN-windows-64\guiConfigs\guiNConfig.json
```
Search for `"LocalPort"` to find configured ports.

## Diagnostic Protocol (MANDATORY Before Any Code Changes)

```bash
# 20-iteration curl test — the ONLY reliable check
for i in $(seq 1 20); do
  code=$(curl -x socks5://127.0.0.1:10806 -s --connect-timeout 5 --max-time 10 \
    -o /dev/null -w "%{http_code}" "https://api.telegram.org")
  echo "attempt $i: HTTP $code"
done
```

**Decision Tree:**
- ≥95% → proxy fine, problem is code (httpx in gateway)
- 70-95% → intermittent, gateway reconnect handles it
- <70% → unreliable proxy, fix v2rayN first
- 0% → proxy dead, code changes won't help

## Critical Pitfalls

### 1. Port Listening ≠ Proxy Working
Happ VPN's `xray.exe` listens on 10808/10809 (netstat shows LISTENING) but **does not route Telegram traffic**. Only v2rayN on 10806 works.

### 2. Wrong Port = Wasted Hours
User said "proxy works in my browser" — browser uses system proxy (HTTP 10809). Telegram bot uses SOCKS5 10806. Different ports, different results.

### 3. Direct Connection Sometimes Works
In Crimea/Russia, `api.telegram.org` is often reachable directly. If proxy is flaky, direct may be MORE reliable:
```bash
curl --connect-timeout 5 https://api.telegram.org
# If this works, consider disabling proxy
```

### 4. Gateway vs Standalone Scripts
- **Gateway** (long-lived async): SOCKS5 via httpx fails (httpcore socks bug). Use HTTP→SOCKS5 bridge on 10807.
- **Standalone scripts** (one-shot): SOCKS5 works fine via HTTPXRequest/urllib.

### 5. YAML Escaping in config.yaml
```yaml
# BAD — backslash interpreted as escape
proxy_url: "socks5://127.0.0.1:10806"

# GOOD — use hermes config set
hermes config set telegram.proxy_url "socks5://127.0.0.1:10806"
```

## Verification Checklist Before Declaring "Proxy Fixed"
- [ ] `netstat -ano | findstr 10806` shows v2rayN.exe
- [ ] 20-iteration curl test ≥95% success on 10806
- [ ] Gateway log shows "Proxy detected; passing explicitly to HTTPXRequest: socks5://..."
- [ ] `getMe` returns `ok:true` through gateway
- [ ] `sendMessage` returns `ok:true` through gateway

## When to Disable Proxy
If direct connection works reliably (test 10x) and proxy is <70%:
```bash
hermes config set telegram.proxy_url ""
# Restart gateway
```

## User Frustration Trigger
> "ты думаешь что мне бот нужен попиздеть.... что ты мне заглушку рисуешь!!!!"
> 
> Translation: User detects placeholder/stub behavior instantly. Never send "test OK", "bot online", "Crystal aktiv". Every message must contain REAL output or direct response to user input.

---
*Added 2026-07-17 after 3-hour proxy debugging session where agent confused Happ VPN (10808) with V2RayN (10806), causing user to lose trust.*