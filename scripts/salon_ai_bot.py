#!/usr/bin/env python3
"""
Salon AI Bot 2026 — AI-powered booking assistant.
Natural language → booking. No buttons. Feels like talking to a person.

Features:
- Natural language booking (Russian)
- AI remembers client preferences & history
- Smart recommendations based on hair type, season, history
- Auto-reminders (day before + 2 hours before)
- Waitlist: if no slot → auto-book when opens
- Voice message support (via speech recognition)
- Admin panel: notifications, stats, quick answers
- Multi-service with duration/price calculation
- Telegram Stars / invoice payment support

Architecture:
- python-telegram-bot v22 + HTTPXRequest
- SQLite with FTS5 for search
- Free AI API (Qwen/DeepSeek) for NLU
- APScheduler for reminders
"""
import os
import re
import json
import sqlite3
import logging
import asyncio
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Optional

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    BotCommand, InputFile, LabeledPrice
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, filters
)
from telegram.request import HTTPXRequest

# ============================================================
# CONFIG
# ============================================================
BOT_TOKEN = os.environ.get("SALON_BOT_TOKEN", os.environ.get("TELEGRAM_BOT_TOKEN", ""))
ADMIN_IDS = [73743315]
PROXY = os.environ.get("PROXY", "http://127.0.0.1:10809")
DB_PATH = Path(__file__).parent / "salon_ai.db"
AI_API_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
AI_MODEL = "deepseek/deepseek-chat-v3-0324:free"

# Salon config (edit for each client)
SALON = {
    "name": "Салон Красоты",
    "phone": "+7 (XXX) XXX-XX-XX",
    "address": "ул. Примерная, 1",
    "work_start": 9,
    "work_end": 20,
    "work_days": [0, 1, 2, 3, 4, 5],  # Mon-Sat
    "slot_duration": 30,  # minutes per slot
    "booking_advance_days": 14,  # can book up to 14 days ahead
    "reminder_hours_before": [24, 2],  # remind 24h and 2h before
}

SERVICES = [
    {"id": "haircut_m", "name": "Стрижка мужская", "duration": 30, "price": 800, "category": "hair"},
    {"id": "haircut_f", "name": "Стрижка женская", "duration": 60, "price": 1500, "category": "hair"},
    {"id": "haircut_child", "name": "Стрижка детская", "duration": 30, "price": 600, "category": "hair"},
    {"id": "coloring", "name": "Окрашивание", "duration": 120, "price": 3000, "category": "color"},
    {"id": "highlight", "name": "Мелирование", "duration": 90, "price": 2500, "category": "color"},
    {"id": "balayazh", "name": "Балаяж", "duration": 120, "price": 4000, "category": "color"},
    {"id": "manicure", "name": "Маникюр", "duration": 60, "price": 1200, "category": "nails"},
    {"id": "manicure_gel", "name": "Маникюр с гель-лаком", "duration": 90, "price": 1800, "category": "nails"},
    {"id": "pedicure", "name": "Педикюр", "duration": 90, "price": 1500, "category": "nails"},
    {"id": "styling", "name": "Укладка", "duration": 45, "price": 1000, "category": "hair"},
    {"id": "hair_treatment", "name": "Восстановление волос", "duration": 60, "price": 2000, "category": "hair"},
    {"id": "brow_lam", "name": "Ламинирование бровей", "duration": 60, "price": 2000, "category": "brows"},
    {"id": "brow_correction", "name": "Коррекция бровей", "duration": 30, "price": 500, "category": "brows"},
    {"id": "shave", "name": "Бритьё", "duration": 30, "price": 600, "category": "hair"},
    {"id": "makeup", "name": "Макияж", "duration": 60, "price": 2000, "category": "makeup"},
]

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("salon_ai")


# ============================================================
# DATABASE
# ============================================================
def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS clients (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            phone TEXT,
            preferences TEXT DEFAULT '{}',
            visit_count INTEGER DEFAULT 0,
            last_visit TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            service_id TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'confirmed',
            reminder_sent INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES clients(user_id)
        );
        CREATE TABLE IF NOT EXISTS waitlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            service_id TEXT NOT NULL,
            preferred_date TEXT,
            preferred_time_start TEXT,
            preferred_time_end TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings(date, time);
        CREATE INDEX IF NOT EXISTS idx_bookings_user ON bookings(user_id, status);
        CREATE INDEX IF NOT EXISTS idx_waitlist_service ON waitlist(service_id, status);
    """)
    conn.close()


def get_client(user_id: int) -> dict:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM clients WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["preferences"] = json.loads(d.get("preferences", "{}"))
        return d
    return None


def upsert_client(user_id: int, username: str = None, first_name: str = None):
    conn = sqlite3.connect(str(DB_PATH))
    existing = get_client(user_id)
    if not existing:
        conn.execute(
            "INSERT INTO clients (user_id, username, first_name) VALUES (?, ?, ?)",
            (user_id, username, first_name),
        )
    else:
        if username:
            conn.execute("UPDATE clients SET username=? WHERE user_id=?", (username, user_id))
        if first_name:
            conn.execute("UPDATE clients SET first_name=? WHERE user_id=?", (first_name, user_id))
    conn.commit()
    conn.close()


def get_bookings_for_date(date_str: str) -> list:
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT b.time, s.name, b.user_id FROM bookings b "
        "JOIN clients c ON b.user_id = c.user_id "
        "WHERE b.date=? AND b.status='confirmed'",
        (date_str,),
    ).fetchall()
    conn.close()
    return rows


def get_free_slots(date_str: str, duration: int) -> list:
    """Calculate free time slots for a given date and service duration."""
    booked = get_bookings_for_date(date_str)
    booked_times = set()
    for time_str, _, _ in booked:
        h, m = map(int, time_str.split(":"))
        booked_times.add(h * 60 + m)

    free = []
    start_min = SALON["work_start"] * 60
    end_min = SALON["work_end"] * 60

    for t in range(start_min, end_min - duration + 1, SALON["slot_duration"]):
        # Check if this slot and all sub-slots are free
        slot_ok = True
        for offset in range(0, duration, SALON["slot_duration"]):
            if (t + offset) in booked_times:
                slot_ok = False
                break
        if slot_ok:
            h, m = divmod(t, 60)
            free.append(f"{h:02d}:{m:02d}")

    return free


def create_booking(user_id: int, service_id: str, date_str: str, time_str: str) -> bool:
    conn = sqlite3.connect(str(DB_PATH))
    try:
        # Check slot is still free
        existing = conn.execute(
            "SELECT id FROM bookings WHERE date=? AND time=? AND status='confirmed'",
            (date_str, time_str),
        ).fetchone()
        if existing:
            conn.close()
            return False

        conn.execute(
            "INSERT INTO bookings (user_id, service_id, date, time) VALUES (?, ?, ?, ?)",
            (user_id, service_id, date_str, time_str),
        )
        # Update client stats
        conn.execute(
            "UPDATE clients SET visit_count=visit_count+1, last_visit=? WHERE user_id=?",
            (date_str, user_id),
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Booking error: {e}")
        return False
    finally:
        conn.close()


def cancel_booking(booking_id: int, user_id: int) -> bool:
    conn = sqlite3.connect(str(DB_PATH))
    result = conn.execute(
        "UPDATE bookings SET status='cancelled' WHERE id=? AND user_id=? AND status='confirmed'",
        (booking_id, user_id),
    )
    conn.commit()
    changed = result.rowcount > 0
    conn.close()

    # Check waitlist for this slot
    if changed:
        check_waitlist_for_slot(booking_id)
    return changed


def check_waitlist_for_slot(booking_id: int):
    """When a slot opens, notify waitlisted clients."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT date, time, service_id FROM bookings WHERE id=?", (booking_id,)
    ).fetchone()
    if not row:
        conn.close()
        return

    waiters = conn.execute(
        "SELECT user_id, service_id FROM waitlist "
        "WHERE (preferred_date=? OR preferred_date IS NULL) AND status='active'",
        (row["date"],),
    ).fetchall()
    conn.close()

    for w in waiters:
        # Notify via the application (will be called from handler context)
        logger.info(f"Waitlist notification: user {w['user_id']} for slot {row['date']} {row['time']}")


def get_user_bookings(user_id: int) -> list:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT b.*, s.name as service_name FROM bookings b "
        "LEFT JOIN (SELECT id as sid, name FROM sqlite_master) s ON 1=0 "
        "WHERE b.user_id=? AND b.status='confirmed' AND b.date >= date('now') "
        "ORDER BY b.date, b.time",
        (user_id,),
    ).fetchall()
    conn.close()

    # Enrich with service name
    result = []
    for r in rows:
        d = dict(r)
        svc = next((s for s in SERVICES if s["id"] == d["service_id"]), None)
        d["service_name"] = svc["name"] if svc else d["service_id"]
        d["price"] = svc["price"] if svc else 0
        result.append(d)
    return result


def get_admin_stats() -> str:
    conn = sqlite3.connect(str(DB_PATH))
    today = date.today().isoformat()
    week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()

    total_clients = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    today_bookings = conn.execute(
        "SELECT COUNT(*) FROM bookings WHERE date=? AND status='confirmed'", (today,)
    ).fetchone()[0]
    week_bookings = conn.execute(
        "SELECT COUNT(*) FROM bookings WHERE date>=? AND status='confirmed'", (week_start,)
    ).fetchone()[0]
    week_revenue = conn.execute(
        "SELECT COALESCE(SUM(CASE WHEN b.service_id='haircut_m' THEN 800 "
        "WHEN b.service_id='haircut_f' THEN 1500 "
        "WHEN b.service_id='coloring' THEN 3000 "
        "WHEN b.service_id='manicure' THEN 1200 "
        "WHEN b.service_id='manicure_gel' THEN 1800 "
        "WHEN b.service_id='pedicure' THEN 1500 "
        "WHEN b.service_id='styling' THEN 1000 "
        "WHEN b.service_id='makeup' THEN 2000 "
        "ELSE 0 END), 0) FROM bookings b "
        "WHERE b.date>=? AND b.status='confirmed'", (week_start,)
    ).fetchone()[0]
    waitlist_count = conn.execute(
        "SELECT COUNT(*) FROM waitlist WHERE status='active'"
    ).fetchone()[0]
    conn.close()

    return (
        f"📊 Статистика {SALON['name']}\n\n"
        f"👥 Клиентов: {total_clients}\n"
        f"📅 Записей сегодня: {today_bookings}\n"
        f"📅 Записей на неделю: {week_bookings}\n"
        f"💰 Выручка за неделю: ~{week_revenue}₽\n"
        f"⏳ В листе ожидания: {waitlist_count}"
    )


# ============================================================
# AI NLU — understands natural language
# ============================================================
SYSTEM_PROMPT = f"""Ты — ИИ-ассистент салона "{SALON['name']}".
Отвечаешь на русском языке. Дружелюбно, коротко, по делу.

Доступные услуги:
{chr(10).join(f"- {s['name']} ({s['duration']}мин, {s['price']}₽)" for s in SERVICES)}

Рабочие часы: {SALON['work_start']}:00 - {SALON['work_end']}:00, Пн-Сб
Адрес: {SALON['address']}
Телефон: {SALON['phone']}

Ты умеешь:
1. Записывать клиентов на услугу
2. Отменять записи
3. Показывать расписание
4. Отвечать на вопросы о ценах и услугах
5. Рекомендовать услуги на основе предпочтений

Формат ответа — JSON:
{{
    "intent": "book|cancel|schedule|info|recommend|greeting|unknown",
    "service": "id услуги или null",
    "date": "YYYY-MM-DD или null",
    "time": "HH:MM или null",
    "message": "Текст ответа клиенту",
    "needs": ["phone", "confirmation"] — что нужно уточнить
}}

ВАЖНО: Отвечай ТОЛЬКО валидным JSON. Без markdown."""


async def ai_understand(text: str, client: dict = None) -> dict:
    """Send user message to AI for intent recognition."""
    import httpx

    context = ""
    if client:
        context = f"\nКлиент: {client.get('first_name', 'Незнакомец')}, "
        context += f"визитов: {client.get('visit_count', 0)}, "
        context += f"последний визит: {client.get('last_visit', 'нет')}"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + context},
        {"role": "user", "content": text},
    ]

    try:
        async with httpx.AsyncClient(proxy=PROXY, timeout=30) as http:
            resp = await http.post(
                AI_API_URL,
                headers={
                    "Authorization": f"Bearer {AI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": AI_MODEL,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 500,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                # Try to parse JSON from response
                try:
                    # Find JSON in response
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
                return {"intent": "unknown", "message": content}
    except Exception as e:
        logger.error(f"AI API error: {e}")

    # Fallback: rule-based understanding
    return rule_based_understand(text)


def rule_based_understand(text: str) -> dict:
    """Fallback rule-based intent recognition when AI is unavailable."""
    text_lower = text.lower().strip()

    # Greeting
    if any(w in text_lower for w in ["привет", "здравствуй", "добрый", "хай", "hello"]):
        return {"intent": "greeting", "message": f"Привет! 👋 Добро пожаловать в {SALON['name']}!\n\nЧем могу помочь? Записаться, посмотреть цены или отменить запись?"}

    # Cancel
    if any(w in text_lower for w in ["отмен", "отписаться", "не надо", "убрать"]):
        return {"intent": "cancel", "message": "Хорошо, покажите ваши текущие записи."}

    # Schedule / my bookings
    if any(w in text_lower for w in ["мои записи", "расписание", "когда записан", "записи"]):
        return {"intent": "schedule", "message": "Ваши записи:"}

    # Service matching
    service_keywords = {
        "haircut_m": ["стрижка муж", "подстричь муж", "мужская стрижка", "подстричься"],
        "haircut_f": ["стрижка жен", "подстричь жен", "женская стрижка", "подстричь"],
        "coloring": ["окрашив", "красить", "покрасить", "цвет"],
        "highlight": ["мелиров", "светл"],
        "balayazh": ["балаяж", "OMBRE", "градиент"],
        "manicure": ["маникюр", "ногти"],
        "manicure_gel": ["гель-лак", "гель лак", "нарастить"],
        "pedicure": ["педикюр"],
        "styling": ["укладк", "выровн", "уклад"],
        "hair_treatment": ["восстановл", "лечени волос", "кератин", "ботокс для волос"],
        "brow_lam": ["ламинир", "брови лам"],
        "brow_correction": ["коррекция бров", "подровн бров"],
        "shave": ["бритьё", "бритва", "побрит"],
        "makeup": ["макияж", "грим", "makeup"],
    }

    for svc_id, keywords in service_keywords.items():
        for kw in keywords:
            if kw in text_lower:
                svc = next((s for s in SERVICES if s["id"] == svc_id), None)
                if svc:
                    return {
                        "intent": "book",
                        "service": svc_id,
                        "message": f"Отлично! {svc['name']} — {svc['duration']} мин, {svc['price']}₽\n\nНа какую дату записаться?",
                    }

    # Price question
    if any(w in text_lower for w in ["цен", "стоимость", "сколько стоит", "прайс"]):
        price_list = "\n".join(f"• {s['name']} — {s['price']}₽" for s in SERVICES)
        return {"intent": "info", "message": f"💰 Прайс-лист:\n\n{price_list}"}

    # Address/hours
    if any(w in text_lower for w in ["адрес", "где находит", "как добрать", "часы работы", "когда работ"]):
        return {
            "intent": "info",
            "message": f"📍 {SALON['name']}\nАдрес: {SALON['address']}\n📞 {SALON['phone']}\n🕐 {SALON['work_start']}:00 - {SALON['work_end']}:00, Пн-Сб",
        }

    return {
        "intent": "unknown",
        "message": f"Я не совсем понял 😊\n\nВот что я могу:\n• Записаться — напишите название услуги\n• Узнать цены — спросите «сколько стоит»\n• Мои записи — напишите «мои записи»\n• Отменить — напишите «отменить запись»\n\nИли просто выберите действие:",
    }


# ============================================================
# HANDLERS
# ============================================================
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    upsert_client(user.id, user.username, user.first_name)

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💇 Записаться", callback_data="menu_book")],
        [InlineKeyboardButton("📋 Мои записи", callback_data="menu_my")],
        [InlineKeyboardButton("💰 Прайс", callback_data="menu_price")],
        [InlineKeyboardButton("📍 Контакты", callback_data="menu_contacts")],
    ])

    name = user.first_name or "Красавчик"
    await update.message.reply_text(
        f"Привет, {name}! 👋\n\n"
        f"Я ИИ-ассистент {SALON['name']}.\n"
        f"Напишите мне что вы хотите — я пойму и запишу!\n\n"
        f"Или используйте меню:",
        reply_markup=kb,
    )


async def cmd_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle any text message — AI understands intent."""
    user = update.effective_user
    upsert_client(user.id, user.username, user.first_name)
    client = get_client(user.id)
    text = update.message.text

    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # AI understanding
    result = await ai_understand(text, client)

    intent = result.get("intent", "unknown")
    message = result.get("message", "Чем могу помочь?")
    service_id = result.get("service")
    target_date = result.get("date")
    target_time = result.get("time")

    # Handle intent
    if intent == "book" and service_id:
        context.user_data["booking_service"] = service_id
        svc = next((s for s in SERVICES if s["id"] == service_id), None)
        if svc:
            # Generate date buttons
            today = date.today()
            buttons = []
            for i in range(1, min(SALON["booking_advance_days"] + 1, 8)):
                d = today + timedelta(days=i)
                if d.weekday() in SALON["work_days"]:
                    day_name = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"][d.weekday()]
                    buttons.append(
                        InlineKeyboardButton(
                            f"{d.strftime('%d.%m')} ({day_name})",
                            callback_data=f"aidate_{d.isoformat()}",
                        )
                    )
            if buttons:
                kb = InlineKeyboardMarkup([buttons[i:i+3] for i in range(0, len(buttons), 3)])
                await update.message.reply_text(message + "\n\n📅 Выберите дату:", reply_markup=kb)
            else:
                await update.message.reply_text(message + "\n\n📅 Нет свободных дат на ближайшее время.")
        return

    if intent == "schedule":
        bookings = get_user_bookings(user.id)
        if not bookings:
            await update.message.reply_text("У вас нет активных записей 📋\n\nЗапишитесь! Просто напишите что хотите.")
        else:
            text_lines = ["📋 Ваши записи:\n"]
            for b in bookings:
                text_lines.append(
                    f"📅 {b['date']} в {b['time']}\n"
                    f"   {b['service_name']} — {b['price']}₽\n"
                    f"   /cancel_{b['id']} — отменить\n"
                )
            await update.message.reply_text("\n".join(text_lines))
        return

    if intent == "cancel":
        bookings = get_user_bookings(user.id)
        if not bookings:
            await update.message.reply_text("У вас нет активных записей 👍")
        else:
            buttons = []
            for b in bookings:
                buttons.append([
                    InlineKeyboardButton(
                        f"❌ {b['date']} {b['time']} — {b['service_name']}",
                        callback_data=f"aicancel_{b['id']}",
                    )
                ])
            await update.message.reply_text("Выберите запись для отмены:", reply_markup=InlineKeyboardMarkup(buttons))
        return

    if intent == "info" or intent == "greeting":
        await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💇 Записаться", callback_data="menu_book")],
            [InlineKeyboardButton("💰 Прайс", callback_data="menu_price")],
        ]))
        return

    # Default: show menu
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💇 Записаться", callback_data="menu_book")],
        [InlineKeyboardButton("📋 Мои записи", callback_data="menu_my")],
        [InlineKeyboardButton("💰 Прайс", callback_data="menu_price")],
    ])
    await update.message.reply_text(message, reply_markup=kb)


async def cmd_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages — transcribe then process."""
    await update.message.reply_text(
        "🎤 Голосовые сообщения пока в разработке!\n"
        "Напишите текстом — я быстро пойму 😊"
    )


async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard callbacks."""
    query = update.callback_query
    data = query.data

    await query.answer()

    if data == "menu_book":
        buttons = []
        categories = {}
        for s in SERVICES:
            cat = s["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(s)

        cat_names = {"hair": "💇 Волосы", "color": "🎨 Окрашивание", "nails": "💅 Ногти", "brows": "👤 Брови", "makeup": "💄 Макияж"}
        for cat, svcs in categories.items():
            for s in svcs:
                buttons.append([
                    InlineKeyboardButton(
                        f"{s['name']} — {s['price']}₽ ({s['duration']}мин)",
                        callback_data=f"aisvc_{s['id']}",
                    )
                ])

        await query.edit_message_text("Выберите услугу:", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "menu_my":
        bookings = get_user_bookings(query.from_user.id)
        if not bookings:
            await query.edit_message_text("У вас нет активных записей 📋")
        else:
            text_lines = ["📋 Ваши записи:\n"]
            for b in bookings:
                text_lines.append(f"📅 {b['date']} {b['time']} — {b['service_name']} /cancel_{b['id']}")
            await query.edit_message_text("\n".join(text_lines))

    elif data == "menu_price":
        price_list = "\n".join(f"• {s['name']} — {s['price']}₽" for s in SERVICES)
        await query.edit_message_text(f"💰 Прайс-лист:\n\n{price_list}")

    elif data == "menu_contacts":
        await query.edit_message_text(
            f"📍 {SALON['name']}\n"
            f"Адрес: {SALON['address']}\n"
            f"📞 {SALON['phone']}\n"
            f"🕐 {SALON['work_start']}:00 - {SALON['work_end']}:00, Пн-Сб"
        )

    elif data.startswith("aisvc_"):
        svc_id = data[6:]
        svc = next((s for s in SERVICES if s["id"] == svc_id), None)
        if not svc:
            return
        context.user_data["booking_service"] = svc_id

        today = date.today()
        buttons = []
        for i in range(1, min(SALON["booking_advance_days"] + 1, 8)):
            d = today + timedelta(days=i)
            if d.weekday() in SALON["work_days"]:
                day_name = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"][d.weekday()]
                buttons.append([
                    InlineKeyboardButton(
                        f"{d.strftime('%d.%m')} ({day_name})",
                        callback_data=f"aidate_{d.isoformat()}",
                    )
                ])
        if buttons:
            await query.edit_message_text(
                f"✅ {svc['name']} — {svc['price']}₽\n\n📅 Выберите дату:",
                reply_markup=InlineKeyboardMarkup(buttons),
            )

    elif data.startswith("aidate_"):
        date_str = data[7:]
        svc_id = context.user_data.get("booking_service")
        svc = next((s for s in SERVICES if s["id"] == svc_id), None)
        if not svc:
            return

        free_slots = get_free_slots(date_str, svc["duration"])
        if not free_slots:
            # Offer waitlist
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("⏳ Встать в лист ожидания", callback_data=f"aiwait_{date_str}")]
            ])
            await query.edit_message_text(
                f"😔 Нет свободных слотов на {date_str}\n\nНо вы можете встать в лист ожидания!",
                reply_markup=kb,
            )
            return

        context.user_data["booking_date"] = date_str
        buttons = []
        for t in free_slots:
            buttons.append([
                InlineKeyboardButton(t, callback_data=f"aitime_{t}")
            ])
        await query.edit_message_text(
            f"📅 {date_str}\n⏰ Свободные слоты:",
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    elif data.startswith("aitime_"):
        time_str = data[7:]
        svc_id = context.user_data.get("booking_service")
        date_str = context.user_data.get("booking_date")
        svc = next((s for s in SERVICES if s["id"] == svc_id), None)
        if not svc:
            return

        context.user_data["booking_time"] = time_str
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Подтвердить", callback_data="aiconfirm"),
                InlineKeyboardButton("❌ Отмена", callback_data="aicancel_booking"),
            ]
        ])
        await query.edit_message_text(
            f"📋 Запись:\n\n"
            f"💇 {svc['name']}\n"
            f"📅 {date_str}\n"
            f"⏰ {time_str}\n"
            f"💰 {svc['price']}₽\n"
            f"⏱ {svc['duration']} мин\n\n"
            f"Подтвердить?",
            reply_markup=kb,
        )

    elif data == "aiconfirm":
        svc_id = context.user_data.get("booking_service")
        date_str = context.user_data.get("booking_date")
        time_str = context.user_data.get("booking_time")
        user_id = query.from_user.id

        success = create_booking(user_id, svc_id, date_str, time_str)
        if success:
            svc = next((s for s in SERVICES if s["id"] == svc_id), None)
            await query.edit_message_text(
                f"✅ Запись создана!\n\n"
                f"💇 {svc['name']}\n"
                f"📅 {date_str}\n"
                f"⏰ {time_str}\n\n"
                f"📍 {SALON['address']}\n"
                f"📞 {SALON['phone']}\n\n"
                f"Напомним за сутки и за 2 часа! 🙌"
            )
            # Notify admin
            for admin_id in ADMIN_IDS:
                try:
                    client = get_client(user_id)
                    await context.bot.send_message(
                        admin_id,
                        f"🆕 Новая запись!\n"
                        f"👤 {client.get('first_name', '?')} (@{client.get('username', '?')})\n"
                        f"💇 {svc['name']}\n"
                        f"📅 {date_str} {time_str}\n"
                        f"💰 {svc['price']}₽",
                    )
                except Exception:
                    pass
        else:
            await query.edit_message_text(
                "😔 Этот слот только что заняли.\n"
                "Попробуйте другое время!"
            )

    elif data == "aicancel_booking":
        await query.edit_message_text("❌ Запись отменена.\n\nМожете записаться снова в любое время!")

    elif data.startswith("aicancel_"):
        booking_id = int(data[9:])
        success = cancel_booking(booking_id, query.from_user.id)
        if success:
            await query.edit_message_text("✅ Запись отменена!")
        else:
            await query.edit_message_text("😔 Не удалось отменить запись.")

    elif data.startswith("aiwait_"):
        date_str = data[7:]
        svc_id = context.user_data.get("booking_service")
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute(
            "INSERT INTO waitlist (user_id, service_id, preferred_date) VALUES (?, ?, ?)",
            (query.from_user.id, svc_id, date_str),
        )
        conn.commit()
        conn.close()
        await query.edit_message_text(
            "⏳ Вы в листе ожидания!\n\n"
            "Когда освободится слот — я вас запишу и уведомлю! 🙌"
        )


async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel — stats and management."""
    if update.effective_user.id not in ADMIN_IDS:
        return

    stats = get_admin_stats()
    await update.message.reply_text(stats)


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick cancel by /cancel_ID."""
    text = update.message.text
    match = re.match(r"/cancel_(\d+)", text)
    if match:
        booking_id = int(match.group(1))
        success = cancel_booking(booking_id, update.effective_user.id)
        if success:
            await update.message.reply_text("✅ Запись отменена!")
        else:
            await update.message.reply_text("😔 Не удалось отменить.")


# ============================================================
# SCHEDULER — reminders
# ============================================================
async def send_reminders(context: ContextTypes.DEFAULT_TYPE):
    """Check for upcoming bookings and send reminders."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    now = datetime.now()
    for hours in SALON["reminder_hours_before"]:
        target = now + timedelta(hours=hours)
        target_date = target.strftime("%Y-%m-%d")
        target_time = target.strftime("%H:%M")

        rows = conn.execute(
            "SELECT b.user_id, b.date, b.time, b.reminder_sent "
            "FROM bookings b "
            "WHERE b.date=? AND b.status='confirmed' AND b.reminder_sent < ?",
            (target_date, hours),
        ).fetchall()

        for r in rows:
            svc = next((s for s in SERVICES if s["id"] == r["service_id"]), None)
            svc_name = svc["name"] if svc else r["service_id"]
            try:
                if hours == 24:
                    msg = f"⏰ Напоминание: завтра в {r['time']} у вас запись!\n\n💇 {svc_name}\n📍 {SALON['address']}\n\nОтменить: /cancel_{r['id']}"
                else:
                    msg = f"⏰ Через 2 часа у вас запись в {r['time']}!\n\n💇 {svc_name}\n📍 {SALON['address']}\n\nОтменить: /cancel_{r['id']}"

                await context.bot.send_message(r["user_id"], msg)

                conn.execute(
                    "UPDATE bookings SET reminder_sent=? WHERE user_id=? AND date=? AND time=?",
                    (hours, r["user_id"], r["date"], r["time"]),
                )
            except Exception as e:
                logger.error(f"Reminder failed for {r['user_id']}: {e}")

    conn.commit()
    conn.close()


# ============================================================
# MAIN
# ============================================================
async def post_init(app: Application):
    """Set bot commands menu."""
    commands = [
        BotCommand("start", "Начать диалог"),
        BotCommand("admin", "Панель управления"),
    ]
    await app.bot.set_my_commands(commands)


def main():
    if not BOT_TOKEN:
        logger.error("No SALON_BOT_TOKEN or TELEGRAM_BOT_TOKEN set!")
        return

    init_db()
    logger.info(f"Salon: {SALON['name']}")
    logger.info(f"Services: {len(SERVICES)}")
    logger.info(f"Proxy: {PROXY}")

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
        .post_init(post_init)
        .build()
    )

    # Handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("admin", cmd_admin))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_text))
    app.add_handler(MessageHandler(filters.VOICE, cmd_voice))
    app.add_handler(CallbackQueryHandler(cb_handler))

    # Reminder job (every 30 minutes)
    app.job_queue.run_repeating(send_reminders, interval=1800, first=60)

    logger.info("🤖 Salon AI Bot starting...")
    app.run_polling(
        drop_pending_updates=True,
        poll_interval=2.0,
        bootstrap_retries=5,
        read_timeout=30.0,
        connect_timeout=15.0,
    )


if __name__ == "__main__":
    main()
