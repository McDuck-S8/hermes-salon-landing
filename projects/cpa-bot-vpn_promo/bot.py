#!/usr/bin/env python3
"""Telegram CPA Bot — VPN Promo Bot (auto-generated)"""

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

TOKEN = os.environ.get("CPA_BOT_TOKEN", "YOUR_BOT_TOKEN")

OFFER_URL = os.environ.get("CPA_OFFER_URL", "https://mcduck-s8.github.io/hermes-salon-landing/cpa/vpn_promo/")
ADMIN_IDS = []

START_MSG = "\ud83d\udd12 Protect your privacy online.\n\nGet 60% OFF + 3 months free!"
OFFER_TEXT = "\ud83c\udf10 Secure your connection now:\n\n\u2022 50+ countries\n\u2022 No logs policy\n\u2022 30-day money back"
OFFER_BUTTON = "\ud83d\udd25 CLAIM DISCOUNT"
FALLBACK_TEXT = "Promo ended. New deals coming soon!"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log.info(f"Start: {user.id} {user.full_name}")
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
