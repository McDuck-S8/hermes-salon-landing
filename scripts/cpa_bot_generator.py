#!/usr/bin/env python3
"""Telegram CPA bot template — receive traffic, send offer links, track clicks."""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

HERMES = Path("D:/Portable_Soft/hermes")
TOKEN_ENV = "CPA_BOT_TOKEN"

# === CONFIG ===
BOT_TEMPLATES = {
    "cpa_offers": {
        "name": "CPA Offers Bot",
        "start_msg": "Welcome! Click below to claim your offer.",
        "offer_text": "🔥 Exclusive offer just for you!\n\nClick the button below to get started.",
        "offer_button": "🚀 GET OFFER",
        "fallback_text": "Offer expired. Check back later!",
        "admin_ids": [],
    },
    "content_locker": {
        "name": "Content Locker Bot",
        "start_msg": "🔓 Unlock exclusive content — free V-Bucks, Robux, and more!",
        "offer_text": "✅ Complete ONE quick step to unlock:\n\n👇 Tap the button below",
        "offer_button": "🔓 UNLOCK NOW",
        "fallback_text": "All slots filled today. Try again tomorrow!",
        "admin_ids": [],
    },
    "vpn_promo": {
        "name": "VPN Promo Bot",
        "start_msg": "🔒 Protect your privacy online.\n\nGet 60% OFF + 3 months free!",
        "offer_text": "🌐 Secure your connection now:\n\n• 50+ countries\n• No logs policy\n• 30-day money back",
        "offer_button": "🔥 CLAIM DISCOUNT",
        "fallback_text": "Promo ended. New deals coming soon!",
        "admin_ids": [],
    },
}


def generate_bot(template_name: str, token: Optional[str] = None, output: Optional[str] = None) -> Optional[str]:
    """Generate a runnable Telegram CPA bot from template."""
    t = BOT_TEMPLATES.get(template_name)
    if not t:
        print(f"Unknown: {template_name}. Available: {', '.join(BOT_TEMPLATES.keys())}")
        return None

    token_val = token or f'os.environ.get("{TOKEN_ENV}", "YOUR_TOKEN_HERE")'
    token_line = f'TOKEN = "{token_val}"' if token else f'TOKEN = os.environ.get("{TOKEN_ENV}", "YOUR_BOT_TOKEN")'

    code = f'''#!/usr/bin/env python3
"""Telegram CPA Bot — {t['name']} (auto-generated)"""

import os
import sys
import logging
from pathlib import Path

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
except ImportError:
    print("Install python-telegram-bot: pip install python-telegram-bot")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

{token_line}

OFFER_URL = os.environ.get("CPA_OFFER_URL", {json.dumps(f'https://mcduck-s8.github.io/hermes-salon-landing/cpa/{template_name}/')})
ADMIN_IDS = {json.dumps(t['admin_ids'])}

START_MSG = {json.dumps(t['start_msg'])}
OFFER_TEXT = {json.dumps(t['offer_text'])}
OFFER_BUTTON = {json.dumps(t['offer_button'])}
FALLBACK_TEXT = {json.dumps(t['fallback_text'])}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log.info(f"Start: {{user.id}} {{user.full_name}}")
    keyboard = [[InlineKeyboardButton(OFFER_BUTTON, url=OFFER_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(START_MSG, reply_markup=reply_markup)


async def offer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(OFFER_BUTTON, url=OFFER_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(OFFER_TEXT, reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("Unauthorized.")
        return
    await update.message.reply_text("Bot running. Check CPA dashboard for stats.")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("offer", offer))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(button))
    log.info("Bot started")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
'''

    out_path = output or (HERMES / "projects" / f"cpa-bot-{template_name}" / "bot.py")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Also create a requirements.txt
    req_path = out_path.parent / "requirements.txt"
    req_path.write_text("python-telegram-bot>=21.0\n", encoding="utf-8")

    # Create a .env.example
    env_path = out_path.parent / ".env.example"
    env_path.write_text(f"CPA_BOT_TOKEN=your_bot_token_from_@BotFather\nCPA_OFFER_URL=https://mcduck-s8.github.io/hermes-salon-landing/cpa/{template_name}/\n", encoding="utf-8")

    out_path.write_text(code, encoding="utf-8")
    return str(out_path)


def list_templates():
    print(f"Available bot templates ({len(BOT_TEMPLATES)}):")
    for name, t in BOT_TEMPLATES.items():
        print(f"  {name:<20} {t['name']}")


def batch_bots():
    results = []
    for name in BOT_TEMPLATES:
        path = generate_bot(name)
        if path:
            results.append((name, path))
    return results


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "list":
            list_templates()
        elif cmd == "generate" and len(sys.argv) >= 3:
            path = generate_bot(sys.argv[2])
            if path:
                print(f"Generated: {path}")
                print(f"Set CPA_BOT_TOKEN=... and run: python {path}")
        elif cmd == "batch":
            results = batch_bots()
            print(f"Generated {len(results)} bots:")
            for name, path in results:
                print(f"  {name}: {path}")
        else:
            print("Usage: python cpa_bot_generator.py [list|generate <name>|batch]")
    else:
        list_templates()
