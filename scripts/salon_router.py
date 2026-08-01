#!/usr/bin/env python3
"""
Salon Router — aiogram 3.x Router for mounting into gateway Dispatcher.
Same token, same polling, zero conflict.

> Revisit: when salon router logic, command routing, or handler dispatch changes. Last touched: 2026-07-02.

Mount in gateway:
    from salon_router import salon_router
    dp.include_router(salon_router)
"""
import os
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

logger = logging.getLogger("salon")

# Config
DB_PATH = Path(__file__).parent / "salon_bookings.db"

# Services
SERVICES = [
    {"id": "haircut_m", "name": "Стрижка мужская", "duration": 30, "price": 800},
    {"id": "haircut_f", "name": "Стрижка женская", "duration": 60, "price": 1500},
    {"id": "coloring", "name": "Окрашивание", "duration": 120, "price": 3000},
    {"id": "manicure", "name": "Маникюр", "duration": 60, "price": 1200},
    {"id": "pedicure", "name": "Педикюр", "duration": 90, "price": 1500},
    {"id": "styling", "name": "Укладка", "duration": 45, "price": 1000},
    {"id": "shave", "name": "Бритьё", "duration": 30, "price": 600},
    {"id": "brow_lam", "name": "Ламинирование бровей", "duration": 60, "price": 2000},
]
WORK_HOURS = {"start": 9, "end": 20}
WORK_DAYS = [0, 1, 2, 3, 4, 5]  # Пн-Сб

# FSM States
class BookingForm(StatesGroup):
    choosing_service = State()
    choosing_date = State()
    choosing_time = State()
    confirming = State()

# Database
def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            service TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'confirmed',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_bookings_for_date(date_str):
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT time, service FROM bookings WHERE date=? AND status='confirmed'",
        (date_str,)
    ).fetchall()
    conn.close()
    return rows

def create_booking(user_id, username, service, date_str, time_str):
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT INTO bookings (user_id, username, service, date, time) VALUES (?, ?, ?, ?, ?)",
        (user_id, username, service, date_str, time_str)
    )
    conn.commit()
    conn.close()

def cancel_booking(user_id, date_str, time_str):
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "UPDATE bookings SET status='cancelled' WHERE user_id=? AND date=? AND time=? AND status='confirmed'",
        (user_id, date_str, time_str)
    )
    conn.commit()
    conn.close()

# Router
salon_router = Router(name="salon")

@salon_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Check if this is a salon-related command, otherwise ignore."""
    text = message.text or ""
    if text == "/start":
        # Show main menu with salon option
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💇 Записаться в салон", callback_data="salon_book")]
        ])
        await message.answer(
            "Добро пожаловать! Выберите действие:",
            reply_markup=kb
        )

@salon_router.message(Command("salon"))
async def cmd_salon(message: Message, state: FSMContext):
    """Direct salon booking command."""
    await show_services(message)

@salon_router.callback_query(F.data == "salon_book")
async def cb_salon_book(callback: CallbackQuery, state: FSMContext):
    await show_services(callback.message)
    await callback.answer()

async def show_services(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{s['name']} — {s['price']}₽ ({s['duration']}мин)",
            callback_data=f"svc_{s['id']}"
        )]
        for s in SERVICES
    ])
    await message.answer("Выберите услугу:", reply_markup=kb)

@salon_router.callback_query(F.data.startswith("svc_"))
async def cb_choose_service(callback: CallbackQuery, state: FSMContext):
    svc_id = callback.data.replace("svc_", "")
    svc = next((s for s in SERVICES if s["id"] == svc_id), None)
    if not svc:
        await callback.answer("Услуга не найдена")
        return

    await state.update_data(service=svc["name"], duration=svc["duration"], price=svc["price"])

    # Show dates for next 7 days
    today = datetime.now()
    buttons = []
    for i in range(1, 8):
        day = today + timedelta(days=i)
        if day.weekday() in WORK_DAYS:
            buttons.append([InlineKeyboardButton(
                text=day.strftime("%a %d.%m"),
                callback_data=f"date_{day.strftime('%Y-%m-%d')}"
            )])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.answer(f"Услуга: {svc['name']} ({svc['price']}₽)\nВыберите дату:", reply_markup=kb)
    await state.set_state(BookingForm.choosing_date)
    await callback.answer()

@salon_router.callback_query(F.data.startswith("date_"))
async def cb_choose_date(callback: CallbackQuery, state: FSMContext):
    date_str = callback.data.replace("date_", "")
    await state.update_data(date=date_str)

    # Get available time slots
    booked = get_bookings_for_date(date_str)
    booked_times = {b[0] for b in booked}

    buttons = []
    for hour in range(WORK_HOURS["start"], WORK_HOURS["end"]):
        for minute in [0, 30]:
            time_str = f"{hour:02d}:{minute:02d}"
            if time_str not in booked_times:
                buttons.append([InlineKeyboardButton(text=time_str, callback_data=f"time_{time_str}")])

    if not buttons:
        await callback.message.answer("Нет свободных слотов на эту дату. Выберите другую.")
        await callback.answer()
        return

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.answer("Выберите время:", reply_markup=kb)
    await state.set_state(BookingForm.choosing_time)
    await callback.answer()

@salon_router.callback_query(F.data.startswith("time_"))
async def cb_choose_time(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data.replace("time_", "")
    await state.update_data(time=time_str)

    data = await state.get_data()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_yes")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="confirm_no")],
    ])
    await callback.message.answer(
        f"📋 Запись:\n"
        f"Услуга: {data['service']}\n"
        f"Дата: {data['date']}\n"
        f"Время: {time_str}\n"
        f"Цена: {data['price']}₽\n\n"
        f"Подтвердить?",
        reply_markup=kb
    )
    await state.set_state(BookingForm.confirming)
    await callback.answer()

@salon_router.callback_query(F.data == "confirm_yes", BookingForm.confirming)
async def cb_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = callback.from_user
    create_booking(
        user_id=user.id,
        username=user.username or user.first_name,
        service=data["service"],
        date_str=data["date"],
        time_str=data["time"]
    )
    await callback.message.answer(
        f"✅ Запись создана!\n"
        f"{data['service']} — {data['date']} в {data['time']}\n"
        f"Ждём вас! 💇"
    )
    await state.clear()
    await callback.answer()

@salon_router.callback_query(F.data == "confirm_no", BookingForm.confirming)
async def cb_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Запись отменена.")
    await state.clear()
    await callback.answer()

@salon_router.message(Command("my_bookings"))
async def cmd_my_bookings(message: Message):
    """Show user's active bookings."""
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT service, date, time FROM bookings WHERE user_id=? AND status='confirmed' ORDER BY date, time",
        (message.from_user.id,)
    ).fetchall()
    conn.close()

    if not rows:
        await message.answer("У вас нет активных записей.")
        return

    lines = [f"📋 Ваши записи:\n"]
    for svc, date, time in rows:
        lines.append(f"• {svc} — {date} в {time}")
    await message.answer("\n".join(lines))

# Initialize DB on import
init_db()
logger.info("Salon router loaded, DB initialized")
