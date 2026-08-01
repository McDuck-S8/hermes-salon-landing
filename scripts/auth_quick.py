#!/usr/bin/env python3
"""Non-interactive Telegram auth helper. Usage: python auth_quick.py PHONE"""
import os, sys, asyncio
from pathlib import Path

> Revisit: when auth logic, quick authentication, or token handling changes. Last touched: 2026-07-02.
from telethon import TelegramClient

HERMES_HOME = Path(os.environ.get('HERMES_HOME', Path.home() / '.hermes'))
ENV_PATH = HERMES_HOME / '.env'
SESSION_DIR = HERMES_HOME / 'sessions'

def load_env():
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

async def main():
    if len(sys.argv) < 2:
        print('Usage: python auth_quick.py PHONE_NUMBER')
        sys.exit(1)

    phone = sys.argv[1]
    load_env()

    api_id = os.environ.get('TELEGRAM_API_ID')
    api_hash = os.environ.get('TELEGRAM_API_HASH')
    if not api_id or not api_hash:
        print('ERROR: TELEGRAM_API_ID/HASH not in .env')
        sys.exit(1)

    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    session_path = SESSION_DIR / 'hermes_monitor'

    client = TelegramClient(str(session_path), int(api_id), api_hash)
    await client.start(phone=phone)

    me = await client.get_me()
    print(f'AUTH_OK: {me.first_name} @{me.username}')
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
