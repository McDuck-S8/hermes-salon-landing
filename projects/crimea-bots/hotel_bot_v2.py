#!/usr/bin/env python3
"""
Hotel Bot v2 — Full-featured Telegram bot for Crimea hotel
Stack: aiogram 3.x + aiosqlite + SOCKS5 proxy
Features: booking, wheel of fortune, quiz, loyalty, daily check-in,
          photo gallery, admin notifications, SQLite database
"""

import os
import random
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional

import aiosqlite
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
    InputMediaPhoto,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ============================================================
# CONFIGURATION
# ============================================================
BOT_TOKEN=os.environ.get("BOT_TOKEN", os.environ.get("TELEGRAM_BOT_TOKEN", ""))
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
HOTEL_NAME = os.environ.get("HOTEL_NAME", 'Отель «Черноморский»')
DB_PATH = os.environ.get("DB_PATH", "hotel_bot_v2.db")

# SOCKS5 proxy for Russia (api.telegram.org often blocked)
PROXY_URL = os.environ.get(
    "TELEGRAM_PROXY",
    "socks5://user:pass@proxy.example.com:1080",
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("hotel_bot_v2")

# ============================================================
# GLOBALS
# ============================================================
bot: Optional[Bot] = None
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# ============================================================
# DATABASE (aiosqlite)
# ============================================================
async def init_db():
    """Create all tables and seed default data."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                full_name   TEXT,
                username    TEXT,
                points      INTEGER DEFAULT 0,
                level       INTEGER DEFAULT 1,
                referrals   INTEGER DEFAULT 0,
                last_checkin TEXT,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS rooms (
                id          INTEGER PRIMARY KEY,
                name        TEXT NOT NULL,
                price       INTEGER NOT NULL,
                description TEXT,
                photo_url   TEXT,
                available   INTEGER DEFAULT 5
            );

            CREATE TABLE IF NOT EXISTS bookings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                room_id     INTEGER,
                guest_name  TEXT,
                guest_phone TEXT,
                check_in    TEXT,
                check_out   TEXT,
                guests      INTEGER,
                total_price INTEGER,
                status      TEXT DEFAULT 'pending',
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_id) REFERENCES rooms(id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS quiz_progress (
                user_id     INTEGER PRIMARY KEY,
                score       INTEGER DEFAULT 0,
                current_q   INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS wheel_history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                prize       TEXT,
                spun_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)

        # Seed rooms if empty
        cursor = await db.execute("SELECT COUNT(*) FROM rooms")
        count = (await cursor.fetchone())[0]
        if count == 0:
            rooms = [
                (1, "Стандарт", 3500, "Уютный номер с видом на сад. Площадь 20 м², односпальная кровать, кондиционер, Wi-Fi.", None, 5),
                (2, "Комфорт", 5000, "Просторный номер с балконом. Площадь 30 м², двуспальная кровать, мини-бар, вид на море.", None, 3),
                (3, "Люкс", 8000, "Роскошный номер с панорамным видом на море. Площадь 50 м², джакuzzi, гостиная, терраса.", None, 2),
                (4, "Семейный", 6500, "Идеален для семьи. Площадь 40 м², две комнаты, детская кроватка по запросу.", None, 3),
                (5, "Президентский", 15000, "VIP-люкс на последнем этаже. 80 м², панорамные окна, персональный бассейн, бутылка шампанского.", None, 1),
            ]
            await db.executemany(
                "INSERT OR IGNORE INTO rooms (id, name, price, description, photo_url, available) VALUES (?,?,?,?,?,?)",
                rooms,
            )

        await db.commit()


async def ensure_user(user: types.User):
    """Register user in DB if not exists."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR IGNORE INTO users (user_id, full_name, username)
               VALUES (?, ?, ?)""",
            (user.id, user.full_name, user.username),
        )
        await db.commit()


async def get_user_points(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        return row[0] if row else 0


async def add_points(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET points = points + ? WHERE user_id=?",
            (amount, user_id),
        )
        # Auto-level up: every 100 points = +1 level
        await db.execute(
            """UPDATE users SET level = 1 + points / 100 WHERE user_id=?""",
            (user_id,),
        )
        await db.commit()


# ============================================================
# KEYBOARDS
# ============================================================
def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏨 Наши номера"), KeyboardButton(text="📅 Забронировать")],
            [KeyboardButton(text="🎰 Колесо фортуны"), KeyboardButton(text="🧠 Викторина о Крыму")],
            [KeyboardButton(text="🏆 Мои баллы"), KeyboardButton(text="✅ Ежедневный чек-ин")],
            [KeyboardButton(text="📸 Галерея"), KeyboardButton(text="📋 Мои бронирования")],
            [KeyboardButton(text="📞 Контакты"), KeyboardButton(text="❓ Помощь")],
        ],
        resize_keyboard=True,
    )


def rooms_inline_kb(rooms: list) -> InlineKeyboardMarkup:
    buttons = []
    for r in rooms:
        buttons.append([
            InlineKeyboardButton(
                text=f"{r[1]} — {r[2]}₽/ночь (свободно: {r[5]})",
                callback_data=f"room_{r[0]}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_booking_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="booking_confirm")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="booking_cancel")],
    ])


def quiz_answer_kb(answers: list) -> InlineKeyboardMarkup:
    buttons = []
    for i, ans in enumerate(answers):
        buttons.append([InlineKeyboardButton(text=ans, callback_data=f"quiz_{i}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# FSM STATES
# ============================================================
class BookingStates(StatesGroup):
    choosing_room = State()
    entering_name = State()
    entering_phone = State()
    entering_checkin = State()
    entering_checkout = State()
    entering_guests = State()
    confirming = State()


class QuizStates(StatesGroup):
    answering = State()


# ============================================================
# QUIZ DATA
# ============================================================
QUIZ_QUESTIONS = [
    {
        "q": "🏔 Какой горный массив является символом Крыма?",
        "answers": ["Кавказ", "Карпаты", "Ай-Петри", "Эльбрус"],
        "correct": 2,
        "fact": "Ай-Петри (1234 м) — одна из самых посещаемых вершин Крыма, расположена над Ялтой.",
    },
    {
        "q": "🏰 Какой дворец находится в Ливадии?",
        "answers": ["Зимний дворец", "Ливадийский дворец", "Воронцовский дворец", "Массандровский дворец"],
        "correct": 1,
        "fact": "Ливадийский дворец — место проведения Ялтинской конференции 1945 года.",
    },
    {
        "q": "🌊 Какой пролив отделяет Крым от Кубани?",
        "answers": ["Дарданеллы", "Босфор", "Керченский пролив", "Гибралтар"],
        "correct": 2,
        "fact": "Керченский пролив соединяет Чёрное и Азовское моря, ширина около 4,5 км.",
    },
    {
        "q": "🍇 Какой крымский город славится виноделием?",
        "answers": ["Севастополь", "Симферополь", "Массандра", "Феодосия"],
        "correct": 2,
        "fact": "Массандра — крупнейшее винодельческое предприятие с коллекцией более 1 млн бутылок.",
    },
    {
        "q": "🦅 Какой заповедник находится в Крыму?",
        "answers": ["Баргузинский", "Крымский природный заповедник", "Кавказский", "Астраханский"],
        "correct": 1,
        "fact": "Крымский природный заповедник основан в 1923 году, занимает 33 394 га.",
    },
    {
        "q": "🏖 Какой пляж считается лучшим в Крыму?",
        "answers": ["Пляж Ласточкино гнездо", "Голубой залив", "Песчаный пляж (Евпатория)", "Все перечисленные"],
        "correct": 3,
        "fact": "Крым славится разнообразием пляжей — от песчаных на западе до галечных на южном берегу.",
    },
    {
        "q": "🏛 В каком году Крым вошёл в состав России?",
        "answers": ["1783", "1853", "1917", "1954"],
        "correct": 0,
        "fact": "В 1783 году Екатерина II подписала Манифест о присоединении Крыма к Российской империи.",
    },
    {
        "q": "🦇 Где в Крыму можно увидеть летучих мышей?",
        "answers": ["Мраморная пещера", "Красные пещеры", "Шахта Кизил-Коба", "Все перечисленные"],
        "correct": 3,
        "fact": "Крымские пещеры — дом для нескольких видов летучих мышей, включая редкие.",
    },
    {
        "q": "🚂 Какая железная дорога проходит по Крыму?",
        "answers": ["Транссибирская", "Южнобережная", "БАМ", "Северо-Кавказская"],
        "correct": 1,
        "fact": "Южнобережная дорога идёт вдоль побережья от Севастополя до Керчи.",
    },
    {
        "q": "🌺 Какое растение является символом Южного берега Крыма?",
        "answers": ["Пальма", "Кипарис", "Олеандр", "Все перечисленные"],
        "correct": 3,
        "fact": "Южный берег Крыма славится субтропической растительностью: пальмы, кипарисы, магнолии.",
    },
]

# ============================================================
# WHEEL OF FORTUNE PRIZES
# ============================================================
WHEEL_PRIZES = [
    ("🎁 Скидка 5% на бронирование", 5),
    ("☕ Бесплатный кофе в ресторане", 2),
    ("🎟 Скидка 10% на следующее бронирование", 10),
    ("🏖 Бесплатный зонт на пляже", 3),
    ("💆 Скидка 20% на спа-процедуры", 15),
    ("🍽 Бесплатный завтрак", 5),
    ("🏊 Бесплатное посещение бассейна", 3),
    ("🎉 Скидка 30% на экскурсию", 20),
    ("😢 Не повезло! Попробуйте завтра", 0),
    ("🍷 Бутылка крымского вина", 8),
]

# ============================================================
# PHOTO GALLERY (placeholder URLs — replace with real hotel photos)
# ============================================================
GALLERY_PHOTOS = [
    ("https://example.com/hotel/exterior.jpg", "🏨 Фасад отеля — вид с моря"),
    ("https://example.com/hotel/lobby.jpg", "🛋 Ресепшен и лобби"),
    ("https://example.com/hotel/room_standard.jpg", "🛏 Номер «Стандарт»"),
    ("https://example.com/hotel/room_comfort.jpg", "🛏 Номер «Комфорт» с балконом"),
    ("https://example.com/hotel/room_lux.jpg", "✨ Номер «Люкс» с панорамным видом"),
    ("https://example.com/hotel/pool.jpg", "🏊 Бассейн на крыше"),
    ("https://example.com/hotel/beach.jpg", "🏖 Собственный пляж"),
    ("https://example.com/hotel/restaurant.jpg", "🍽 Ресторан «Черноморский»"),
    ("https://example.com/hotel/spa.jpg", "💆 Спа-центр"),
    ("https://example.com/hotel/view.jpg", "🌅 Вид на море с террасы"),
]

# ============================================================
# /start & /help
# ============================================================
@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await ensure_user(message.from_user)
    welcome = (
        f"🏨 <b>Добро пожаловать в {HOTEL_NAME}!</b>\n\n"
        "Я помогу вам:\n"
        "• 🏨 Посмотреть номера и цены\n"
        "• 📅 Забронировать номер\n"
        "• 🎰 Испытать удачу в Колесе фортуны\n"
        "• 🧠 Узнать интересные факты о Крыму\n"
        "• 🏆 Копить баллы и получать скидки\n"
        "• ✅ Отмечаться каждый день\n"
        "• 📸 Посмотреть фотографии отеля\n\n"
        "Выберите действие в меню 👇"
    )
    await message.answer(welcome, reply_markup=main_menu_kb(), parse_mode="HTML")


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await show_help(message)


@router.message(F.text == "❓ Помощь")
async def show_help(message: types.Message):
    text = (
        "❓ <b>Помощь</b>\n\n"
        "🏨 <b>Наши номера</b> — посмотреть все типы номеров\n"
        "📅 <b>Забронировать</b> — оформить бронирование\n"
        "🎰 <b>Колесо фортуны</b> — выиграть скидку или приз\n"
        "🧠 <b>Викторина</b> — проверьте знания о Крыму\n"
        "🏆 <b>Мои баллы</b> — ваша карта лояльности\n"
        "✅ <b>Чек-ин</b> — ежедневный бонус\n"
        "📸 <b>Галерея</b> — фото отеля\n"
        "📋 <b>Мои бронирования</b> — история и статус\n"
        "📞 <b>Контакты</b> — связаться с нами\n\n"
        "Команды:\n"
        "/start — главное меню\n"
        "/help — эта справка\n"
        "/admin — панель администратора\n"
        "/stats — статистика баллов"
    )
    await message.answer(text, reply_markup=main_menu_kb(), parse_mode="HTML")


# ============================================================
# ROOMS DISPLAY
# ============================================================
@router.message(F.text == "🏨 Наши номера")
async def show_rooms(message: types.Message):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, name, price, description, available FROM rooms")
        rooms = await cur.fetchall()

    text = "🏠 <b>Наши номера:</b>\n\n"
    for r in rooms:
        status = f"✅ Свободно: {r[4]}" if r[4] > 0 else "❌ Нет мест"
        text += f"<b>{r[1]}</b> — {r[2]}₽/ночь\n{r[3]}\n{status}\n\n"

    text += 'Нажмите «📅 Забронировать» чтобы забронировать номер'
    await message.answer(text, parse_mode="HTML")


# ============================================================
# BOOKING FLOW
# ============================================================
@router.message(F.text == "📅 Забронировать")
async def booking_start(message: types.Message, state: FSMContext):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, name, price, available FROM rooms WHERE available > 0")
        rooms = await cur.fetchall()

    if not rooms:
        await message.answer("😔 К сожалению, все номера заняты. Попробуйте позже.")
        return

    await message.answer("Выберите номер для бронирования:", reply_markup=rooms_inline_kb(rooms))
    await state.set_state(BookingStates.choosing_room)


@router.callback_query(BookingStates.choosing_room, F.data.startswith("room_"))
async def booking_choose_room(callback: types.CallbackQuery, state: FSMContext):
    room_id = int(callback.data.split("_")[1])
    await state.update_data(room_id=room_id)
    await callback.message.answer("👤 Введите ваше имя и фамилию:")
    await state.set_state(BookingStates.entering_name)
    await callback.answer()


@router.message(BookingStates.entering_name)
async def booking_enter_name(message: types.Message, state: FSMContext):
    if len(message.text) < 2:
        await message.answer("❌ Пожалуйста, введите корректное имя.")
        return
    await state.update_data(guest_name=message.text.strip())
    await message.answer("📱 Введите номер телефона (начиная с +7):")
    await state.set_state(BookingStates.entering_phone)


@router.message(BookingStates.entering_phone)
async def booking_enter_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not (phone.startswith("+7") or phone.startswith("8")) or len(phone) < 10:
        await message.answer("❌ Неверный формат. Введите телефон начиная с +7:")
        return
    await state.update_data(guest_phone=phone)
    await message.answer("📅 Дата заезда (ДД.ММ.ГГГГ):")
    await state.set_state(BookingStates.entering_checkin)


@router.message(BookingStates.entering_checkin)
async def booking_enter_checkin(message: types.Message, state: FSMContext):
    try:
        dt = datetime.strptime(message.text.strip(), "%d.%m.%Y")
        if dt.date() < datetime.now().date():
            await message.answer("❌ Дата заезда не может быть в прошлом. Введите заново:")
            return
        await state.update_data(check_in=message.text.strip())
        await message.answer("📅 Дата выезда (ДД.ММ.ГГГГ):")
        await state.set_state(BookingStates.entering_checkout)
    except ValueError:
        await message.answer("❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ:")


@router.message(BookingStates.entering_checkout)
async def booking_enter_checkout(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        dt_out = datetime.strptime(message.text.strip(), "%d.%m.%Y")
        dt_in = datetime.strptime(data["check_in"], "%d.%m.%Y")
        if dt_out <= dt_in:
            await message.answer("❌ Дата выезда должна быть позже даты заезда:")
            return
        await state.update_data(check_out=message.text.strip())
        await message.answer("👥 Количество гостей:")
        await state.set_state(BookingStates.entering_guests)
    except ValueError:
        await message.answer("❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ:")


@router.message(BookingStates.entering_guests)
async def booking_enter_guests(message: types.Message, state: FSMContext):
    try:
        guests = int(message.text.strip())
        if guests < 1 or guests > 10:
            await message.answer("❌ Укажите от 1 до 10 гостей:")
            return
    except ValueError:
        await message.answer("❌ Введите число гостей:")
        return

    await state.update_data(guests=guests)
    data = await state.get_data()

    # Fetch room info
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT name, price, description FROM rooms WHERE id=?", (data["room_id"],))
        room = await cur.fetchone()

    if not room:
        await message.answer("❌ Ошибка: номер не найден. Начните заново.")
        await state.clear()
        return

    d_in = datetime.strptime(data["check_in"], "%d.%m.%Y")
    d_out = datetime.strptime(data["check_out"], "%d.%m.%Y")
    nights = (d_out - d_in).days
    total = room[1] * nights

    await state.update_data(total_price=total)

    summary = (
        f"📋 <b>Подтвердите бронирование:</b>\n\n"
        f"🏨 Номер: <b>{room[0]}</b>\n"
        f"📝 {room[2]}\n"
        f"📅 Заезд: {data['check_in']}\n"
        f"📅 Выезд: {data['check_out']}\n"
        f"🌙 Ночей: {nights}\n"
        f"👥 Гостей: {guests}\n"
        f"💰 <b>Итого: {total}₽</b>\n\n"
        f"👤 Имя: {data['guest_name']}\n"
        f"📱 Телефон: {data['guest_phone']}"
    )
    await message.answer(summary, reply_markup=confirm_booking_kb(), parse_mode="HTML")
    await state.set_state(BookingStates.confirming)


@router.callback_query(BookingStates.confirming, F.data == "booking_confirm")
async def booking_confirm(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    async with aiosqlite.connect(DB_PATH) as db:
        # Create booking
        cur = await db.execute(
            """INSERT INTO bookings (user_id, room_id, guest_name, guest_phone,
               check_in, check_out, guests, total_price, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'confirmed')""",
            (
                callback.from_user.id, data["room_id"], data["guest_name"],
                data["guest_phone"], data["check_in"], data["check_out"],
                data["guests"], data["total_price"],
            ),
        )
        booking_id = cur.lastrowid

        # Decrease availability
        await db.execute(
            "UPDATE rooms SET available = available - 1 WHERE id=? AND available > 0",
            (data["room_id"],),
        )

        # Add loyalty points (1 point per 100 rubles)
        points_earned = data["total_price"] // 100
        await db.execute(
            "UPDATE users SET points = points + ?, level = 1 + (points + ?) / 100 WHERE user_id=?",
            (points_earned, points_earned, callback.from_user.id),
        )

        await db.commit()

    confirm_text = (
        f"✅ <b>Бронирование #{booking_id} подтверждено!</b>\n\n"
        f"Мы свяжемся с вами для уточнения деталей.\n"
        f"Начислено <b>{points_earned} баллов</b> лояльности!\n\n"
        f"Спасибо, что выбрали {HOTEL_NAME}! 🏨"
    )
    await callback.message.answer(confirm_text, reply_markup=main_menu_kb(), parse_mode="HTML")

    # Admin notification
    if ADMIN_ID:
        admin_text = (
            f"🔔 <b>Новое бронирование #{booking_id}!</b>\n\n"
            f"👤 {data['guest_name']}\n"
            f"📱 {data['guest_phone']}\n"
            f"🏨 Комната: {data['room_id']}\n"
            f"📅 {data['check_in']} → {data['check_out']}\n"
            f"👥 Гостей: {data['guests']}\n"
            f"💰 {data['total_price']}₽\n"
            f"🆔 User: @{callback.from_user.username or 'N/A'} ({callback.from_user.id})"
        )
        try:
            await bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")
        except Exception as e:
            log.warning(f"Failed to notify admin: {e}")

    await state.clear()
    await callback.answer()


@router.callback_query(BookingStates.confirming, F.data == "booking_cancel")
async def booking_cancel_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Бронирование отменено.", reply_markup=main_menu_kb())
    await state.clear()
    await callback.answer()


# ============================================================
# MY BOOKINGS
# ============================================================
@router.message(F.text == "📋 Мои бронирования")
async def my_bookings(message: types.Message):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """SELECT b.id, r.name, b.check_in, b.check_out, b.total_price, b.status, b.guests
               FROM bookings b JOIN rooms r ON b.room_id = r.id
               WHERE b.user_id = ?
               ORDER BY b.created_at DESC LIMIT 10""",
            (message.from_user.id,),
        )
        bookings = await cur.fetchall()

    if not bookings:
        await message.answer("📋 У вас пока нет бронирований.\nНажмите «📅 Забронировать» чтобы оформить.")
        return

    text = "📋 <b>Ваши бронирования:</b>\n\n"
    status_emoji = {"confirmed": "✅", "pending": "⏳", "cancelled": "❌"}
    for b in bookings:
        emoji = status_emoji.get(b[5], "❓")
        text += (
            f"{emoji} <b>#{b[0]}</b> — {b[1]}\n"
            f"   📅 {b[2]} → {b[3]} | 👥 {b[6]} | 💰 {b[4]}₽\n"
            f"   Статус: {b[5]}\n\n"
        )
    await message.answer(text, parse_mode="HTML")


# ============================================================
# CONTACTS
# ============================================================
@router.message(F.text == "📞 Контакты")
async def show_contacts(message: types.Message):
    text = (
        f"📞 <b>Контакты {HOTEL_NAME}:</b>\n\n"
        "📱 Телефон: +7 978 123 45 67\n"
        "📧 Email: info@hotel-crimea.ru\n"
        "📍 Адрес: г. Ялта, ул. Ленина, 10\n"
        "🌐 Сайт: hotel-crimea.ru\n"
        "📱 Telegram: @hotel_crimea_support\n\n"
        "⏰ Работаем круглосуточно!"
    )
    await message.answer(text, parse_mode="HTML")


# ============================================================
# WHEEL OF FORTUNE
# ============================================================
@router.message(F.text == "🎰 Колесо фортуны")
async def wheel_spin(message: types.Message):
    uid = message.from_user.id

    # Check if already spun today
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT spun_at FROM wheel_history WHERE user_id=? ORDER BY spun_at DESC LIMIT 1",
            (uid,),
        )
        last = await cur.fetchone()
        if last:
            last_time = datetime.fromisoformat(last[0])
            if last_time.date() == datetime.now().date():
                await message.answer(
                    "🎰 Вы уже крутили колесо сегодня!\n"
                    "Приходите завтра за новым призом 🎁"
                )
                return

    # Animation-like sequence
    anim = await message.answer("🎰 Колесо фортуны крутится...")
    await asyncio.sleep(0.8)
    await anim.edit_text("🎰 Крутится... 🎡")
    await asyncio.sleep(0.8)
    await anim.edit_text("🎰 Почти готово... 🎡🎰")
    await asyncio.sleep(0.6)

    # Pick prize
    prize_text, prize_points = random.choice(WHEEL_PRIZES)

    # Save to history
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO wheel_history (user_id, prize) VALUES (?, ?)",
            (uid, prize_text),
        )
        if prize_points > 0:
            await db.execute(
                "UPDATE users SET points = points + ?, level = 1 + (points + ?) / 100 WHERE user_id=?",
                (prize_points, prize_points, uid),
            )
        await db.commit()

    result_text = f"🎉 <b>Ваш приз:</b>\n\n{prize_text}"
    if prize_points > 0:
        result_text += f"\n\n🏆 +{prize_points} баллов начислено!"
    await anim.edit_text(result_text, parse_mode="HTML")


# ============================================================
# QUIZ ABOUT CRIMEA
# ============================================================
@router.message(F.text == "🧠 Викторина о Крыму")
async def quiz_start(message: types.Message, state: FSMContext):
    uid = message.from_user.id
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO quiz_progress (user_id, score, current_q) VALUES (?, 0, 0)",
            (uid,),
        )
        await db.commit()

    q = QUIZ_QUESTIONS[0]
    await message.answer(
        f"🧠 <b>Викторина о Крыму</b>\n\n"
        f"Вопрос 1/{len(QUIZ_QUESTIONS)}:\n\n{q['q']}",
        reply_markup=quiz_answer_kb(q["answers"]),
        parse_mode="HTML",
    )
    await state.set_state(QuizStates.answering)


@router.callback_query(QuizStates.answering, F.data.startswith("quiz_"))
async def quiz_answer(callback: types.CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    chosen = int(callback.data.split("_")[1])

    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT score, current_q FROM quiz_progress WHERE user_id=?", (uid,))
        row = await cur.fetchone()
        if not row:
            await callback.answer("Начните викторину заново!", show_alert=True)
            await state.clear()
            return
        score, current_q = row
        q = QUIZ_QUESTIONS[current_q]

        # Check answer
        if chosen == q["correct"]:
            score += 1
            result = f"✅ Правильно! {q['fact']}"
        else:
            correct_text = q["answers"][q["correct"]]
            result = f"❌ Неправильно! Правильный ответ: {correct_text}\n\n{q['fact']}"

        current_q += 1

        # Save progress
        await db.execute(
            "UPDATE quiz_progress SET score=?, current_q=? WHERE user_id=?",
            (score, current_q, uid),
        )

        # Award points for participation
        if current_q >= len(QUIZ_QUESTIONS):
            bonus = score * 5  # 5 points per correct answer
            await db.execute(
                "UPDATE users SET points = points + ?, level = 1 + (points + ?) / 100 WHERE user_id=?",
                (bonus, bonus, uid),
            )

        await db.commit()

    await callback.answer()

    if current_q >= len(QUIZ_QUESTIONS):
        # Quiz finished
        final = (
            f"🏁 <b>Викторина завершена!</b>\n\n"
            f"{result}\n\n"
            f"📊 Результат: <b>{score}/{len(QUIZ_QUESTIONS)}</b> правильных ответов\n"
            f"🏆 Начислено <b>{score * 5}</b> баллов!\n\n"
        )
        if score == len(QUIZ_QUESTIONS):
            final += "🏆 Отлично! Вы настоящий знаток Крыма!"
        elif score >= len(QUIZ_QUESTIONS) // 2:
            final += "👍 Хороший результат! Продолжайте изучать Крым!"
        else:
            final += "📚 Стоит почитать больше о Крыме — удивительном полуострове!"

        await callback.message.answer(final, reply_markup=main_menu_kb(), parse_mode="HTML")
        await state.clear()
    else:
        # Next question
        next_q = QUIZ_QUESTIONS[current_q]
        text = (
            f"{result}\n\n"
            f"─────────────\n\n"
            f"Вопрос {current_q + 1}/{len(QUIZ_QUESTIONS)}:\n\n{next_q['q']}"
        )
        await callback.message.answer(
            text,
            reply_markup=quiz_answer_kb(next_q["answers"]),
            parse_mode="HTML",
        )


# ============================================================
# DAILY CHECK-IN
# ============================================================
@router.message(F.text == "✅ Ежедневный чек-ин")
async def daily_checkin(message: types.Message):
    uid = message.from_user.id
    today = datetime.now().strftime("%Y-%m-%d")

    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT last_checkin, points FROM users WHERE user_id=?", (uid,))
        row = await cur.fetchone()
        if not row:
            await ensure_user(message.from_user)
            cur = await db.execute("SELECT last_checkin, points FROM users WHERE user_id=?", (uid,))
            row = await cur.fetchone()

        last_checkin = row[0]
        if last_checkin == today:
            await message.answer(
                "✅ Вы уже отметились сегодня!\n"
                "Приходите завтра за бонусом 🎁"
            )
            return

        # Streak bonus: consecutive days
        streak = 1
        if last_checkin:
            try:
                last_dt = datetime.strptime(last_checkin, "%Y-%m-%d")
                if (datetime.now() - last_dt).days == 1:
                    # Get current streak from points context (simplified)
                    streak = min(row[1] // 5 + 1, 7)  # Simple streak approximation
            except (ValueError, TypeError):
                pass

        bonus = 5 + (streak - 1) * 2  # 5 base + 2 per consecutive day, max 17
        bonus = min(bonus, 20)

        await db.execute(
            "UPDATE users SET last_checkin=?, points = points + ?, level = 1 + (points + ?) / 100 WHERE user_id=?",
            (today, bonus, bonus, uid),
        )
        await db.commit()

    text = (
        f"✅ <b>Чек-ин выполнен!</b>\n\n"
        f"🎁 +{bonus} баллов начислено!\n"
        f"🔥 Серия: {streak} дн. подряд\n\n"
        f"Отмечайтесь каждый день, чтобы увеличить бонус!"
    )
    await message.answer(text, reply_markup=main_menu_kb(), parse_mode="HTML")


# ============================================================
# LOYALTY / MY POINTS
# ============================================================
@router.message(F.text == "🏆 Мои баллы")
async def my_points(message: types.Message):
    uid = message.from_user.id
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT points, level FROM users WHERE user_id=?", (uid,))
        row = await cur.fetchone()

    if not row:
        await ensure_user(message.from_user)
        points, level = 0, 1
    else:
        points, level = row

    # Level names
    level_names = {
        1: "🥉 Новичок",
        2: "🥈 Путешественник",
        3: "🥇 Знаток Крыма",
        4: "💎 VIP-гость",
        5: "👑 Платиновый гость",
    }
    level_name = level_names.get(level, f"👑 Уровень {level}")
    next_level_points = level * 100
    progress = points - (level - 1) * 100
    bar_filled = progress // 10
    bar_empty = 10 - bar_filled
    progress_bar = "█" * bar_filled + "░" * bar_empty

    text = (
        f"🏆 <b>Ваша карта лояльности</b>\n\n"
        f"👤 Уровень: {level_name} (уровень {level})\n"
        f"⭐ Баллы: <b>{points}</b>\n"
        f"📊 Прогресс до следующего уровня:\n"
        f"   [{progress_bar}] {progress}/{next_level_points - (level-1)*100}\n\n"
        f"💡 <b>Как заработать баллы:</b>\n"
        f"• ✅ Ежедневный чек-ин: 5-20 баллов\n"
        f"• 🎰 Колесо фортуны: до 20 баллов\n"
        f"• 🧠 Викторина: до 50 баллов\n"
        f"• 📅 Бронирование: 1 балл за 100₽\n\n"
        f"🎁 <b>Уровни:</b>\n"
        f"0-99 — 🥉 Новичок\n"
        f"100-199 — 🥈 Путешественник\n"
        f"200-299 — 🥇 Знаток Крыма\n"
        f"300-399 — 💎 VIP-гость\n"
        f"400+ — 👑 Платиновый гость"
    )
    await message.answer(text, parse_mode="HTML")


# ============================================================
# PHOTO GALLERY
# ============================================================
@router.message(F.text == "📸 Галерея")
async def photo_gallery(message: types.Message):
    gallery_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="gallery_prev"),
         InlineKeyboardButton(text="▶️ Вперёд", callback_data="gallery_next")],
    ])

    photo = GALLERY_PHOTOS[0]
    text = f"📸 <b>Фотогалерея {HOTEL_NAME}</b>\n\nФото 1/{len(GALLERY_PHOTOS)}\n{photo[1]}"

    # Try to send as photo, fall back to text
    try:
        await message.answer_photo(photo=photo[0], caption=text, parse_mode="HTML")
    except Exception:
        await message.answer(text + "\n\n(Фото временно недоступно)", parse_mode="HTML")


# ============================================================
# ADMIN COMMANDS
# ============================================================
@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас нет доступа к панели администратора.")
        return

    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        users_count = (await cur.fetchone())[0]
        cur = await db.execute("SELECT COUNT(*) FROM bookings WHERE status='confirmed'")
        bookings_count = (await cur.fetchone())[0]
        cur = await db.execute("SELECT COUNT(*) FROM bookings WHERE status='confirmed' AND date(created_at) = date('now')")
        today_bookings = (await cur.fetchone())[0]
        cur = await db.execute("SELECT SUM(total_price) FROM bookings WHERE status='confirmed'")
        total_revenue = (await cur.fetchone())[0] or 0
        cur = await db.execute("SELECT COUNT(*) FROM rooms")
        rooms_count = (await cur.fetchone())[0]

    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")],
        [InlineKeyboardButton(text="📅 Бронирования", callback_data="admin_bookings")],
        [InlineKeyboardButton(text="🏨 Номера", callback_data="admin_rooms")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
    ])

    text = (
        f"🔐 <b>Панель администратора</b>\n\n"
        f"👥 Пользователей: {users_count}\n"
        f"📅 Бронирований: {bookings_count}\n"
        f"📅 Сегодня: {today_bookings}\n"
        f"💰 Общая выручка: {total_revenue}₽\n"
        f"🏨 Типов номеров: {rooms_count}"
    )
    await message.answer(text, reply_markup=admin_kb, parse_mode="HTML")


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM bookings WHERE status='confirmed'")
        total = (await cur.fetchone())[0]
        cur = await db.execute(
            "SELECT COUNT(*) FROM bookings WHERE status='confirmed' AND created_at >= datetime('now', '-7 days')"
        )
        week = (await cur.fetchone())[0]
        cur = await db.execute("SELECT SUM(total_price) FROM bookings WHERE status='confirmed'")
        revenue = (await cur.fetchone())[0] or 0
        cur = await db.execute("SELECT COUNT(*) FROM wheel_history WHERE spun_at >= datetime('now', '-1 day')")
        wheels_today = (await cur.fetchone())[0]
        cur = await db.execute("SELECT AVG(score) FROM quiz_progress WHERE score > 0")
        avg_quiz = (await cur.fetchone())[0] or 0

    text = (
        f"📊 <b>Статистика</b>\n\n"
        f"📅 Всего бронирований: {total}\n"
        f"📅 За неделю: {week}\n"
        f"💰 Общая выручка: {revenue}₽\n"
        f"🎰 Крутов колеса сегодня: {wheels_today}\n"
        f"🧠 Средний балл викторины: {avg_quiz:.1f}"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin_rooms")
async def admin_rooms(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, name, price, available FROM rooms")
        rooms = await cur.fetchall()

    text = "🏨 <b>Номера:</b>\n\n"
    for r in rooms:
        text += f"#{r[0]} {r[1]} — {r[2]}₽ | Свободно: {r[3]}\n"
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin_bookings")
async def admin_bookings(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """SELECT b.id, r.name, b.guest_name, b.check_in, b.check_out, b.total_price, b.status
               FROM bookings b JOIN rooms r ON b.room_id = r.id
               ORDER BY b.created_at DESC LIMIT 15"""
        )
        bookings = await cur.fetchall()

    if not bookings:
        await callback.message.answer("Бронирований пока нет.")
        await callback.answer()
        return

    text = "📅 <b>Последние бронирования:</b>\n\n"
    for b in bookings:
        text += f"#{b[0]} {b[1]} — {b[2]} | {b[3]}→{b[4]} | {b[5]}₽ | {b[6]}\n"
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin_users")
async def admin_users(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT user_id, full_name, username, points, level FROM users ORDER BY points DESC LIMIT 20"
        )
        users = await cur.fetchall()

    text = "👥 <b>Топ пользователей:</b>\n\n"
    for u in users:
        name = u[1] or "N/A"
        uname = f"@{u[2]}" if u[2] else "нет username"
        text += f"🆔{u[0]} | {name} ({uname}) | ⭐{u[3]} | Ур.{u[4]}\n"
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    await callback.message.answer("📢 Введите текст рассылки для всех пользователей:")
    await state.set_state("broadcast_waiting")
    await callback.answer()


@router.message(F.text, lambda m: m.from_user.id == ADMIN_ID)
async def admin_broadcast_send(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state != "broadcast_waiting":
        return

    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT user_id FROM users")
        users = await cur.fetchall()

    sent, failed = 0, 0
    for (uid,) in users:
        try:
            await bot.send_message(uid, f"📢 <b>Сообщение от {HOTEL_NAME}:</b>\n\n{message.text}", parse_mode="HTML")
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)  # Rate limiting

    await message.answer(f"📢 Рассылка завершена!\n✅ Доставлено: {sent}\n❌ Ошибки: {failed}")
    await state.clear()


# ============================================================
# /stats — user stats command
# ============================================================
@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    await my_points(message)


# ============================================================
# CATCH-ALL for unknown text
# ============================================================
@router.message(F.text)
async def unknown_message(message: types.Message):
    await message.answer(
        "🤔 Не понимаю вас. Используйте кнопки меню или /help для справки.",
        reply_markup=main_menu_kb(),
    )


# ============================================================
# MAIN
# ============================================================
async def main():
    global bot

    # Initialize database
    await init_db()
    log.info("Database initialized")

    # Create bot with optional SOCKS5 proxy
    try:
        from aiohttp_socks import ProxyConnector
        from aiogram.client.session.aiohttp import AiohttpSession
        session = AiohttpSession(proxy=PROXY_URL)
        bot = Bot(token=BOT_TOKEN, session=session)
        proxy_host = PROXY_URL.split("@")[1] if "@" in PROXY_URL else PROXY_URL
        log.info(f"Bot started with proxy: {proxy_host}")
    except ImportError:
        bot = Bot(token=BOT_TOKEN)
        log.info("Bot started (direct connection, aiohttp-socks not installed)")
    except Exception as e:
        bot = Bot(token=BOT_TOKEN)
        log.warning(f"Proxy failed ({e}), using direct connection")

    log.info(f"{HOTEL_NAME} bot v2 starting polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
