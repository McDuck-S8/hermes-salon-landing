#!/usr/bin/env python3
"""Check TG bot channels and capabilities."""
import urllib.request, json, os, sys


> Revisit: when check logic, Telegram API check, or connectivity verification changes. Last touched: 2026-07-02.
HERMES_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
token = ""
for line in open(os.path.join(HERMES_HOME, ".env"), encoding="utf-8"):
    line = line.strip()
    if line.startswith("TELEGRAM_BOT_TOKEN=") and not line.startswith("#"):
        token = line.split("=", 1)[1].strip().strip('"').strip("'")
        break

proxy = urllib.request.ProxyHandler({"http": "http://127.0.0.1:10809", "https": "http://127.0.0.1:10809"})
opener = urllib.request.build_opener(proxy)

def api(method, **params):
    url = f"https://api.telegram.org/bot{token}/{method}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    resp = opener.open(urllib.request.Request(url), timeout=10)
    return json.loads(resp.read())

# 1. getMe
me = api("getMe")
print(f"Bot: @{me['result']['username']} (id={me['result']['id']})")

# 2. getUpdates (check recent chats)
updates = api("getUpdates", limit="10")
print(f"\nRecent updates: {len(updates.get('result', []))}")
for u in updates.get("result", []):
    msg = u.get("message") or u.get("my_chat_member", {})
    chat = msg.get("chat", {})
    if chat:
        print(f"  Chat: {chat.get('title', chat.get('first_name', '?'))} (id={chat.get('id')}) type={chat.get('type')}")

# 3. Try to create a channel (test if bot is admin somewhere)
print("\n--- Bot capabilities ---")
# Check if bot can post
print(f"Can write: {me['result'].get('can_join_groups', 'unknown')}")
print(f"Can read: {me['result'].get('can_read_all_group_messages', 'unknown')}")
