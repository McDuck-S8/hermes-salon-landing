#!/usr/bin/env python3
"""
Telegram Authorization Script
Run this ONCE to create a session file for Telethon.

Usage:
    python auth.py

You will be asked for:
1. Phone number
2. Verification code (sent to Telegram)
3. 2FA password (if enabled)
"""

import os
import sys
import asyncio
from pathlib import Path

from telethon import TelegramClient


async def main():
    # Load .env
    env_path = Path(os.environ.get('HERMES_HOME', Path.home() / '.hermes')) / '.env'
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ.setdefault(key.strip(), val.strip())
    
    api_id = os.environ.get("TELEGRAM_API_ID")
    api_hash = os.environ.get("TELEGRAM_API_HASH")
    
    if not api_id or not api_hash:
        print("Error: TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in .env")
        print(f"  .env path: {env_path}")
        print("  Get credentials at: https://my.telegram.org")
        sys.exit(1)
    
    # Session file location
    session_dir = Path(os.environ.get('HERMES_HOME', Path.home() / '.hermes')) / 'sessions'
    session_dir.mkdir(parents=True, exist_ok=True)
    session_path = session_dir / "hermes_session"
    
    print(f"Session will be saved to: {session_path}")
    print()
    
    client = TelegramClient(str(session_path), int(api_id), api_hash)
    
    await client.start(
        phone=lambda: input("Enter your phone number: "),
        code=lambda: input("Enter the code from Telegram: "),
        password=lambda: input("Enter 2FA password (if any, or press Enter): ") or None,
    )
    
    me = await client.get_me()
    print(f"\nAuthorized as: {me.first_name} {me.last_name or ''} (@{me.username or 'no username'})")
    print(f"Session saved to: {session_path}")
    print("\nYou can now use collect_channels.py!")
    
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
