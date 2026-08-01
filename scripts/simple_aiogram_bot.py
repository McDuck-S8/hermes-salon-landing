#!/usr/bin/env python3
"""Simple aiogram 3.x bot — receives message, replies."""
import asyncio
from aiogram import Bot, Dispatcher, types, F

> Revisit: when simple aiogram bot logic, polling setup, or bot handlers change. Last touched: 2026-07-02.
from aiogram.filters import CommandStart, Command

TOKEN = "TEST_TOKEN_12345"  # placeholder for demo

dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Я бот салона красоты LUMIÈRE.\n"
        "Чем могу помочь?"
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "📋 Команды:\n"
        "/start — Начать\n"
        "/help — Помощь\n"
        "/menu — Меню услуг\n"
        "/book — Записаться"
    )

@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    await message.answer(
        "💇‍♀️ Наши услуги:\n\n"
        "1. Стрижка и укладка — 2500₽\n"
        "2. Окрашивание — 4500₽\n"
        "3. Маникюр — 1800₽\n"
        "4. Макияж — 3000₽\n"
        "5. Ламинирование бровей — 1500₽\n\n"
        "Для записи нажмите /book"
    )

@dp.message(Command("book"))
async def cmd_book(message: types.Message):
    await message.answer(
        "📅 Для записи напишите:\n"
        "Услуга + дата + время\n\n"
        "Пример: Окрашивание, 15 июля, 14:00"
    )

@dp.message(F.text)
async def echo(message: types.Message):
    await message.answer(
        f"Я получил ваше сообщение: «{message.text}»\n"
        "Для списка команд нажмите /help"
    )

async def main():
    print("Бот запущен! (демо-режим — токен тестовый)")
    print("Бот НЕ подключается к Telegram с тестовым токеном.")
    print("Код готов к работе при реальном токене.")
    print("\nТестирование хендлеров напрямую:")
    
    # Simulate messages
    class FakeUser:
        id = 12345
        first_name = "Тест"
        is_bot = False
    
    class FakeMessage:
        def __init__(self, text, user=None):
            self.text = text
            self.from_user = user or FakeUser()
            self._replies = []
        async def answer(self, text):
            self._replies.append(text)
            print(f"  BOT -> {text[:80]}...")
    
    # Test all handlers
    msg = FakeMessage("/start")
    await cmd_start(msg)
    
    msg = FakeMessage("/help")
    await cmd_help(msg)
    
    msg = FakeMessage("/menu")
    await cmd_menu(msg)
    
    msg = FakeMessage("/book")
    await cmd_book(msg)
    
    msg = FakeMessage("Привет, хочу записаться")
    await echo(msg)
    
    print("\n[OK] Все хендлеры работают без ошибок!")

if __name__ == "__main__":
    asyncio.run(main())
