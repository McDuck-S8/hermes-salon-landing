#!/usr/bin/env python3
"""
Telegram Delivery Bridge — отправка сообщений в Telegram через Bot API.
Читает сообщение из --message аргумента или stdin.
Токен: TELEGRAM_BOT_TOKEN (env) или --token аргумент.
Chat ID: CHAT_ID (env) или --chat-id аргумент.

Также предоставляет importable функцию send_telegram_message() для использования
из других скриптов (error_alerter.py и т.д.).
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path


def _load_env_if_missing():
    """Load .env from HERMES_HOME if TELEGRAM_BOT_TOKEN is not already set."""
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
            val = val.strip().strip("\"'")
            # Only set if not already present
            if key not in os.environ:
                os.environ[key] = val


def send_telegram_message(text, chat_id=None, token=None):
    """
    Отправляет сообщение в Telegram канал/чат.

    Args:
        text: Текст сообщения (поддерживает Markdown)
        chat_id: Chat ID или @username (по умолчанию из CHAT_ID env)
        token: Bot API токен (по умолчанию из TELEGRAM_BOT_TOKEN env)

    Returns:
        True при успехе, иначе raises исключение.

    Raises:
        ValueError: если не указан token или chat_id
        urllib.error.HTTPError: при HTTP ошибке API
        urllib.error.URLError: при сетевой ошибке
    """
    _load_env_if_missing()
    token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN не указан (token аргумент или TELEGRAM_BOT_TOKEN env)")

    chat_id = chat_id or os.environ.get("CHAT_ID")
    if not chat_id:
        raise ValueError("CHAT_ID не указан (chat_id аргумент или CHAT_ID env)")

    if not text or not text.strip():
        raise ValueError("сообщение пустое")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        if result.get("ok"):
            preview = text[:80].replace("\n", " ").strip()
            print(f"[telegram-bridge] Sent to chat {chat_id}: {preview}")
            return True
        else:
            err_desc = result.get("description", "Unknown error")
            raise RuntimeError(f"Telegram API error — {err_desc}")


def main():
    parser = argparse.ArgumentParser(description="Telegram Delivery Bridge")
    parser.add_argument("--token", help="Telegram Bot API токен")
    parser.add_argument("--chat-id", help="Chat ID или @username канала")
    parser.add_argument("--message", help="Текст сообщения (если не указан, читает stdin)")
    args = parser.parse_args()

    # Сообщение: аргумент > stdin
    if args.message:
        message = args.message
    else:
        message = sys.stdin.read().strip()
        if not message:
            print("[telegram-bridge] ERROR: сообщение пусто (--message или stdin)")
            sys.exit(1)

    try:
        send_telegram_message(text=message, chat_id=args.chat_id, token=args.token)
    except ValueError as e:
        print(f"[telegram-bridge] ERROR: {e}")
        sys.exit(1)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"[telegram-bridge] ERROR: HTTP {e.code} — {body}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"[telegram-bridge] ERROR: Network error — {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"[telegram-bridge] ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
