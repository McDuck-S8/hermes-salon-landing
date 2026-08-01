"""
Salon Bot — Entry Point (2026)
Backend Architect 🏗️
"""

import asyncio
import logging
import sys
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession

from config import config
from bot.handlers import client, admin, master, webapp, fun
import bot.db as db
from aiogram.exceptions import TelegramBadRequest

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("salon-bot")


async def main():
    # Verify token
    if not config.BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не установлен!")
        logger.error("   Установите переменную окружения BOT_TOKEN или пропишите в config.py")
        sys.exit(1)

    if config.SUPERADMIN_ID == 0:
        logger.warning("⚠️  SUPERADMIN_ID не установлен. /admin будет недоступен.")

    # Init DB
    logger.info(f"📦 База данных: {config.DB_PATH}")
    Path(config.DB_PATH).parent.mkdir(parents=True, exist_ok=True)

    # Proxy session (SOCKS5 через aiohttp-socks)
    if config.PROXY:
        logger.info(f"🔌 Прокси: {config.PROXY}")
        session = AiohttpSession(proxy=config.PROXY)
    else:
        session = AiohttpSession()

    bot = Bot(token=config.BOT_TOKEN, session=session)
    dp = Dispatcher(storage=MemoryStorage())

    # Register routers
    dp.include_router(admin.router)
    dp.include_router(master.router)
    dp.include_router(client.router)
    dp.include_router(webapp.router)
    dp.include_router(fun.router)

    # Global error handler: "no text to edit" → send new message instead of crash
    from aiogram.types import ErrorEvent

    @dp.error()
    async def handle_errors(event: ErrorEvent):
        """Catch TelegramBadRequest when edit_text on photo messages."""
        exc = event.exception
        if not isinstance(exc, TelegramBadRequest):
            return
        if "there is no text in the message to edit" not in str(exc):
            return
        update = event.update
        if update.callback_query:
            cb = update.callback_query
            await cb.answer()
            try:
                from bot.keyboards import main_menu_kb
                await cb.message.answer(
                    "🏠 <b>Выберите действие:</b>",
                    reply_markup=main_menu_kb(),
                    parse_mode="HTML",
                )
            except Exception:
                pass

    # Seed demo data
    await db.seed_demo()
    logger.info("✅ Демо-данные загружены")

    # Set bot commands
    from aiogram.types import BotCommand
    await bot.set_my_commands([
        BotCommand(command="start", description="🏠 Главное меню"),
        BotCommand(command="admin", description="🔧 Панель администратора"),
        BotCommand(command="master", description="👩‍🎨 Панель мастера"),
        BotCommand(command="webapp", description="🌐 Mini App запись"),
    ])

    logger.info(f"🤖 {config.SALON_NAME} запущен!")
    logger.info(f"📍 {config.SALON_ADDRESS}")
    logger.info(f"📞 {config.SALON_PHONE}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен")
