# urllib + SOCKS Proxy on Windows — Workaround

## Problem
Python `urllib.request` does NOT work through SOCKS5 proxy on Windows, even with PySocks installed in system Python. The Hermes venv (Python 3.13) doesn't have PySocks, and installing it there doesn't help because the underlying socket replacement doesn't propagate to urllib.

## Symptoms
- `urllib.request.urlopen(url)` hangs indefinitely (no timeout)
- `httpx.get(url, proxy=...)` raises `anyio.EndOfStream` on SOCKS5+TLS
- Direct connection gets 503 (provider block)

## Solution: curl via subprocess
```python
import subprocess

def http_get(url: str, timeout: int = 8) -> bytes:
    """HTTP GET через curl + SOCKS proxy. Fail fast."""
    try:
        result = subprocess.run(
            ["curl", "-s", "--connect-timeout", "3", "--max-time", str(timeout),
             "-x", "socks5://127.0.0.1:10806", url],
            capture_output=True, timeout=timeout + 2
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
    except Exception:
        pass
    # Fallback: direct (no proxy)
    try:
        result = subprocess.run(
            ["curl", "-s", "--connect-timeout", "3", "--max-time", str(timeout), url],
            capture_output=True, timeout=timeout + 2
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
    except Exception:
        pass
    return b""  # graceful degradation
```

## Key Points
- `--connect-timeout 3` — fail fast if proxy unreachable
- `--max-time 8` — hard limit per request
- Fallback chain: SOCKS proxy → direct → empty bytes
- Never hang: always return something (even empty)
- Proxy: `socks5://127.0.0.1:10806` (SOCKS5 via V2RayN)
- HTTP proxy alternative: `http://127.0.0.1:10809`

## DON'T
- Don't install PySocks in venv (won't help urllib)
- Don't use `urllib.request.ProxyHandler` (doesn't support SOCKS5)
- Don't use `httpx` with SOCKS5 (anyio.EndOfStream on TLS)
- Don't set infinite timeouts — always cap at 10-15s
