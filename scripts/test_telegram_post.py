#!/usr/bin/env python3
"""
Test Telegram posting with the configured bot and channels.
"""
import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

CHANNELS = {
    "max_brain_chef_official": -1003777013964,
    "ai_frontier_you": -1003705792421,
    "max_brain_chef_ai": -1003882833000,
    "neuro_kitchen_ai": -1003525498743,
}

async def test_post():
    bot = Bot(token=BOT_TOKEN)
    
    # Test message with inline keyboard
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎁 Забрать чек-лист", callback_data="get_checklist"),
        InlineKeyboardButton("🤖 Получить бота", callback_data="get_bot"),
    ]])
    
    text = (
        "🚀 <b>Кейс: Салон на Дарнице — +40% повторок за 2 недели без рекламы</b>\n\n"
        "🔴 <b>БЫЛО:</b> No-show 25%, админ 6ч/нед на звонки, теряли 15 клиентов/мес\n"
        "🟢 <b>СТАЛО:</b> No-show 5%, админ 0ч, +12 клиентов возвращено, +42к грн/мес\n\n"
        "🛠 <b>Что сделали за 1 вечер (бесплатно):</b>\n"
        "1. Подключили @Manybot (бесплатно)\n"
        "2. 3 цепочки: напоминание 24ч/2ч + возврат 21 день + апсейл\n"
        "3. Google Таблицы как CRM\n"
        "4. Кнопка «Записаться» в Инстаграм\n\n"
        "💰 <b>Экономия ~30к грн/мес + доп. выручка 42к</b>\n\n"
        "👇 Хочешь повторить? Жми кнопку — скину чек-лист и шаблоны:"
    )
    
    for name, chat_id in CHANNELS.items():
        try:
            msg = await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
            print(f"✅ {name}: Message sent (msg_id: {msg.message_id})")
        except Exception as e:
            print(f"❌ {name}: {e}")

if __name__ == "__main__":
    asyncio.run(test_post())