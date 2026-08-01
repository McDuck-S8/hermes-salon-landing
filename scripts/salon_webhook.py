#!/usr/bin/env python3
"""
Salon Webhook Server — aiogram 3.x with webhook mode.
Runs on port 8443, same bot token as gateway, no polling conflict.

> Revisit: when salon webhook logic, HTTP endpoints, or callback handling changes. Last touched: 2026-07-02.

Gateway handles regular messages via polling.
This server handles salon-specific webhook calls.

Actually: this is STANDALONE. Run it instead of gateway for salon testing.
When ready: gateway + salon coexist via webhook path routing.
"""
import os
import sys
import logging
import asyncio
from pathlib import Path

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    Update,
    WebhookInfo,
)
from aiohttp import web

# Import salon router
sys.path.insert(0, str(Path(__file__).parent))
from salon_router import salon_router, SERVICES, get_bookings_for_date, create_booking

# Config
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_HOST = os.environ.get("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT = int(os.environ.get("WEBHOOK_PORT", "8443"))
WEBHOOK_PATH = "/salon"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")  # External URL for Telegram
PROXY = os.environ.get("PROXY", "")

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("salon_webhook")


async def on_startup(app):
    """Set webhook on Telegram."""
    bot = app["bot"]
    if WEBHOOK_URL:
        webhook_full = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
        await bot.set_webhook(webhook_full)
        logger.info(f"Webhook set: {webhook_full}")
    else:
        logger.warning("No WEBHOOK_URL set — webhook not configured. Use for testing only.")


async def on_shutdown(app):
    """Remove webhook."""
    bot = app["bot"]
    await bot.delete_webhook()
    logger.info("Webhook removed")


async def webhook_handler(request: web.Request):
    """Receive Telegram updates."""
    bot = request.app["bot"]
    dp = request.app["dp"]
    
    update_json = await request.json()
    update = Update.model_validate(update_json)
    
    await dp.feed_update(bot, update)
    
    return web.Response(status=200)


async def health(request: web.Request):
    """Health check."""
    return web.json_response({"status": "ok", "service": "salon"})


async def main():
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return
    
    # Create bot
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Create dispatcher with salon router
    dp = Dispatcher()
    dp.include_router(salon_router)
    
    # Create aiohttp app
    app = web.Application()
    app["bot"] = bot
    app["dp"] = dp
    
    app.router.add_post(WEBHOOK_PATH, webhook_handler)
    app.router.add_get("/health", health)
    
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_shutdown)
    
    logger.info(f"Starting salon webhook server on {WEBHOOK_HOST}:{WEBHOOK_PORT}")
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEBHOOK_HOST, WEBHOOK_PORT)
    await site.start()
    
    logger.info(f"Salon webhook running at {WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}")
    
    # Keep running
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
