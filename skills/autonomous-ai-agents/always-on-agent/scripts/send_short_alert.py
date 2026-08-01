#!/usr/bin/env python3
"""
Send short Telegram alerts (< 8 lines) that bypass the HTTP 400 limit.
Usage: python scripts/send_short_alert.py "Alert text line 1\nLine 2\nLine 3"
"""

import sys
import os
import json
import urllib.request
import urllib.error
from pathlib import Path

# Load .env if needed
def _load_env_if_missing():
    if os.environ.get("TELEGRAM_BOT_TOKEN"):
        return
    hermes_home = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
    env_path = hermes_home / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"\'')
            if key not in os.environ:
                os.environ[key] = val

def send_telegram_plain(text, chat_id=None, token=None):
    """Send plain text (no markdown) to avoid 400 errors."""
    _load_env_if_missing()
    token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set")
    chat_id = chat_id or os.environ.get("CHAT_ID")
    if not chat_id:
        raise ValueError("CHAT_ID not set")
    if not text or not text.strip():
        raise ValueError("empty message")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        # NO parse_mode = plain text, no markdown parsing
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    last_err = None
    for attempt in ("direct", "proxy"):
        try:
            if attempt == "proxy":
                proxy_handler = urllib.request.ProxyHandler({
                    "http": "http://127.0.0.1:10809",
                    "https": "http://127.0.0.1:10809",
                })
                opener = urllib.request.build_opener(proxy_handler)
            else:
                opener = urllib.request.build_opener()
            with opener.open(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if result.get("ok"):
                    preview = text[:80].replace("\n", " ").strip()
                    print(f"[telegram] Sent to chat {chat_id}: {preview}")
                    return True
                else:
                    err_desc = result.get("description", "Unknown error")
                    raise RuntimeError(f"Telegram API error — {err_desc}")
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            last_err = e
            continue
    raise RuntimeError(f"Telegram API unreachable (tried direct + proxy): {last_err}")

def send_short_alert(message: str):
    """Send a short alert message to Telegram (plain text, chunked if >7 lines)."""
    lines = message.strip().split('\n')
    if len(lines) > 7:
        chunks = [lines[i:i+7] for i in range(0, len(lines), 7)]
        for i, chunk in enumerate(chunks):
            chunk_msg = '\n'.join(chunk)
            if i > 0:
                chunk_msg = f"(cont.)\n{chunk_msg}"
            try:
                send_telegram_plain(chunk_msg)
                print(f"✅ Sent chunk {i+1}/{len(chunks)}")
            except Exception as e:
                print(f"❌ Failed chunk {i+1}: {e}")
    else:
        try:
            send_telegram_plain(message)
            print("✅ Sent")
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    from pathlib import Path
    if len(sys.argv) > 1:
        msg = sys.argv[1]
    else:
        msg = sys.stdin.read()
    send_short_alert(msg)