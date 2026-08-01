#!/usr/bin/env python3
"""
Telegram Bot Webhook Handler — обработка callback'ов от кнопок в каналах.
Запускает на порту 8443 (webhook mode), отдаёт лид-магниты, логирует в KC.
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# ─── Config ─────────────────────────────────────────────────────────────
load_dotenv()
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
WEBHOOK_URL = os.environ.get("TELEGRAM_WEBHOOK_URL", "https://your-domain.com/webhook")
WEBHOOK_PATH = "/webhook"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = 8443

LOG_PATH = HERMES_HOME / "logs" / "tg_webhook.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("tg_webhook")

# ─── Lead Magnets ───────────────────────────────────────────────────────
LEAD_MAGNETS = {
    "send_lead_magnet": {
        "title": "Чек-лист: Автозапись в салоне за 15 минут",
        "file": HERMES_HOME / "assets" / "content_warehouse" / "telegram" / "lead_magnet_checklist.html",
        "caption": "🎁 <b>Твой чек-лист готов!</b>\n\nВот пошаговая инструкция настройки бесплатного бота для автозаписи в салоне:\n\n✅ Создание бота через @BotFather (2 мин)\n✅ Подключение к @Manybot/@Chatfuel (3 мин)\n✅ 3 цепочки: приветствие, напоминания, возврат клиентов (10 мин)\n✅ Google Таблицы как CRM (5 мин)\n✅ Чек-лист проверки перед запуском\n\n📎 Файл в HTML — открой в браузере, распечатай или сохрани как PDF.\n\n<i>Нужна помощь с настройкой? Пиши в ЛС канала @max_brain_chef_official</i>",
    },
    "send_case_study": {
        "title": "Кейс: Салон на Дарнице +40% повторок",
        "file": HERMES_HOME / "assets" / "content_warehouse" / "telegram" / "case_study_darnitsa.html",
        "caption": "📖 <b>Кейс салона на Дарнице</b>\n\nКак салон 3 мастера увеличил повторные записи на 40% за 2 недели без рекламы:\n\n🔴 <b>Было:</b> No-show 25%, админ 6ч/нед на звонки, теряли клиентов\n🟢 <b>Стало:</b> No-show 5%, админ 0ч на звонки, +42к грн/мес\n\n🛠 <b>Что сделали за 1 вечер:</b>\n1. Подключили бесплатного бота @Manybot\n2. Настроили 3 цепочки: напоминание 24ч/2ч + возврат через 21 день + апсейл\n3. Добавили кнопку «Записаться» в Инстаграм профиль\n\n🎁 Хочешь повторить? Жми кнопку ниже — скину чек-лист.",
    },
}

# ─── Handlers ───────────────────────────────────────────────────────────

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    log.info(f"Callback from {user_id}: {data}")
    
    if data in LEAD_MAGNETS:
        magnet = LEAD_MAGNETS[data]
        
        # Send document
        file_path = magnet["file"]
        if file_path.exists():
            with open(file_path, "rb") as f:
                await context.bot.send_document(
                    chat_id=user_id,
                    document=f,
                    filename=f"{magnet['title']}.html",
                    caption=magnet["caption"],
                    parse_mode="HTML"
                )
        else:
            # Fallback: send text
            await context.bot.send_message(
                chat_id=user_id,
                text=magnet["caption"],
                parse_mode="HTML"
            )
        
        # Log to KC
        try:
            from kc_rag import upsert
            upsert(
                content=f"LEAD_MAGNET_SENT: {data} to user {user_id}",
                tags=["lead_magnet", "telegram", data, "delivered"],
                source="tg_webhook",
                confidence=0.95,
                verification_method="auto"
            )
        except Exception:
            pass
    
    log.info(f"Delivered {data} to user {user_id}")

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - show main menu."""
    user_id = update.effective_user.id
    
    keyboard = [
        [InlineKeyboardButton("🎁 Чек-лист автозаписи", callback_data="send_lead_magnet")],
        [InlineKeyboardButton("📖 Кейс салона на Дарнице", callback_data="send_case_study")],
        [InlineKeyboardButton("🤖 Пример бота", url="https://t.me/max_brain_chef_bot")],
        [InlineKeyboardButton("📢 Наш канал", url="https://t.me/max_brain_chef_official")],
    ]
    
    await update.message.reply_html(
        "👋 <b>MAX BRAIN CHEF</b> — автоматизация салонов и малого бизнеса.\n\n"
        "Выбери что нужно:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    log.info(f"/start from user {user_id}")

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors."""
    log.error(f"Error: {context.error}", exc_info=context.error)

# ─── Webhook Setup ──────────────────────────────────────────────────────

async def on_startup(app: Application):
    """Set webhook on startup."""
    await app.bot.set_webhook(
        url=f"{WEBHOOK_URL}{WEBHOOK_PATH}",
        allowed_updates=["callback_query", "message"],
        drop_pending_updates=True
    )
    log.info(f"Webhook set: {WEBHOOK_URL}{WEBHOOK_PATH}")

async def on_shutdown(app: Application):
    """Delete webhook on shutdown."""
    await app.bot.delete_webhook()
    log.info("Webhook deleted")

def main():
    """Main entry point."""
    if not BOT_TOKEN:
        log.error("TELEGRAM_BOT_TOKEN not set!")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_error_handler(handle_error)
    
    # Startup/shutdown
    application.post_init = on_startup
    application.post_shutdown = on_shutdown
    
    # Run webhook
    log.info(f"Starting webhook on {WEBAPP_HOST}:{WEBAPP_PORT}{WEBHOOK_PATH}")
    application.run_webhook(
        listen=WEBAPP_HOST,
        port=WEBAPP_PORT,
        url_path=WEBHOOK_PATH.lstrip("/"),
        webhook_url=f"{WEBHOOK_URL}{WEBHOOK_PATH}",
    )

if __name__ == "__main__":
    main()