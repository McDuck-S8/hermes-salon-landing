"""
Salon Bot — Keyboards (2026 Design)
Backend Architect: clean UX, gradient accents, branded patterns.
"""

from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import date, timedelta
from config import config


# ══════════════════════════════════════════════════════════
# DESIGN TOKENS
# ══════════════════════════════════════════════════════════

# Each button can carry emoji prefix for visual hierarchy.
# Colors are handled by Telegram theme, but we structure for clarity.


# ══════════════════════════════════════════════════════════
# MAIN MENU
# ══════════════════════════════════════════════════════════

def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Записаться", callback_data="book_start", style="primary")
    builder.button(text="📋 Мои записи", callback_data="my_bookings")
    builder.button(text="🎯 Спецпредложение дня", callback_data="daily_special")
    builder.button(text="🎲 Брось кубик — скидка!", callback_data="dice_game")
    builder.button(text="📸 Галерея работ", callback_data="gallery")
    builder.button(text="🧠 Тест о волосах", callback_data="quiz")
    builder.button(text="💳 Моя карта лояльности", callback_data="loyalty")
    builder.button(text="ℹ️ Контакты", callback_data="contacts")
    builder.button(text="⭐ Оставить отзыв", callback_data="leave_review")
    builder.adjust(1)
    return builder.as_markup()


def back_to_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    return builder.as_markup()


# ══════════════════════════════════════════════════════════
# SERVICES
# ══════════════════════════════════════════════════════════

def services_kb(services: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for s in services:
        emoji = s.get("emoji", "💇")
        price = s.get("price", 0)
        dur = s.get("duration_min", 60)
        label = f"{emoji} {s['name']} — {price}₽ ({dur}мин)"
        builder.button(text=label, callback_data=f"svc_{s['id']}")
    builder.button(text="⬅️ Назад", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


# ══════════════════════════════════════════════════════════
# MASTERS
# ══════════════════════════════════════════════════════════

def masters_kb(masters: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for m in masters:
        label = f"👩‍🎨 {m['name']}"
        if m.get('bio'):
            label += f" — {m['bio'][:40]}"
        builder.button(text=label, callback_data=f"mst_{m['id']}")
    builder.button(text="⬅️ Назад", callback_data="book_start")
    builder.adjust(1)
    return builder.as_markup()


# ══════════════════════════════════════════════════════════
# DATES — Calendar-style
# ══════════════════════════════════════════════════════════

def dates_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    today = date.today()
    days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

    # Header row: day names
    for d in days_of_week:
        builder.button(text=d, callback_data="noop")

    for d in range(config.BOOKING_DAYS_AHEAD):
        dt = today + timedelta(days=d)
        day_name = days_of_week[dt.weekday()]
        is_today = d == 0
        label = f"{'📌 ' if is_today else ''}{dt.day} {day_name}"
        if d == 0:
            label = "📌 Сегодня"
        elif d == 1:
            label = "📌 Завтра"
        builder.button(text=label, callback_data=f"date_{dt.isoformat()}")

    builder.button(text="⬅️ Назад", callback_data="main_menu")
    builder.adjust(7, *[1] * config.BOOKING_DAYS_AHEAD, 1)
    return builder.as_markup()


# ══════════════════════════════════════════════════════════
# TIME SLOTS
# ══════════════════════════════════════════════════════════

def times_kb(slots: list, date_iso: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # Group by morning/afternoon/evening
    morning = [s for s in slots if int(s.split(":")[0]) < 12]
    afternoon = [s for s in slots if 12 <= int(s.split(":")[0]) < 17]
    evening = [s for s in slots if int(s.split(":")[0]) >= 17]

    groups = [
        ("🌅 Утро", morning),
        ("☀️ День", afternoon),
        ("🌆 Вечер", evening),
    ]

    first_group = True
    for title, group in groups:
        if not group:
            continue
        if first_group:
            first_group = False
        else:
            pass  # visual separator
        for t in group:
            builder.button(text=t, callback_data=f"time_{date_iso}_{t}")

    builder.button(text="⬅️ Назад", callback_data="my_bookings")
    builder.adjust(3)
    return builder.as_markup()


# ══════════════════════════════════════════════════════════
# CONFIRMATION
# ══════════════════════════════════════════════════════════

def confirm_kb(params: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data=f"confirm_{params}", style="success")
    builder.button(text="❌ Отменить", callback_data="cancel_flow", style="danger")
    builder.adjust(2)
    return builder.as_markup()


# ══════════════════════════════════════════════════════════
# BOOKING ACTIONS
# ══════════════════════════════════════════════════════════

def booking_actions_kb(booking_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отменить запись", callback_data=f"del_{booking_id}", style="danger")
    builder.button(text="⭐ Оценить визит", callback_data=f"review_{booking_id}", style="primary")
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


# ══════════════════════════════════════════════════════════
# RATING
# ══════════════════════════════════════════════════════════

def rating_kb(booking_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for r in range(1, 6):
        stars = "⭐" * r
        builder.button(text=stars, callback_data=f"rate_{booking_id}_{r}")
    builder.button(text="⬅️ Назад", callback_data="main_menu")
    builder.adjust(5, 1)
    return builder.as_markup()


# ══════════════════════════════════════════════════════════
# SHARE & REVIEW
# ══════════════════════════════════════════════════════════

def share_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📤 Поделиться ботом", switch_inline_query="Запишись в салон → ", style="primary")
    builder.button(text="⭐ Оставить отзыв", callback_data="leave_review")
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


# ══════════════════════════════════════════════════════════
# MINI APP (2026)
# ══════════════════════════════════════════════════════════

def mini_app_kb() -> InlineKeyboardMarkup:
    """Opens the Telegram Mini App for full booking experience."""
    builder = InlineKeyboardBuilder()
    if config.WEBAPP_URL:
        builder.button(
            text="✨ Записаться через Mini App",
            web_app=WebAppInfo(url=config.WEBAPP_URL),
            style="primary",
        )
    builder.button(text="📅 Обычная запись", callback_data="book_start")
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


# ══════════════════════════════════════════════════════════
# ADMIN
# ══════════════════════════════════════════════════════════

def admin_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Статистика", callback_data="a_stats")
    builder.button(text="👩‍🎨 Мастера", callback_data="a_masters")
    builder.button(text="💇 Услуги", callback_data="a_services")
    builder.button(text="📅 Записи", callback_data="a_bookings")
    builder.button(text="👥 Клиенты", callback_data="a_clients")
    builder.button(text="🔑 Коды мастеров", callback_data="a_master_codes")
    builder.button(text="📤 Рассылка", callback_data="a_broadcast")
    builder.adjust(2)
    return builder.as_markup()


def admin_masters_list_kb(masters: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for m in masters:
        icon = "✅" if m.get("is_active") or m.get("active") else "❌"
        builder.button(text=f"{icon} {m['name']}", callback_data=f"am_{m['id']}")
    builder.button(text="➕ Добавить мастера", callback_data="am_add")
    builder.button(text="⬅️ Назад", callback_data="a_menu")
    builder.adjust(1)
    return builder.as_markup()


def admin_services_list_kb(services: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for s in services:
        icon = "✅" if s.get("is_active") or s.get("active") else "❌"
        builder.button(
            text=f"{icon} {s.get('emoji','💇')} {s['name']} — {s['price']}₽",
            callback_data=f"as_{s['id']}",
        )
    builder.button(text="➕ Добавить услугу", callback_data="as_add")
    builder.button(text="⬅️ Назад", callback_data="a_menu")
    builder.adjust(1)
    return builder.as_markup()
