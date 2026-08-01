#!/usr/bin/env python3
"""
PRODUCTION Telegram Bot for Crimea Hotels
FIXED VERSION - no syntax errors
Stack: aiogram + SQLite
"""

import os
import sqlite3
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ============ CONFIG ============
# Get token from environment or use placeholder
BOT_TOKEN=os.environ.get("TELEGRAM_BOT_TOKEN", "8645168670:AAG_wrpmbyKcqE5PCe192k5WWWV-swl6dug")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
HOTEL_NAME = os.environ.get("HOTEL_NAME", "Отель «Черноморский»")

# ============ DATABASE ============
def init_db():
    conn = sqlite3.connect("hotel_bot.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price INTEGER,
            description TEXT,
            available INTEGER DEFAULT 1
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER,
            guest_name TEXT,
            guest_phone TEXT,
            check_in TEXT,
            check_out TEXT,
            guests INTEGER,
            total_price INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES rooms(id)
        )
    """)
    
    # Insert default rooms if empty
    c.execute("SELECT COUNT(*) FROM rooms")
    if c.fetchone()[0] == 0:
        rooms = [
            (1, "Стандарт", 3500, "Уютный номер с видом на сад", 5),
            (2, "Комфорт", 5000, "Просторный номер с балконом", 3),
            (3, "Люкс", 8000, "Роскошный номер с панорамным видом на море", 2),
        ]
        c.executemany("INSERT INTO rooms (id, name, price, description, available) VALUES (?, ?, ?, ?, ?)", rooms)
    
    conn.commit()
    conn.close()

# ============ STATES ============
class BookingStates(StatesGroup):
    choosing_room = State()
    entering_name = State()
    entering_phone = State()
    entering_checkin = State()
    entering_checkout = State()
    entering_guests = State()
    confirming = State()

# ============ BOT ============
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ============ KEYBOARDS ============
def main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏨 Наши номера"), KeyboardButton(text="📅 Забронировать")],
            [KeyboardButton(text="📋 Мои бронирования"), KeyboardButton(text="📞 Контакты")],
            [KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True
    )

def rooms_kb():
    conn = sqlite3.connect("hotel_bot.db")
    c = conn.cursor()
    c.execute("SELECT id, name, price, available FROM rooms WHERE available > 0")
    rooms = c.fetchall()
    conn.close()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for room in rooms:
        kb.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{room[1]} - {room[2]}rub/night ({room[3]} avail)",
                callback_data=f"room_{room[0]}"
            )
        ])
    return kb

# ============ HANDLERS ============
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome = f"""🏨 Добро пожаловать в {HOTEL_NAME}!

Я помогу вам:
• Посмотреть наши номера и цены
• Забронировать номер
• Проверить статус бронирования
• Связаться с администратором

Выберите действие в меню ниже 👇"""
    
    await message.answer(welcome, reply_markup=main_kb())

@dp.message(F.text == "🏨 Наши номера")
async def show_rooms(message: types.Message):
    conn = sqlite3.connect("hotel_bot.db")
    c = conn.cursor()
    c.execute("SELECT name, price, description, available FROM rooms")
    rooms = c.fetchall()
    conn.close()
    
    text = "🏠 Наши номера:\n\n"
    for room in rooms:
        status = "✅ Доступен" if room[3] > 0 else "❌ Занят"
        text += f"• {room[0]} — {room[1]}₽/ночь\n"
        text += f"  {room[2]}\n"
        text += f"  {status}\n\n"
    
    text += 'Нажмите "📅 Забронировать" чтобы забронировать номер'
    await message.answer(text)

@dp.message(F.text == "📅 Забронировать")
async def start_booking(message: types.Message, state: FSMContext):
    await message.answer("Выберите номер:", reply_markup=rooms_kb())
    await state.set_state(BookingStates.choosing_room)

@dp.callback_query(F.data.startswith("room_"))
async def choose_room(callback: types.CallbackQuery, state: FSMContext):
    room_id = int(callback.data.split("_")[1])
    await state.update_data(room_id=room_id)
    await callback.message.answer("Введите ваше имя:")
    await state.set_state(BookingStates.entering_name)

@dp.message(BookingStates.entering_name)
async def enter_name(message: types.Message, state: FSMContext):
    await state.update_data(guest_name=message.text)
    await message.answer("Введите ваш телефон (с +7):")
    await state.set_state(BookingStates.entering_phone)

@dp.message(BookingStates.entering_phone)
async def enter_phone(message: types.Message, state: FSMContext):
    await state.update_data(guest_phone=message.text)
    await message.answer("Дата заезда (ДД.ММ.ГГГГ):")
    await state.set_state(BookingStates.entering_checkin)

@dp.message(BookingStates.entering_checkin)
async def enter_checkin(message: types.Message, state: FSMContext):
    try:
        datetime.strptime(message.text, "%d.%m.%Y")
        await state.update_data(check_in=message.text)
        await message.answer("Дата выезда (ДД.ММ.ГГГГ):")
        await state.set_state(BookingStates.entering_checkout)
    except ValueError:
        await message.answer("❌ Неверный формат. Используйте ДД.ММ.ГГГГ")

@dp.message(BookingStates.entering_checkout)
async def enter_checkout(message: types.Message, state: FSMContext):
    try:
        datetime.strptime(message.text, "%d.%m.%Y")
        await state.update_data(check_out=message.text)
        await message.answer("Количество гостей:")
        await state.set_state(BookingStates.entering_guests)
    except ValueError:
        await message.answer("❌ Неверный формат. Используйте ДД.ММ.ГГГГ")

@dp.message(BookingStates.entering_guests)
async def enter_guests(message: types.Message, state: FSMContext):
    try:
        guests = int(message.text)
        await state.update_data(guests=guests)
        
        data = await state.get_data()
        
        # Calculate price
        conn = sqlite3.connect("hotel_bot.db")
        c = conn.cursor()
        c.execute("SELECT name, price FROM rooms WHERE id = ?", (data["room_id"],))
        room = c.fetchone()
        conn.close()
        
        d1 = datetime.strptime(data["check_in"], "%d.%m.%Y")
        d2 = datetime.strptime(data["check_out"], "%d.%m.%Y")
        nights = (d2 - d1).days
        total = room[1] * nights
        
        text = f"""📋 Подтвердите бронирование:

🏨 Номер: {room[0]}
📅 Заезд: {data["check_in"]}
📅 Выезд: {data["check_out"]}
🌙 Ночей: {nights}
👥 Гостей: {guests}
💰 Сумма: {total}₽

👤 Имя: {data["guest_name"]}
📱 Телефон: {data["guest_phone"]}

Всё верно?"""
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_booking")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_booking")]
        ])
        
        await message.answer(text, reply_markup=kb)
        await state.update_data(total_price=total)
        await state.set_state(BookingStates.confirming)
    except ValueError:
        await message.answer("❌ Введите число")

@dp.callback_query(F.data == "confirm_booking")
async def confirm_booking(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    conn = sqlite3.connect("hotel_bot.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO bookings (room_id, guest_name, guest_phone, check_in, check_out, guests, total_price, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'confirmed')
    """, (data["room_id"], data["guest_name"], data["guest_phone"], 
          data["check_in"], data["check_out"], data["guests"], data["total_price"]))
    
    booking_id = c.lastrowid
    
    # Decrease available rooms
    c.execute("UPDATE rooms SET available = available - 1 WHERE id = ?", (data["room_id"],))
    conn.commit()
    conn.close()
    
    await callback.message.answer(f"""✅ Бронирование #{booking_id} подтверждено!

Мы свяжемся с вами для уточнения деталей.

Спасибо, что выбрали {HOTEL_NAME}! 🏨""", reply_markup=main_kb())
    
    # Notify admin
    if ADMIN_ID:
        await bot.send_message(ADMIN_ID, f"🔔 Новое бронирование #{booking_id}!\n\nИмя: {data['guest_name']}\nТелефон: {data['guest_phone']}")
    
    await state.clear()

@dp.callback_query(F.data == "cancel_booking")
async def cancel_booking(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Бронирование отменено.", reply_markup=main_kb())
    await state.clear()

@dp.message(F.text == "📞 Контакты")
async def show_contacts(message: types.Message):
    await message.answer(f"""📞 Контакты {HOTEL_NAME}:

📱 Телефон: +7 978 123 45 67
📧 Email: info@hotel-crimea.ru
📍 Адрес: г. Ялта, ул. Ленина, 10
🌐 Сайт: hotel-crimea.ru

⏰ Работаем круглосуточно!""")

@dp.message(F.text == "❓ Помощь")
async def show_help(message: types.Message):
    await message.answer("""❓ Помощь:

• 🏨 Наши номера — посмотреть номера и цены
• 📅 Забронировать — забронировать номер
• 📋 Мои бронирования — проверить статус
• 📞 Контакты — связаться с нами

Если остались вопросы — напишите нам!""")

# ============ MAIN ============
async def main():
    import sys
    print("BOT STARTING...", flush=True, file=sys.stderr)
    print(f"Token: {os.environ.get('BOT_TOKEN', 'NOT SET')[:15]}...", flush=True, file=sys.stderr)
    init_db()
    logging.info(f"Bot {HOTEL_NAME} started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
