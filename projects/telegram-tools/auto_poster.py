#!/usr/bin/env python3
"""
Auto-poster — публикует контент в Telegram каналы по расписанию.

Контент генерируется из шаблонов + trending topics.
Публикуется через Telegram Bot API.

Запуск:
    TELEGRAM_BOT_TOKEN=xxx python auto_poster.py
    TELEGRAM_BOT_TOKEN=xxx python auto_poster.py --preview
"""
import os
import json
import random
import urllib.request
from datetime import datetime
from pathlib import Path

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

# Content templates for different channels
CONTENT_TEMPLATES = {
    "ai_tips": [
        "Pro tip: Always test your prompts with edge cases before deploying.\n\nWhat edge cases do you test for?",
        "The best AI workflow: Human sets direction -> AI executes -> Human verifies.\n\nNever skip the verification step.",
        "3 signs your AI agent is actually useful:\n1. It saves you time on repetitive tasks\n2. It remembers context between sessions\n3. It asks for clarification when uncertain",
        "AI automation isn't about replacing humans. It's about amplifying what humans do best: creative thinking and decision-making.",
        "Your AI agent should be like a good assistant: proactive, reliable, and knows when to ask for help.",
    ],
    "tech_news": [
        "New: Open-source AI models now outperform proprietary ones in many benchmarks.\n\nWhat this means for developers: free tools are catching up fast.",
        "Trend: AI agents are moving from chatbots to autonomous workers.\n\nThe shift: from 'answer my question' to 'do this task for me'.",
        "The future of development: AI handles the boilerplate, humans handle the architecture.\n\nWho else is seeing this shift?",
        "MCP (Model Context Protocol) is becoming the standard for AI tool integration.\n\nThink of it as USB for AI agents.",
    ],
    "business_ideas": [
        "Business idea: AI-powered appointment booking for salons.\n\nMarket: 50k+ salons in Russia alone.\nMVP: Telegram bot + SQLite.\nRevenue: 500-2000 rub/month per client.",
        "Business idea: Automated social media content for small businesses.\n\nMany businesses know they need social media but don't have time.\nAI can generate + schedule posts.",
        "Business idea: AI document processing for accountants.\n\nExtract data from invoices, receipts, contracts.\nSave hours of manual data entry.",
    ],
}


def generate_post(category: str = None) -> str:
    """Generate a post from templates."""
    if category is None:
        category = random.choice(list(CONTENT_TEMPLATES.keys()))
    templates = CONTENT_TEMPLATES.get(category, CONTENT_TEMPLATES["ai_tips"])
    return random.choice(templates)


def send_message(chat_id: int, text: str):
    """Send message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            if result.get("ok"):
                print(f"Posted to {chat_id}")
            else:
                print(f"Error: {result}")
    except Exception as e:
        print(f"Send error: {e}")


def preview():
    """Preview posts without sending."""
    print("=== AUTO-POSTER PREVIEW ===\n")
    for category in CONTENT_TEMPLATES:
        post = generate_post(category)
        print(f"[{category}]")
        print(post)
        print()


def main():
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        return

    if "--preview" in sys.argv:
        preview()
        return

    # Post to configured channels
    channels_file = Path(__file__).parent.parent / ".env"
    channel_ids = []

    # Read channel IDs from .env
    if channels_file.exists():
        for line in channels_file.read_text().splitlines():
            if "CHANNEL" in line and "=" in line:
                try:
                    cid = int(line.split("=", 1)[1].strip())
                    channel_ids.append(cid)
                except ValueError:
                    pass

    if not channel_ids:
        print("No channels configured. Set CHANNEL_ID in .env")
        print("Or use --preview to see sample posts")
        return

    print(f"Posting to {len(channel_ids)} channels...")
    for cid in channel_ids:
        post = generate_post()
        send_message(cid, post)
        print(f"  Sent to {cid}: {post[:50]}...")


if __name__ == "__main__":
    import sys
    main()
