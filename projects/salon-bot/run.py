#!/usr/bin/env python3
"""Launch salon_booking_bot.py with proxy and env loaded."""
import os
import sys

# Load .env
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()

# Set proxy
os.environ['PROXY'] = 'socks5://127.0.0.1:10806'

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

print(f"Token: {os.environ['TELEGRAM_BOT_TOKEN'][:10]}...")
print(f"Proxy: {os.environ['PROXY']}")
print("Starting bot...")

from salon_booking_bot import main
import asyncio
asyncio.run(main())
