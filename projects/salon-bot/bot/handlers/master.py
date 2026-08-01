"""
Salon Bot — Master Panel
Backend Architect: view schedule, confirm/cancel, stats.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import bot.db as db
import bot.keyboards as kb
from datetime import date

router = Router()


class MasterAuth(StatesGroup):
    waiting_code = State()


# ── Auth ────────────────────────────────────────────────────
@router.message(F.text == "/master")
async def master_login(msg: Message, state: FSMContext):
    master = await db.get_master_by_tg(msg.from_user.id)
    if master:
        await show_master_menu(msg, master)
        return
    await state.set_state(MasterAuth.waiting_code)
    await msg.answer(
        "🔑 Введите код доступа, полученный от администратора:"
    )


@router.message(MasterAuth.waiting_code)
async def master_auth_code(msg: Message, state: FSMContext):
    code = msg.text.strip().upper()
    # Find master by code
    db_conn = await db.get_db()
    try:
        rows = await db_conn.execute_fetchall(
            "SELECT master_id FROM master_users WHERE access_code=? AND (tg_user_id=0 OR tg_user_id=?)",
            (code, msg.from_user.id),
        )
        if not rows:
            await msg.answer("❌ Неверный код. Попробуйте ещё раз или обратитесь к администратору.")
            return

        master_id = rows[0]["master_id"]
        await db.link_master_tg(master_id, msg.from_user.id, code)
        master = await db.get_master(master_id)
        await state.clear()
        await msg.answer(
            f"✅ Вы авторизованы как <b>{master['name']}</b>",
            parse_mode="HTML",
        )
        await show_master_menu(msg, master)
    finally:
        await db_conn.close()


async def show_master_menu(msg: Message, master: dict):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await msg.answer(
        f"👩‍🎨 <b>{master['name']}</b>\n\n"
        f"Панель мастера:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 Записи на сегодня", callback_data=f"m_today_{master['id']}")],
            [InlineKeyboardButton(text="📅 Записи на дату", callback_data=f"m_date_{master['id']}")],
            [InlineKeyboardButton(text="📊 Моя статистика", callback_data=f"m_stats_{master['id']}")],
            [InlineKeyboardButton(text="🏠 Выйти", callback_data="m_logout")],
        ]),
        parse_mode="HTML",
    )


# ── Menu reply (for callback) ──────────────────────────────
async def master_menu_kb(master_id: int):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Записи на сегодня", callback_data=f"m_today_{master_id}")],
        [InlineKeyboardButton(text="📅 Записи на дату", callback_data=f"m_date_{master_id}")],
        [InlineKeyboardButton(text="📊 Моя статистика", callback_data=f"m_stats_{master_id}")],
        [InlineKeyboardButton(text="🏠 Выйти", callback_data="m_logout")],
    ])


async def get_master_or_deny(cb: CallbackQuery) -> dict | None:
    master = await db.get_master_by_tg(cb.from_user.id)
    if not master:
        await cb.answer("⛔ Вы не авторизованы")
        return None
    return master


# ── Today ───────────────────────────────────────────────────
@router.callback_query(F.data.startswith("m_today_"))
async def master_today(cb: CallbackQuery):
    master = await get_master_or_deny(cb)
    if not master:
        return

    today = date.today().isoformat()
    bookings = await db.get_master_bookings(master["id"], today)

    if not bookings:
        await cb.message.edit_text(
            f"📅 На сегодня записей нет.",
            reply_markup=await master_menu_kb(master["id"]),
        )
        return

    text = f"📅 <b>Записи на сегодня ({today}):</b>\n\n"
    for b in bookings:
        text += (
            f"⏰ <b>{b['time_slot']}</b>\n"
            f"  👤 {b['client_name']}\n"
            f"  💇 {b.get('service_name', '?')}\n"
            f"  📞 {b.get('client_phone', '—')}\n\n"
        )

    await cb.message.edit_text(
        text[:4000],
        reply_markup=await master_menu_kb(master["id"]),
        parse_mode="HTML",
    )


# ── Stats ───────────────────────────────────────────────────
@router.callback_query(F.data.startswith("m_stats_"))
async def master_stats(cb: CallbackQuery):
    master = await get_master_or_deny(cb)
    if not master:
        return

    rating, count = await db.get_master_rating(master["id"])

    db_conn = await db.get_db()
    try:
        today = await db_conn.execute_fetchall(
            "SELECT COUNT(*) as c FROM bookings WHERE master_id=? AND booking_date=? AND status='confirmed'",
            (master["id"], date.today().isoformat()),
        )
        total = await db_conn.execute_fetchall(
            "SELECT COUNT(*) as c FROM bookings WHERE master_id=? AND status='completed'",
            (master["id"],),
        )
        reviews = await db_conn.execute_fetchall(
            "SELECT COUNT(*) as c FROM reviews WHERE master_id=?", (master["id"],)
        )
    finally:
        await db_conn.close()

    await cb.message.edit_text(
        f"📊 <b>Статистика: {master['name']}</b>\n\n"
        f"⭐ Рейтинг: {rating} ({count} отзывов)\n"
        f"📅 Сегодня записей: {today[0]['c']}\n"
        f"✅ Всего выполнено: {total[0]['c']}\n"
        f"💬 Отзывов: {reviews[0]['c']}",
        reply_markup=await master_menu_kb(master["id"]),
        parse_mode="HTML",
    )


# ── Logout ──────────────────────────────────────────────────
@router.callback_query(F.data == "m_logout")
async def master_logout(cb: CallbackQuery):
    await cb.message.edit_text("Вы вышли из панели мастера.")
