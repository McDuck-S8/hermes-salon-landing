"""
Salon Bot — Watchdog
Checks if the bot is alive via Telegram API every 5 minutes (via Hermes cron).
Restarts if unresponsive.
No bot.close() — avoids flood control on repeated checks.
"""
import asyncio
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import config
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession


async def check_bot() -> bool:
    """Check if bot responds to API calls. No close() to avoid flood limit."""
    try:
        session = AiohttpSession(proxy=config.PROXY) if config.PROXY else AiohttpSession()
        bot = Bot(token=config.BOT_TOKEN, session=session)
        me = await bot.get_me()
        # Don't close — flood control on rapid checks
        if me:
            return True
        return False
    except Exception as e:
        print(f"Bot check failed: {e}")
        return False


def restart_bot():
    """Start bot as background process."""
    log_path = PROJECT_ROOT / "data" / "bot.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = f'cd "{PROJECT_ROOT}" && python -u main.py >> "{log_path}" 2>&1'
    subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Bot started. Log: {log_path}")


async def main():
    alive = await check_bot()
    if alive:
        # Silent exit = bot is healthy
        return

    print("BOT NOT RESPONDING — restarting...")
    restart_bot()
    await asyncio.sleep(8)
    alive = await check_bot()
    if alive:
        print("✓ Bot restarted successfully")
    else:
        print("✗ Restart FAILED — manual intervention needed")


if __name__ == "__main__":
    asyncio.run(main())
