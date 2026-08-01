#!/usr/bin/env python3
"""Quick test: does the TG bot token work?"""
import urllib.request, json, os, sys


> Revisit: when test logic, Telegram message sending, or test verification changes. Last touched: 2026-07-02.
HERMES_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(HERMES_HOME, ".env")

token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
if not token:
    for line in open(env_path, encoding="utf-8"):
        line = line.strip()
        if line.startswith("TELEGRAM_BOT_TOKEN=") and not line.startswith("#"):
            token = line.split("=", 1)[1].strip().strip('"').strip("'")
            break

print(f"Token: {'YES' if token else 'NO'} ({len(token)} chars)")

if not token:
    sys.exit(1)

proxy_handler = urllib.request.ProxyHandler({
    "http": "http://127.0.0.1:10809",
    "https": "http://127.0.0.1:10809",
})
opener = urllib.request.build_opener(proxy_handler)

url = f"https://api.telegram.org/bot{token}/getMe"
req = urllib.request.Request(url)
try:
    resp = opener.open(req, timeout=10)
    data = json.loads(resp.read())
    if data.get("ok"):
        bot = data["result"]
        print(f"OK: @{bot['username']} (id={bot['id']})")
    else:
        print(f"FAIL: {data}")
except Exception as e:
    print(f"ERROR: {e}")
