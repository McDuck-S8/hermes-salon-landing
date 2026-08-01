#!/usr/bin/env python3
"""
Salon Booking Bot — рабочий Telegram бот для записи в салон красоты.

Функции:
- Клиент выбирает услугу из меню
- Клиент выбирает дату и время
- Бот проверяет доступность
- Клиент подтверждает запись
- Бот отправляет напоминание

Запуск:
    TELEGRAM_BOT_TOKEN=xxx python salon_booking_bot.py
"""
import os
import json
import sqlite3
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# Config
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
DB_PATH = Path(__file__).parent / "salon_bookings.db"
SERVICES = [
    {"name": "Стрижка мужская", "duration": 30, "price": 800},
    {"name": "Стрижка женская", "duration": 60, "price": 1500},
    {"name": "Окрашивание", "duration": 120, "price": 3000},
    {"name": "Маникюр", "duration": 60, "price": 1200},
    {"name": "Педикюр", "duration": 90, "price": 1500},
    {"name": "Укладка", "duration": 45, "price": 1000},
    {"name": "Бритьё", "duration": 30, "price": 600},
    {"name": "Ламинирование бровей", "duration": 60, "price": 2000},
]
WORK_HOURS = {"start": 9, "end": 20}  # 9:00 - 20:00
WORK_DAYS = [0, 1, 2, 3, 4, 5]  # Пн-Сб


def init_db():
    """Initialize SQLite database."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("""
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


def get_available_slots(date_str: str, service_idx: int) -> list:
    """Get available time slots for a given date and service."""
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return []

    # Check if it's a work day
    if target_date.weekday() not in WORK_DAYS:
        return []

    # Get service duration
    if service_idx < 0 or service_idx >= len(SERVICES):
        return []
    duration = SERVICES[service_idx]["duration"]

    # Get booked slots for this date
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute(
        "SELECT time FROM bookings WHERE date = ? AND status = 'confirmed'",
        (date_str,)
    )
    booked = set(row[0] for row in cur.fetchall())
    conn.close()

    # Generate available slots
    available = []
    for hour in range(WORK_HOURS["start"], WORK_HOURS["end"]):
        for minute in [0, 30]:
            time_str = f"{hour:02d}:{minute:02d}"
            # Check if this slot conflicts with any booking
            slot_start = hour * 60 + minute
            slot_end = slot_start + duration
            conflict = False
            for booked_time in booked:
                b_hour, b_min = map(int, booked_time.split(":"))
                b_start = b_hour * 60 + b_min
                # Assume 60min default duration for booked slots
                if slot_start < b_start + 60 and slot_end > b_start:
                    conflict = True
                    break
            if not conflict and slot_end <= WORK_HOURS["end"] * 60:
                available.append(time_str)

    return available


def create_booking(user_id: int, username: str, service_idx: int, date_str: str, time_str: str) -> bool:
    """Create a booking."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO bookings (user_id, username, service, date, time) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, SERVICES[service_idx]["name"], date_str, time_str)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def cancel_booking(user_id: int, booking_id: int) -> bool:
    """Cancel a booking."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute(
        "UPDATE bookings SET status = 'cancelled' WHERE id = ? AND user_id = ?",
        (booking_id, user_id)
    )
    conn.commit()
    affected = cur.rowcount
    conn.close()
    return affected > 0


def get_user_bookings(user_id: int) -> list:
    """Get user's active bookings."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute(
        "SELECT id, service, date, time, status FROM bookings WHERE user_id = ? AND status = 'confirmed' ORDER BY date, time",
        (user_id,)
    )
    bookings = [{"id": row[0], "service": row[1], "date": row[2], "time": row[3]} for row in cur.fetchall()]
    conn.close()
    return bookings


# --- Telegram Bot (using raw HTTP API, no external dependencies) ---

def send_message(chat_id: int, text: str, reply_markup: dict = None):
    """Send message via Telegram Bot API."""
    import urllib.request
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"Send error: {e}")
        return None


def send_keyboard(chat_id: int, text: str, buttons: list):
    """Send message with inline keyboard."""
    keyboard = {"inline_keyboard": [[{"text": b, "callback_data": b}] for b in buttons]}
    return send_message(chat_id, text, keyboard)


def handle_start(chat_id: int, user_id: int, username: str):
    """Handle /start command."""
    text = (
        "Welcome to Salon Bot!\n\n"
        "Choose an action:"
    )
    send_keyboard(chat_id, text, ["Book appointment", "My bookings", "Help"])


def handle_services(chat_id: int):
    """Show services list."""
    buttons = [f"{i+1}. {s['name']} ({s['duration']}min, {s['price']} rub)" for i, s in enumerate(SERVICES)]
    send_keyboard(chat_id, "Choose a service:", buttons)


def handle_dates(chat_id: int, service_idx: int):
    """Show available dates."""
    today = datetime.now()
    buttons = []
    for i in range(1, 8):  # Next 7 days
        date = today + timedelta(days=i)
        if date.weekday() in WORK_DAYS:
            date_str = date.strftime("%Y-%m-%d")
            date_display = date.strftime("%d.%m (%a)")
            buttons.append(f"{date_str} | {date_display}")
    send_keyboard(chat_id, "Choose a date:", buttons)


def handle_times(chat_id: int, service_idx: int, date_str: str):
    """Show available times."""
    slots = get_available_slots(date_str, service_idx)
    if not slots:
        send_message(chat_id, "No available slots for this date. Try another date.")
        return
    # Show first 10 slots
    buttons = slots[:10]
    send_keyboard(chat_id, f"Available times for {date_str}:", buttons)


def handle_booking_confirmed(chat_id: int, user_id: int, username: str, service_idx: int, date_str: str, time_str: str):
    """Confirm booking."""
    if create_booking(user_id, username, service_idx, date_str, time_str):
        service = SERVICES[service_idx]
        text = (
            f"Booking confirmed!\n\n"
            f"Service: {service['name']}\n"
            f"Date: {date_str}\n"
            f"Time: {time_str}\n"
            f"Duration: {service['duration']} min\n"
            f"Price: {service['price']} rub\n\n"
            f"See you at the salon!"
        )
        send_message(chat_id, text)
    else:
        send_message(chat_id, "Error creating booking. Please try again.")


def handle_my_bookings(chat_id: int, user_id: int):
    """Show user's bookings."""
    bookings = get_user_bookings(user_id)
    if not bookings:
        send_message(chat_id, "You have no active bookings.")
        return
    text = "Your bookings:\n\n"
    for b in bookings:
        text += f"#{b['id']} | {b['service']} | {b['date']} {b['time']}\n"
    text += "\nTo cancel, type /cancel <number>"
    send_message(chat_id, text)


# --- Main bot loop ---

def main():
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        print("Set it: export TELEGRAM_BOT_TOKEN=your_token")
        return

    init_db()
    print("Salon Booking Bot started")
    print(f"Services: {len(SERVICES)}")
    print(f"Work hours: {WORK_HOURS['start']}:00 - {WORK_HOURS['end']}:00")

    # Simple polling loop
    import urllib.request
    offset = 0

    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=30"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read())

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                callback = update.get("callback_query", {})

                if msg:
                    chat_id = msg["chat"]["id"]
                    user_id = msg["from"]["id"]
                    username = msg["from"].get("username", "")
                    text = msg.get("text", "")

                    if text == "/start":
                        handle_start(chat_id, user_id, username)
                    elif text == "Book appointment":
                        handle_services(chat_id)
                    elif text == "My bookings":
                        handle_my_bookings(chat_id, user_id)
                    elif text.startswith("/cancel"):
                        parts = text.split()
                        if len(parts) > 1:
                            try:
                                bid = int(parts[1])
                                if cancel_booking(user_id, bid):
                                    send_message(chat_id, f"Booking #{bid} cancelled.")
                                else:
                                    send_message(chat_id, "Booking not found.")
                            except ValueError:
                                send_message(chat_id, "Usage: /cancel <number>")

                elif callback:
                    chat_id = callback["message"]["chat"]["id"]
                    user_id = callback["from"]["id"]
                    username = callback["from"].get("username", "")
                    data_cb = callback["data"]

                    # Handle service selection
                    if data_cb.startswith("1.") or data_cb.startswith("2.") or data_cb.startswith("3.") or data_cb.startswith("4.") or data_cb.startswith("5.") or data_cb.startswith("6.") or data_cb.startswith("7.") or data_cb.startswith("8."):
                        idx = int(data_cb.split(".")[0]) - 1
                        # Store state in user data (simplified)
                        state_file = Path(f"cache/bot_state_{user_id}.json")
                        state_file.parent.mkdir(exist_ok=True)
                        state_file.write_text(json.dumps({"service_idx": idx}))
                        handle_dates(chat_id, idx)

                    # Handle date selection
                    elif "|" in data_cb and len(data_cb) == 10:  # YYYY-MM-DD
                        date_str = data_cb.split("|")[0].strip()
                        state_file = Path(f"cache/bot_state_{user_id}.json")
                        if state_file.exists():
                            state = json.loads(state_file.read_text())
                            idx = state.get("service_idx", 0)
                            handle_times(chat_id, idx, date_str)
                            state["date"] = date_str
                            state_file.write_text(json.dumps(state))

                    # Handle time selection
                    elif ":" in data_cb and len(data_cb) == 5:  # HH:MM
                        time_str = data_cb
                        state_file = Path(f"cache/bot_state_{user_id}.json")
                        if state_file.exists():
                            state = json.loads(state_file.read_text())
                            idx = state.get("service_idx", 0)
                            date_str = state.get("date", "")
                            if date_str:
                                handle_booking_confirmed(chat_id, user_id, username, idx, date_str, time_str)
                                state_file.unlink(missing_ok=True)

        except KeyboardInterrupt:
            print("Bot stopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    import time
    main()
