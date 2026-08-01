#!/usr/bin/env python3
"""
Salon Bot — python-telegram-bot v22 + HTTPXRequest + SOCKS5 proxy.
Same library as gateway. Proven to work with Crimea network.

> Revisit: when salon bot logic, aiogram handlers, or salon integration changes. Last touched: 2026-07-02.
"""
import os
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.request import HTTPXRequest

# Config
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
DB_PATH = Path(__file__).parent / "salon_bookings.db"
PROXY = os.environ.get("PROXY", "http://127.0.0.1:10809")

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
WORK_DAYS = [0, 1, 2, 3, 4, 5]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("salon")


# --- Database ---
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
        (date_str,),
    ).fetchall()
    conn.close()
    return rows


def create_booking(user_id, username, service, date_str, time_str):
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT INTO bookings (user_id, username, service, date, time) VALUES (?, ?, ?, ?, ?)",
        (user_id, username, service, date_str, time_str),
    )
    conn.commit()
    conn.close()


# --- Handlers ---
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("💇 Записаться в салон", callback_data="salon_book")]]
    )
    await update.message.reply_text("Добро пожаловать! Выберите действие:", reply_markup=kb)


async def cmd_salon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(
                f"{s['name']} — {s['price']}₽ ({s['duration']}мин)",
                callback_data=f"svc_{s['id']}",
            )]
            for s in SERVICES
        ]
    )
    await update.message.reply_text("Выберите услугу:", reply_markup=kb)


async def cmd_my_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT service, date, time FROM bookings WHERE user_id=? AND status='confirmed' ORDER BY date, time",
        (uid,),
    ).fetchall()
    conn.close()
    if not rows:
        await update.message.reply_text("У вас нет активных записей.")
        return
    lines = ["📋 Ваши записи:\n"]
    for svc, date, time in rows:
        lines.append(f"• {svc} — {date} в {time}")
    await update.message.reply_text("\n".join(lines))


async def cb_salon_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(
                f"{s['name']} — {s['price']}₽ ({s['duration']}мин)",
                callback_data=f"svc_{s['id']}",
            )]
            for s in SERVICES
        ]
    )
    await query.edit_message_text("Выберите услугу:", reply_markup=kb)


async def cb_choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    svc_id = query.data.replace("svc_", "")
    svc = next((s for s in SERVICES if s["id"] == svc_id), None)
    if not svc:
        await query.answer("Услуга не найдена")
        return

    context.user_data["service"] = svc["name"]
    context.user_data["price"] = svc["price"]

    today = datetime.now()
    buttons = []
    for i in range(1, 8):
        day = today + timedelta(days=i)
        if day.weekday() in WORK_DAYS:
            buttons.append(
                [InlineKeyboardButton(
                    day.strftime("%a %d.%m"),
                    callback_data=f"date_{day.strftime('%Y-%m-%d')}",
                )]
            )

    kb = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(
        f"Услуга: {svc['name']} ({svc['price']}₽)\nВыберите дату:",
        reply_markup=kb,
    )
    await query.answer()


async def cb_choose_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    date_str = query.data.replace("date_", "")
    context.user_data["date"] = date_str

    booked = get_bookings_for_date(date_str)
    booked_times = {b[0] for b in booked}

    buttons = []
    for hour in range(WORK_HOURS["start"], WORK_HOURS["end"]):
        for minute in [0, 30]:
            t = f"{hour:02d}:{minute:02d}"
            if t not in booked_times:
                buttons.append(
                    [InlineKeyboardButton(t, callback_data=f"time_{t}")]
                )

    if not buttons:
        await query.edit_message_text("Нет свободных слотов. Выберите другую дату.")
        await query.answer()
        return

    kb = InlineKeyboardMarkup(buttons)
    await query.edit_message_text("Выберите время:", reply_markup=kb)
    await query.answer()


async def cb_choose_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    time_str = query.data.replace("time_", "")
    context.user_data["time"] = time_str

    d = context.user_data
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_yes")],
            [InlineKeyboardButton("❌ Отмена", callback_data="confirm_no")],
        ]
    )
    await query.edit_message_text(
        f"📋 Запись:\n"
        f"Услуга: {d['service']}\n"
        f"Дата: {d['date']}\n"
        f"Время: {time_str}\n"
        f"Цена: {d['price']}₽\n\n"
        f"Подтвердить?",
        reply_markup=kb,
    )
    await query.answer()


async def cb_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    d = context.user_data
    user = update.effective_user
    create_booking(
        user_id=user.id,
        username=user.username or user.first_name,
        service=d["service"],
        date_str=d["date"],
        time_str=d["time"],
    )
    await query.edit_message_text(
        f"✅ Запись создана!\n"
        f"{d['service']} — {d['date']} в {d['time']}\n"
        f"Ждём вас! 💇"
    )
    context.user_data.clear()
    await query.answer()


async def cb_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.edit_message_text("Запись отменена.")
    context.user_data.clear()
    await query.answer()


# --- Error handler ---
async def error_handler(update, context):
    """Log errors but keep polling alive."""
    logger.warning(f"Polling error: {context.error}")
    # Don't crash — keep running like gateway does

# --- Main ---
def main():
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        return

    init_db()
    logger.info(f"Services: {len(SERVICES)}")
    logger.info(f"Proxy: {PROXY}")

    # HTTPXRequest with generous timeouts for flaky Crimea network
    request = HTTPXRequest(
        proxy=PROXY,
        connect_timeout=15.0,
        read_timeout=30.0,
        pool_timeout=10.0,
    )

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .request(request)
        .build()
    )

    # Error handler — keeps polling alive on network errors
    app.add_error_handler(error_handler)

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("salon", cmd_salon))
    app.add_handler(CommandHandler("my_bookings", cmd_my_bookings))
    app.add_handler(CallbackQueryHandler(cb_salon_book, pattern="^salon_book$"))
    app.add_handler(CallbackQueryHandler(cb_choose_service, pattern=r"^svc_"))
    app.add_handler(CallbackQueryHandler(cb_choose_date, pattern=r"^date_"))
    app.add_handler(CallbackQueryHandler(cb_choose_time, pattern=r"^time_"))
    app.add_handler(CallbackQueryHandler(cb_confirm, pattern="^confirm_yes$"))
    app.add_handler(CallbackQueryHandler(cb_cancel, pattern="^confirm_no$"))

    logger.info("Salon bot starting polling...")
    import time
    while True:
        try:
            app.run_polling(
                drop_pending_updates=True,
                poll_interval=2.0,
                bootstrap_retries=5,
            )
        except Exception as e:
            logger.error(f"Polling crashed: {e}. Restarting in 10s...")
            time.sleep(10)


if __name__ == "__main__":
    main()
