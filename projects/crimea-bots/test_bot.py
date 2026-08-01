
import asyncio
import os

async def test():
    from aiogram import Bot
    
    token = os.environ.get("BOT_TOKEN", "8645168670:***")
    print(f"Token: {token[:10]}...{token[-5:]}")
    
    bot = Bot(token=token)
    try:
        me = await bot.get_me()
        print(f"Bot username: @{me.username}")
        print(f"Bot name: {me.first_name}")
        print(f"Bot ID: {me.id}")
        print("SUCCESS: Telegram API works!")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        await bot.session.close()

asyncio.run(test())
