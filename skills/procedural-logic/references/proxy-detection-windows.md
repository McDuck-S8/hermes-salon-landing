# Windows Proxy Detection — V2RayN and Others

## Problem
Hardcoded proxy ports break when user switches VPN/proxy tools. V2RayN port changes between installs.

## Detection via Registry (2026-06-29)
```python
import winreg
key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Internet Settings')
proxy_enable = winreg.QueryValueEx(key, 'ProxyEnable')[0]
proxy_server = winreg.QueryValueEx(key, 'ProxyServer')[0] if proxy_enable else None
# Returns: "127.0.0.1:10806" (V2RayN) or "127.0.0.1:10809" (older setup)
winreg.CloseKey(key)
```

## Port Verification
```bash
netstat -ano | grep LISTEN | grep <port>
# If port is LISTENING → proxy is active
```

## Telegram API Quirk
- `api.telegram.org` — TLS handshake fails through V2RayN HTTP proxy (CONNECT tunnel works, TLS stalls)
- `web.telegram.org` — works fine through same proxy
- Workaround: check if Telegram process is running (`tasklist | grep Telegram`), or use `web.telegram.org` as connectivity test

## curl Proxy Syntax
```bash
# HTTP proxy
curl -s -o /dev/null -w "%{http_code}" --proxy http://127.0.0.1:10806 https://site.com

# SOCKS5 proxy (unreliable on Windows)
curl -s -o /dev/null -w "%{http_code}" --proxy socks5h://127.0.0.1:10806 https://site.com
```

## Python urllib Proxy
```python
import urllib.request
proxy = urllib.request.ProxyHandler({'https': 'http://127.0.0.1:10806'})
opener = urllib.request.build_opener(proxy)
r = opener.open('https://site.com', timeout=10)
```
