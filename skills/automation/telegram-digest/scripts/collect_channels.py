#!/usr/bin/env python3
"""
Telegram Channel Collector
Collects messages from specified Telegram channels using User API (Telethon).

Usage:
    python collect_channels.py --channels "channel1,channel2" --hours 24
    python collect_channels.py --channels "channel1,channel2" --output /tmp/digest.json

Environment:
    TELEGRAM_API_ID - Telegram API ID
    TELEGRAM_API_HASH - Telegram API Hash
"""

import os
import sys
import json
import asyncio
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from telethon import TelegramClient
from telethon.errors import ChannelPrivateError, ChatAdminRequiredError


def get_env_or_die(name: str) -> str:
    """Get environment variable or exit with error."""
    val = os.environ.get(name)
    if not val:
        print(f"Error: {name} not set in environment or .env file", file=sys.stderr)
        sys.exit(1)
    return val


async def collect_channel(client: TelegramClient, channel_username: str, hours: int) -> dict:
    """Collect messages from a single channel."""
    result = {
        "url": f"https://t.me/{channel_username}",
        "messages": [],
        "error": None
    }
    
    try:
        entity = await client.get_entity(channel_username)
        since = datetime.now() - timedelta(hours=hours)
        
        async for message in client.iter_messages(entity, offset_date=since, reverse=True):
            if message.text:  # Only text messages
                msg_data = {
                    "id": message.id,
                    "date": message.date.isoformat(),
                    "text": message.text[:2000],  # Limit text length
                    "views": message.views or 0,
                    "forwards": message.forwards or 0,
                    "link": f"https://t.me/{channel_username}/{message.id}"
                }
                result["messages"].append(msg_data)
        
        result["total"] = len(result["messages"])
        
    except ChannelPrivateError:
        result["error"] = "Channel is private - cannot access"
    except ChatAdminRequiredError:
        result["error"] = "Admin privileges required"
    except Exception as e:
        result["error"] = str(e)
    
    return result


async def main():
    parser = argparse.ArgumentParser(description="Collect Telegram channel messages")
    parser.add_argument("--channels", required=True, help="Comma-separated channel usernames")
    parser.add_argument("--hours", type=int, default=24, help="Hours to look back (default: 24)")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--session", default="hermes_session", help="Session name")
    args = parser.parse_args()
    
    # Load .env if exists
    env_path = Path(os.environ.get('HERMES_HOME', Path.home() / '.hermes')) / '.env'
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ.setdefault(key.strip(), val.strip())
    
    api_id = get_env_or_die("TELEGRAM_API_ID")
    api_hash = get_env_or_die("TELEGRAM_API_HASH")
    
    # Session file location
    session_dir = Path(os.environ.get('HERMES_HOME', Path.home() / '.hermes')) / 'sessions'
    session_dir.mkdir(parents=True, exist_ok=True)
    session_path = session_dir / args.session
    
    client = TelegramClient(str(session_path), int(api_id), api_hash)
    await client.start()
    
    channels = [c.strip() for c in args.channels.split(",") if c.strip()]
    
    print(f"Collecting from {len(channels)} channels, last {args.hours} hours...")
    
    output = {
        "collected_at": datetime.now().isoformat(),
        "channels": {},
        "total_messages": 0
    }
    
    for channel in channels:
        print(f"  -> {channel}...", end=" ", flush=True)
        result = await collect_channel(client, channel, args.hours)
        output["channels"][channel] = result
        
        if result["error"]:
            print(f"ERROR: {result['error']}")
        else:
            print(f"{result['total']} messages")
            output["total_messages"] += result["total"]
    
    await client.disconnect()
    
    # Output
    json_output = json.dumps(output, ensure_ascii=False, indent=2)
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json_output, encoding='utf-8')
        print(f"\nSaved to: {args.output}")
    else:
        print(json_output)
    
    print(f"\nTotal: {output['total_messages']} messages from {len(channels)} channels")


if __name__ == "__main__":
    asyncio.run(main())
