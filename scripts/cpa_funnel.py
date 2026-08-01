#!/usr/bin/env python3
"""Telegram CPA Funnel Bot — aiogram 3.x.

Funnel: traffic source → bot welcome → channel warmup → offer
5 touchpoints before the offer link.

Usage:
    export CPA_BOT_TOKEN="..."
    python scripts/cpa_funnel.py          # start polling

Configuration via env vars:
    CPA_BOT_TOKEN       — required
    CPA_WARMUP_CHANNEL  — @channel or invite link (optional)
    CPA_OFFER_URL       — target offer URL (optional)
"""
import asyncio
import os
import sys
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = os.environ.get("CPA_BOT_TOKEN", "")
WARMUP_CHANNEL = os.environ.get("CPA_WARMUP_CHANNEL", "https://t.me/+cpa_warmup")
OFFER_URL = os.environ.get("CPA_OFFER_URL", "")

if not TOKEN:
    print("FATAL: CPA_BOT_TOKEN not set", file=sys.stderr)
    sys.exit(1)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# ── FSM ──────────────────────────────────────────────────────
class Funnel(StatesGroup):
    entered = State()
    warmed = State()
    offered = State()


# ── Keyboards ─────────────────────────────────────────────────
def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Что я предлагаю", callback_data="offer")],
        [InlineKeyboardButton(text="📢 Канал с кейсами", url=WARMUP_CHANNEL)],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
    ])


def channel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться", url=WARMUP_CHANNEL)],
        [InlineKeyboardButton(text="✅ Уже подписан", callback_data="subscribed")],
    ])


def offer_kb():
    kb = []
    if OFFER_URL:
        kb.append([InlineKeyboardButton(text="🚀 Перейти к офферу", url=OFFER_URL)])
    kb.append([InlineKeyboardButton(text="🔁 Показать ещё раз", callback_data="offer")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


# ── Handlers ──────────────────────────────────────────────────
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    user = message.from_user
    await state.set_state(Funnel.entered)
    await state.update_data(entered_at=datetime.now().isoformat())

    await message.answer(
        f"👋 Привет, {user.first_name}!\n\n"
        "Я — CPA-воронка. Здесь всё просто:\n"
        "1. Узнаёшь про оффер\n"
        "2. Подписываешься на канал с кейсами\n"
        "3. Получаешь ссылку\n\n"
        "Это займёт 2 минуты.",
        reply_markup=main_kb(),
    )


@dp.callback_query(F.data == "offer")
async def cb_offer(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(offer_shown_at=datetime.now().isoformat())

    await callback.message.edit_text(
        "🔥 **Что за оффер?**\n\n"
        "[Описание продукта/услуги]\n\n"
        "— Высокая конверсия\n"
        "— Прозрачная статистика\n"
        "— Выплаты вовремя\n\n"
        "Но сначала — подпишись на канал с реальными кейсами:",
        parse_mode="Markdown",
        reply_markup=channel_kb(),
    )


@dp.callback_query(F.data == "subscribed")
async def cb_subscribed(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    cur = await state.get_state()
    if cur == Funnel.warmed.state:
        await callback.message.edit_text(
            "✅ Уже прогреты! Держи ссылку:",
            reply_markup=offer_kb(),
        )
        return

    await state.set_state(Funnel.warmed)

    # Sequence of warmup messages — 5 touchpoints
    touchpoints = [
        ("📊 Кейс #1", "Как один клик принёс +340% к конверсии\n\n[контент кейса]"),
        ("💡 Инсайт", "Секрет высоких CR: правильный триггер в первые 3 секунды"),
        ("📈 Кейс #2", "Бюджет $200 → результат $1,280 за неделю\n\n[подробности]"),
        ("🎯 Почему сейчас", "Рынок растёт, конкуренция низкая. Окно возможностей — до конца квартала."),
        ("🚀 Последний шаг", "Всё, прогрев пройден. Забирай ссылку:"),
    ]

    for title, text in touchpoints:
        await callback.message.answer(f"**{title}**\n\n{text}", parse_mode="Markdown")
        await asyncio.sleep(1.5)

    await state.set_state(Funnel.offered)
    await callback.message.answer(
        "Вот твоя персональная ссылка:",
        reply_markup=offer_kb(),
    )


@dp.callback_query(F.data == "help")
async def cb_help(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Команды:\n"
        "/start — начать заново\n"
        "Кнопки ниже — навигация по воронке",
        reply_markup=main_kb(),
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "/start — начать заново\n"
        "/stats — моя статистика"
    )


@dp.message(Command("stats"))
async def cmd_stats(message: types.Message, state: FSMContext):
    data = await state.get_data()
    entered = data.get("entered_at", "неизвестно")
    await message.answer(
        f"📊 Твоя статистика:\n"
        f"• Вошёл: {entered[:19]}\n"
        f"• Этап: {await state.get_state() or 'начало'}"
    )


# ── Fallback ──────────────────────────────────────────────────
@dp.message()
async def fallback(message: types.Message):
    await message.answer(
        "Используй кнопки ниже 👇",
        reply_markup=main_kb(),
    )


# ── Main ──────────────────────────────────────────────────────
async def main():
    print(f"[{datetime.now():%H:%M:%S}] CPA Funnel Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
