# SOCKS Proxy Workaround for Python on Windows

## Problem

Python's `urllib.request` does NOT use system proxy settings or SOCKS proxies on Windows.
Even with PySocks installed, `urllib.request.urlopen()` bypasses it.

## Solution: subprocess + curl

```python
import subprocess

def http_get(url: str, timeout: int = 8) -> bytes:
    """HTTP GET via curl + SOCKS proxy."""
    result = subprocess.run(
        ["curl", "-s", "--connect-timeout", str(timeout),
         "--max-time", str(timeout + 5),
         "-x", "socks5://127.0.0.1:10806",
         url],
        capture_output=True, timeout=timeout + 10
    )
    return result.stdout
```

## Why NOT urllib + PySocks

- PySocks `set_default_proxy()` patches `socket.socket` globally
- This breaks HTTPS/TLS in many Python versions on Windows
- subprocess+curl is reliable, fast, and handles TLS natively

## Why NOT requests + PySocks

- `requests` with `proxies={"https": "socks5://..."}` works BUT
- Requires `requests[socks]` extra install
- Can conflict with other socket-level code
- subprocess+curl has zero dependencies (curl ships with Windows)

## Proxy Detection

Check if proxy is alive before using:
```bash
netstat -ano | grep 10806 | grep LISTENING
```

## Fallback

If curl also fails (proxy down, network issues):
- Return empty bytes `b""`
- Caller handles gracefully (skip signal, log warning)
- Do NOT raise exceptions — let the pipeline continue

## Tested On

- Windows 11, curl 8.9.1, Python 3.13.2
- SOCKS5 proxy on 127.0.0.1:10806
- HN API, GitHub API, httpbin.org
