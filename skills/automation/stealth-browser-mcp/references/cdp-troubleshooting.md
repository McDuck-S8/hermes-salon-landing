# CDP Troubleshooting — Chrome 136+ lockdown

## Problem: Chrome blocks WebSocket CDP

Starting from Chrome 136, remote debugging requires `--remote-allow-origins=*`.
Without it:
- HTTP `/json/version` → 404 (on default profile) or returns data (on custom `--user-data-dir`)
- WebSocket `ws://127.0.0.1:9222/devtools/browser` → 403

```
Rejected an incoming WebSocket connection from the http://127.0.0.1:9222 origin.
Use --remote-allow-origins=* to allow all origins.
```

## 3-layer diagnostics

```bash
# Layer 1: check port owner
netstat -ano | grep ":9222"
tasklist /FI "PID eq $(netstat -ano | grep ':9222.*LISTENING' | awk '{print $5}')"

# Layer 2: HTTP discovery
for var in http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY no_proxy; do unset $var; done
curl -s http://127.0.0.1:9222/json/version
curl -s http://127.0.0.1:9222/json | python -m json.tool

# Layer 3: WebSocket test
python -c "
import websocket
try:
    ws = websocket.create_connection('ws://127.0.0.1:9222/devtools/browser', timeout=5)
    print('OK:', ws.recv()[:100])
    ws.close()
except Exception as e:
    print(f'BLOCKED: {e}')
"
```

## Layer 3a: DevToolsActivePort (when HTTP 404)

Chrome writes port to `DevToolsActivePort` file when chrome://inspect checkbox is on.
This file is the ONLY way browser-harness Way 1 works:

```python
from pathlib import Path
PROFILES = [
    Path.home() / "AppData/Local/Google/Chrome/User Data",
    Path.home() / "AppData/Local/BrowserClaw/User Data",
]
for base in PROFILES:
    try:
        port, ws_path = (base / "DevToolsActivePort").read_text().splitlines()[:2]
        print(f"Port: {port}, WS: ws://127.0.0.1:{port}{ws_path}")
    except (FileNotFoundError, NotADirectoryError):
        continue
```

If this file does NOT exist, the checkbox wasn't accepted or Chrome didn't write it yet.

## Chrome cookie encryption (App-Bound)

Chrome 127+ uses **App-Bound Encryption** for cookies. `win32crypt.CryptUnprotectData` returns
`(13, 'CryptUnprotectData', 'Недопустимые данные.')`. Only `chrome.exe` or Microsoft-signed
binaries can decrypt. Cookie hijacking via filesystem is IMPOSSIBLE on modern Chrome.

```python
# All values are encrypted with no plaintext alternative:
cursor.execute("""
    SELECT host_key, name, length(encrypted_value)
    FROM cookies WHERE host_key LIKE '%.youtube.com'
""")
# → all encrypted (80-382 bytes), plain value column is empty
```

The only way to get auth cookies is via a live CDP WebSocket connection to the running Chrome.

## Origin bypass attempts (all failed)

| Origin header | Result |
|---|---|
| `http://127.0.0.1:9222` | 403 — rejected |
| `chrome://devtools` | 403 — rejected |
| `devtools://devtools` | 403 — rejected |
| No Origin header | Connection dropped (timeout) |
| `file://` | Connection dropped (timeout) |

`--remote-allow-origins=*` is the ONLY solution.

## browser-harness discovery flow

From `browser_harness/daemon.py` → `get_ws_url()`:

1. Check `BU_CDP_WS` env var (direct WebSocket URL) — fastest, use for own Chrome
2. Check `BU_CDP_URL` env var (HTTP endpoint) — resolves WS via `/json/version`
3. Search `DevToolsActivePort` in all known profile paths (Windows: AppData/Local/Google/Chrome/User Data)
4. Probe ports 9222, 9223

Setting `BU_CDP_URL=http://127.0.0.1:9333` makes browser-harness skip discovery and use a
dedicated Chrome. This bypasses both Way 1 (missing DevToolsActivePort) and Way 2 (blocked WS).

## Working Chrome launch (headless + proxy + full CDP)

```bash
chrome.exe \
  --user-data-dir="D:/path/to/custom/profile" \
  --remote-debugging-port=9333 \
  --remote-allow-origins=* \
  --proxy-server=http://127.0.0.1:10806 \
  --headless=new \
  --no-first-run --no-default-browser-check \
  https://www.youtube.com
```

Then connect directly:
```python
import websocket, json
ws = websocket.create_connection(
    json.loads(urllib.request.urlopen('http://127.0.0.1:9333/json/version').read())['webSocketDebuggerUrl'],
    timeout=10
)
```

## BrowserClaw internal ports

BrowserClaw runs its own Chrome alongside user's Chrome:

| Instance | PID | Version | Ports | CDP Access |
|---|---|---|---|---|
| User Chrome | 27328 | Chrome 150 | 9222, 9003 | Blocked (no flag) |
| BrowserClaw | 2588 | Chrome 148 | 9010 (MCP/SSE), 9011, 9110 (CDP HTTP) | Blocked (no flag) |

- BrowserClaw MCP on 9010 uses SSE protocol — requires `Accept: text/event-stream` + `mcp-session-id` header
- BrowserClaw CDP on 9110 returns `/json/version` but blocks WebSocket same way as Chrome 150

## YouTube subtitle access

Without login cookies, most niche-channel videos (faceless, CPA, automation) have NO subtitles.
Testing 15+ videos from 8 search queries: 0/15 had public subtitles.
Only 1/16 had subtitles accessible without login (EyXNKb2HsfM, 119KB).

Reason: YouTube creators must enable "Allow viewers with disabilities and researchers to access
auto-generated captions for this video" in Studio settings. Most faceless/automation channels
leave this OFF. Login cookies bypass this restriction.
