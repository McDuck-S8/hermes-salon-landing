#!/usr/bin/env python3
"""
Production Telegram Bot Template
Stack: aiogram 3.x + SQLite + SOCKS5 proxy support
Features: FSM, inline keyboards, booking flow, admin notifications

Usage:
1. Get token from @BotFather
2. Set BOT_TOKEN env var
3. Set TELEGRAM_PROXY env var if in RF (api.telegram.org blocked)
4. Run: python production_bot_template.py
"""

import os
import sqlite3
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ============ CONFIG ============
BOT_TOKEN = os.env...N", "YOUR_BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
BUSINESS_NAME = os.environ.get("BUSINESS_NAME", "My Business")
TELEGRAM_PROXY = os.environ.get("TELEGRAM_PROXY", "")  # socks5://user:pass@host:port

# ============ DATABASE ============
def init_db():
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price INTEGER,
            description TEXT,
            available INTEGER DEFAULT 1
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id INTEGER,
            customer_name TEXT,
            customer_phone TEXT,
            details TEXT,
            total_price INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (service_id) REFERENCES services(id)
        )
    """)

    c.execute("SELECT COUNT(*) FROM services")
    if c.fetchone()[0] == 0:
        services = [
            (1, "Basic Package", 5000, "Basic service package"),
            (2, "Standard Package", 10000, "Standard service package"),
            (3, "Premium Package", 20000, "Premium service package"),
        ]
        c.executemany(
            "INSERT INTO services (id, name, price, description) VALUES (?, ?, ?, ?)",
            services
        )

    conn.commit()
    conn.close()

# ============ STATES ============
class OrderStates(StatesGroup):
    choosing_service = State()
    entering_name = State()
    entering_phone = State()
    entering_details = State()
    confirming = State()

# ============ BOT (created in main() for proxy support) ============
bot = None
dp = Dispatcher(storage=MemoryStorage())

# ============ KEYBOARDS ============
def main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Services"), KeyboardButton(text="Place Order")],
            [KeyboardButton(text="My Orders"), KeyboardButton(text="Contact Us")],
            [KeyboardButton(text="Help")]
        ],
        resize_keyboard=True
    )

def services_kb():
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("SELECT id, name, price, available FROM services WHERE available > 0")
    services = c.fetchall()
    conn.close()

    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for svc in services:
        kb.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{svc[1]} - ${svc[2]}",
                callback_data=f"service_{svc[0]}"
            )
        ])
    return kb

# ============ HANDLERS ============
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Welcome to {BUSINESS_NAME}!\n\n"
        "I can help you:\n"
        "• View our services and prices\n"
        "• Place an order\n"
        "• Check order status\n"
        "• Contact us\n\n"
        "Choose an option below:",
        reply_markup=main_kb()
    )

@dp.message(F.text == "Services")
async def show_services(message: types.Message):
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("SELECT name, price, description, available FROM services")
    services = c.fetchall()
    conn.close()

    text = "Our Services:\n\n"
    for svc in services:
        status = "Available" if svc[3] > 0 else "Unavailable"
        text += f"• {svc[0]} - ${svc[1]}\n  {svc[2]}\n  Status: {status}\n\n"
    text += 'Click "Place Order" to order'
    await message.answer(text)

@dp.message(F.text == "Place Order")
async def start_order(message: types.Message, state: FSMContext):
    await message.answer("Choose a service:", reply_markup=services_kb())
    await state.set_state(OrderStates.choosing_service)

@dp.callback_query(F.data.startswith("service_"))
async def choose_service(callback: types.CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split("_")[1])
    await state.update_data(service_id=service_id)
    await callback.message.answer("Enter your name:")
    await state.set_state(OrderStates.entering_name)

@dp.message(OrderStates.entering_name)
async def enter_name(message: types.Message, state: FSMContext):
    await state.update_data(customer_name=message.text)
    await message.answer("Enter your phone number:")
    await state.set_state(OrderStates.entering_phone)

@dp.message(OrderStates.entering_phone)
async def enter_phone(message: types.Message, state: FSMContext):
    await state.update_data(customer_phone=message.text)
    await message.answer("Describe your requirements:")
    await state.set_state(OrderStates.entering_details)

@dp.message(OrderStates.entering_details)
async def enter_details(message: types.Message, state: FSMContext):
    await state.update_data(details=message.text)
    data = await state.get_data()

    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("SELECT name, price FROM services WHERE id = ?", (data["service_id"],))
    service = c.fetchone()
    conn.close()

    await message.answer(
        f"Order Summary:\n\n"
        f"Service: {service[0]}\nPrice: ${service[1]}\n"
        f"Name: {data['customer_name']}\nPhone: {data['customer_phone']}\n"
        f"Details: {data['details']}\n\nConfirm?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Confirm", callback_data="confirm_order")],
            [InlineKeyboardButton(text="Cancel", callback_data="cancel_order")]
        ])
    )
    await state.update_data(total_price=service[1])
    await state.set_state(OrderStates.confirming)

@dp.callback_query(F.data == "confirm_order")
async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO orders (service_id, customer_name, customer_phone, details, total_price, status)
        VALUES (?, ?, ?, ?, ?, 'confirmed')
    """, (data["service_id"], data["customer_name"], data["customer_phone"],
          data["details"], data["total_price"]))
    order_id = c.lastrowid
    conn.commit()
    conn.close()

    await callback.message.answer(
        f"Order #{order_id} confirmed!\n\n"
        f"We will contact you shortly.\n"
        f"Thank you for choosing {BUSINESS_NAME}!",
        reply_markup=main_kb()
    )

    if ADMIN_ID:
        await bot.send_message(
            ADMIN_ID,
            f"New order #{order_id}!\n\n"
            f"Name: {data['customer_name']}\n"
            f"Phone: {data['customer_phone']}"
        )
    await state.clear()

@dp.callback_query(F.data == "cancel_order")
async def cancel_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Order cancelled.", reply_markup=main_kb())
    await state.clear()

@dp.message(F.text == "Contact Us")
async def show_contacts(message: types.Message):
    await message.answer(
        f"Contact {BUSINESS_NAME}:\n\n"
        "Phone: +7 XXX XXX XX XX\nEmail: info@example.com\n"
        "Address: City, Street, 1\n\nWe are available 24/7!"
    )

@dp.message(F.text == "Help")
async def show_help(message: types.Message):
    await message.answer(
        "Help:\n\n• Services - view services and prices\n"
        "• Place Order - place an order\n• My Orders - check order status\n"
        "• Contact Us - contact information\n\nIf you have questions, write to us!"
    )

# ============ MAIN ============
async def main():
    global bot
    init_db()

    # Create bot with SOCKS5 proxy if configured (required in RF)
    if TELEGRAM_PROXY:
        from aiogram.client.session.aiohttp import AiohttpSession
        session = AiohttpSession(proxy=TELEGRAM_PROXY)
        bot = Bot(token=BOT_TOKEN, session=session)
        logging.info(f"Bot {BUSINESS_NAME} started with proxy")
    else:
        bot = Bot(token=BOT_TOKEN)
        logging.info(f"Bot {BUSINESS_NAME} started (direct)")

    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
