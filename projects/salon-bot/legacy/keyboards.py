"""All inline keyboards."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOOKING_DAYS_AHEAD
from utils import get_available_dates


# ── Client keyboards ────────────────────────────────────
def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💇 Записаться", callback_data="book_start")],
        [InlineKeyboardButton(text="📋 Мои записи", callback_data="my_bookings")],
        [InlineKeyboardButton(text="📞 Контакты", callback_data="contacts")],
    ])


def services_kb(services: list):
    rows = []
    for s in services:
        text = f"{s['name']} — {s['price']}₽ ({s['duration_min']}мин)"
        rows.append([InlineKeyboardButton(text=text, callback_data=f"svc_{s['id']}")])
    rows.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_flow")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def masters_kb(masters: list):
    rows = []
    for m in masters:
        rows.append([InlineKeyboardButton(text=f"👩‍🎨 {m['name']}", callback_data=f"mst_{m['id']}")])
    rows.append([InlineKeyboardButton(text="⬅ Назад", callback_data="book_start")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def dates_kb():
    dates = get_available_dates()
    rows = []
    for iso, label in dates:
        rows.append([InlineKeyboardButton(text=f"📅 {label}", callback_data=f"date_{iso}")])
    rows.append([InlineKeyboardButton(text="⬅ Назад", callback_data="book_start")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def times_kb(slots: list, date_iso: str):
    rows = []
    row = []
    for i, slot in enumerate(slots):
        row.append(InlineKeyboardButton(text=slot, callback_data=f"time_{date_iso}_{slot}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅ Назад", callback_data="book_start")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_kb(booking_params: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_{booking_params}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_flow")],
    ])


def booking_actions_kb(booking_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить запись", callback_data=f"del_{booking_id}")],
        [InlineKeyboardButton(text="⭐ Оставить отзыв", callback_data=f"review_{booking_id}")],
        [InlineKeyboardButton(text="🏠 Меню", callback_data="main_menu")],
    ])


def rating_kb(booking_id: int):
    rows = []
    row = []
    for i in range(1, 6):
        star = "⭐" * i
        row.append(InlineKeyboardButton(text=star, callback_data=f"rate_{booking_id}_{i}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def back_to_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Меню", callback_data="main_menu")]
    ])


# ── Master keyboards ────────────────────────────────────
def master_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Записи на сегодня", callback_data="m_today")],
        [InlineKeyboardButton(text="📅 Записи на дату", callback_data="m_pick_date")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="m_stats")],
    ])


def master_dates_kb():
    dates = get_available_dates()
    rows = []
    for iso, label in dates:
        rows.append([InlineKeyboardButton(text=f"📅 {label}", callback_data=f"mdate_{iso}")])
    rows.append([InlineKeyboardButton(text="⬅ Назад", callback_data="m_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── Admin keyboards ─────────────────────────────────────
def admin_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="a_stats")],
        [InlineKeyboardButton(text="👩‍🎨 Мастера", callback_data="a_masters")],
        [InlineKeyboardButton(text="💇 Услуги", callback_data="a_services")],
        [InlineKeyboardButton(text="📅 Все записи", callback_data="a_bookings")],
        [InlineKeyboardButton(text="👥 Клиенты", callback_data="a_clients")],
        [InlineKeyboardButton(text="🔑 Коды мастеров", callback_data="a_master_codes")],
    ])


def admin_masters_list_kb(masters: list):
    rows = []
    for m in masters:
        status = "✅" if m["active"] else "❌"
        rows.append([InlineKeyboardButton(
            text=f"{status} {m['name']}", callback_data=f"am_{m['id']}"
        )])
    rows.append([InlineKeyboardButton(text="➕ Добавить мастера", callback_data="am_add")])
    rows.append([InlineKeyboardButton(text="⬅ Назад", callback_data="a_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_services_list_kb(services: list):
    rows = []
    for s in services:
        status = "✅" if s["active"] else "❌"
        rows.append([InlineKeyboardButton(
            text=f"{status} {s['name']} — {s['price']}₽",
            callback_data=f"as_{s['id']}"
        )])
    rows.append([InlineKeyboardButton(text="➕ Добавить услугу", callback_data="as_add")])
    rows.append([InlineKeyboardButton(text="⬅ Назад", callback_data="a_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
