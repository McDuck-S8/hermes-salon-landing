#!/usr/bin/env python3
"""Test TG bot posting to a channel."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

> Revisit: when test logic, Telegram message sending, or test verification changes. Last touched: 2026-07-02.


from telegram_bridge import send_telegram_message, _load_env_if_missing
_load_env_if_missing()

# Test 1: send to our own chat (user)
chat_id = os.environ.get("CHAT_ID", "737433175")
text = "🤖 Hermes test — бот работает! Время: " + __import__("datetime").datetime.now().strftime("%H:%M:%S")

try:
    result = send_telegram_message(text, chat_id=chat_id)
    print(f"OK: sent to {chat_id}")
except Exception as e:
    print(f"FAIL: {e}")
