#!/usr/bin/env python3
"""
Full Telegram Digest Pipeline
1. Collect messages from channels
2. Generate AI digest
3. Return formatted summary

Usage:
    python digest_pipeline.py --channels "channel1,channel2" --hours 24
    python digest_pipeline.py --channels "channel1,channel2" --style telegram

This is the main entry point for cron jobs.
"""

import os
import sys
import json
import asyncio
import argparse
from datetime import datetime
from pathlib import Path

# Add paths
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from telethon import TelegramClient
from telethon.errors import ChannelPrivateError, ChatAdminRequiredError


def load_env():
    """Load .env file."""
    env_path = Path(os.environ.get('HERMES_HOME', Path.home() / '.hermes')) / '.env'
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ.setdefault(key.strip(), val.strip())


def format_digest(data: dict, style: str = "telegram") -> str:
    """Format collected data into digest."""
    collected = data.get("collected_at", "")
    total = data.get("total_messages", 0)
    channels = data.get("channels", {})
    
    if style == "telegram":
        lines = [
            f"📰 **ДАЙДЖЕСТ TELEGRAM**",
            f"📅 {collected[:10]} | 📊 {total} сообщений из {len(channels)} каналов",
            "",
            "━━━━━━━━━━━━━━━━",
        ]
        
        for channel_name, channel_data in channels.items():
            messages = channel_data.get("messages", [])
            error = channel_data.get("error")
            
            if error:
                lines.append(f"\n⚠️ **@{channel_name}** — {error}")
                continue
            
            if not messages:
                lines.append(f"\n📭 **@{channel_name}** — нет сообщений")
                continue
            
            lines.append(f"\n📢 **@{channel_name}** ({len(messages)} сообщений)")
            lines.append("")
            
            # Top messages by views
            popular = sorted(messages, key=lambda m: m.get("views", 0), reverse=True)[:5]
            
            for i, msg in enumerate(popular, 1):
                text = msg["text"][:150].replace("\n", " ")
                views = msg.get("views", 0)
                link = msg.get("link", "")
                
                views_str = f"{views:,}" if views > 0 else ""
                view_emoji = "🔥" if views > 10000 else "👁" if views > 1000 else ""
                
                lines.append(f"{i}. {text}...")
                if views_str:
                    lines.append(f"   {view_emoji} {views_str} просмотров")
                if link:
                    lines.append(f"   🔗 {link}")
                lines.append("")
        
        lines.append("━━━━━━━━━━━━━━━━")
        lines.append(f"🤖 Собрано Hermes Agent | {collected[:19]}")
        
        return "\n".join(lines)
    
    else:
        # Brief style
        lines = [f"📰 Дайджест за {collected[:10]}\n"]
        for channel_name, channel_data in channels.items():
            messages = channel_data.get("messages", [])
            if messages:
                lines.append(f"**@{channel_name}:**")
                for msg in sorted(messages, key=lambda m: m.get("views", 0), reverse=True)[:3]:
                    text = msg["text"][:100].replace("\n", " ")
                    lines.append(f"• {text}")
                lines.append("")
        return "\n".join(lines)


async def collect_channels(channels: list, hours: int, session_name: str = "hermes_session") -> dict:
    """Collect messages from channels."""
    api_id = os.environ.get("TELEGRAM_API_ID")
    api_hash = os.environ.get("TELEGRAM_API_HASH")
    
    if not api_id or not api_hash:
        return {"error": "TELEGRAM_API_ID and TELEGRAM_API_HASH not set"}
    
    session_dir = Path(os.environ.get('HERMES_HOME', Path.home() / '.hermes')) / 'sessions'
    session_dir.mkdir(parents=True, exist_ok=True)
    session_path = session_dir / session_name
    
    client = TelegramClient(str(session_path), int(api_id), api_hash)
    await client.start()
    
    output = {
        "collected_at": datetime.now().isoformat(),
        "channels": {},
        "total_messages": 0
    }
    
    for channel in channels:
        channel = channel.strip()
        if not channel:
            continue
        
        result = {"url": f"https://t.me/{channel}", "messages": [], "error": None}
        
        try:
            entity = await client.get_entity(channel)
            from datetime import timedelta
            since = datetime.now() - timedelta(hours=hours)
            
            async for message in client.iter_messages(entity, offset_date=since, reverse=True):
                if message.text:
                    result["messages"].append({
                        "id": message.id,
                        "date": message.date.isoformat(),
                        "text": message.text[:2000],
                        "views": message.views or 0,
                        "forwards": message.forwards or 0,
                        "link": f"https://t.me/{channel}/{message.id}"
                    })
            
            result["total"] = len(result["messages"])
            output["total_messages"] += result["total"]
            
        except ChannelPrivateError:
            result["error"] = "Channel is private"
        except ChatAdminRequiredError:
            result["error"] = "Admin required"
        except Exception as e:
            result["error"] = str(e)
        
        output["channels"][channel] = result
    
    await client.disconnect()
    return output


async def main():
    parser = argparse.ArgumentParser(description="Telegram Digest Pipeline")
    parser.add_argument("--channels", required=True, help="Comma-separated channel usernames")
    parser.add_argument("--hours", type=int, default=24, help="Hours to look back")
    parser.add_argument("--style", choices=["telegram", "brief"], default="telegram")
    parser.add_argument("--output", help="Save digest to file")
    parser.add_argument("--json", help="Save raw JSON to file")
    args = parser.parse_args()
    
    load_env()
    
    channels = [c.strip() for c in args.channels.split(",") if c.strip()]
    
    print(f"[{datetime.now():%H:%M:%S}] Collecting from {len(channels)} channels...", flush=True)
    
    data = await collect_channels(channels, args.hours)
    
    if "error" in data:
        print(f"Error: {data['error']}", file=sys.stderr)
        sys.exit(1)
    
    # Save raw JSON if requested
    if args.json:
        Path(args.json).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"JSON saved to: {args.json}")
    
    # Generate digest
    digest = format_digest(data, args.style)
    
    if args.output:
        Path(args.output).write_text(digest, encoding='utf-8')
        print(f"Digest saved to: {args.output}")
    else:
        print("\n" + digest)
    
    print(f"\n[{datetime.now():%H:%M:%S}] Done! {data['total_messages']} messages collected.")


if __name__ == "__main__":
    asyncio.run(main())
