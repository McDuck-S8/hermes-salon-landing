# Network & Proxy Patterns (Windows, hermes setup)

## Problem: Most CDNs blocked
Stock photo sites (Unsplash, Pexels, Pixabay), Wikimedia, and many CDNs
are unreachable from this machine. Direct curl fails with timeout.

## Solution: Use proxy for all external requests

```bash
# Set proxy before any curl/download
export ALL_PROXY=socks5://127.0.0.1:10806
export HTTPS_PROXY=http://127.0.0.1:10809
```

## aiogram import hangs without proxy

Telegram API (api.telegram.org) is unreachable directly. aiogram's import
hangs trying to connect. Fix: set proxy env vars BEFORE importing.

```python
import os, socket
os.environ['ALL_PROXY'] = 'socks5://127.0.0.1:10806'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10809'

# If env vars don't work, monkey-patch socket:
_orig = socket.socket
class ProxiedSocket(_orig):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def connect(self, address):
        # Route through proxy
        return super().connect(address)
socket.socket = ProxiedSocket
import aiogram  # Now works
```

## Python version confusion

- `which python` → hermes-agent/venv/Scripts/python (3.13.2)
- `which pip` → /d/Program Files/Python311/Scripts/pip (3.11)
- pip installs to 3.11, but `python` runs 3.13
- Fix: use explicit path "D:/Program Files/Python311/python.exe"

## Image generation blockers

- image_generate requires FAL_KEY (not set by default)
- Alternative: Pillow for generated images (no API needed)
- Alternative: download from stock sites (if CDN reachable)
- Honest fallback: tell user about the blocker, don't fabricate

## Testing connectivity

```bash
# Test if Telegram API is reachable
curl -sI --max-time 5 https://api.telegram.org 2>&1 | head -3

# Test if stock CDN is reachable
curl -sI --max-time 5 https://images.unsplash.com 2>&1 | head -3

# Test with proxy
export ALL_PROXY=socks5://127.0.0.1:10806
curl -sI --max-time 10 https://images.unsplash.com 2>&1 | head -3
```
