# Network Instability — Crimea ISP Decision Matrix (2026-06-25)

## Problem
From Crimea, api.telegram.org connections fail intermittently:
- SSL handshake timeout (DirectConnectionError)
- RemoteProtocolError (Server disconnected)
- OSError: [WinError 121] Semaphore timeout exceeded

## Decision Matrix

| Scenario | Action |
|----------|--------|
| Proxy works, direct fails | Use proxy (socks5://127.0.0.1:10806) |
| Proxy fails, direct works | Disable proxy: `hermes config set telegram.proxy_url ""` |
| Both fail intermittently | Direct + gateway auto-reconnect (handles ~60% of requests) |
| Proxy port listening but not routing | Kill Happ VPN (xray.exe), keep V2RayN |

## Verification Commands
```bash
# Direct connection test
curl --connect-timeout 5 https://api.telegram.org/bot{TOKEN}/getMe

# Proxy connection test
curl --socks5 127.0.0.1:10806 --connect-timeout 5 https://api.telegram.org/bot{TOKEN}/getMe

# Which process owns proxy port
netstat -ano | grep LISTENING | grep 1080
```

## Key Insight
Gateway auto-reconnect is the primary resilience mechanism. Even with 40% request failure rate, the gateway eventually connects and resumes polling. The proxy/direct choice affects failure RATE, not whether the system works.

## Proxy Port Identification
- 10806 SOCKS5 = V2RayN (CONFIRMED working)
- 10808 SOCKS5 = Happ VPN (may be dead/red herring)
- Always verify which process owns which port before concluding proxy is down
