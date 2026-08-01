"""Master panel — schedule, bookings, stats."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import keyboards as kb
from utils import format_date
from datetime import date

router = Router()


class MasterLogin(StatesGroup):
    waiting_code = State()


# ── Login ───────────────────────────────────────────────
@router.message(F.text == "/master")
async def master_login(msg: Message, state: FSMContext):
    master = await db.get_master_by_tg(msg.from_user.id)
    if master:
        await msg.answer(
            f"👋 Здравствуйте, <b>{master['name']}</b>!

Выберите действие:",
            reply_markup=kb.master_menu_kb(),
            parse_mode="HTML",
        )
    else:
        await state.set_state(MasterLogin.waiting_code)
        await msg.answer("🔑 Введите код доступа (получите у администратора):")


@router.message(MasterLogin.waiting_code)
async def process_code(msg: Message, state: FSMContext):
    code = msg.text.strip()
    import aiosqlite
    from database import DB_PATH
    db_conn = await aiosqlite.connect(DB_PATH)
    db_conn.row_factory = aiosqlite.Row
    try:
        rows = await db_conn.execute_fetchall(
            "SELECT mu.*, m.name FROM master_users mu JOIN masters m ON mu.master_id=m.id WHERE mu.access_code=?",
            (code,),
        )
        if not rows:
            await msg.answer("❌ Неверный код. Попробуйте ещё раз или /cancel")
            return
        row = dict(rows[0])
        # Link TG account
        await db_conn.execute(
            "UPDATE master_users SET tg_user_id=? WHERE access_code=?",
            (msg.from_user.id, code),
        )
        await db_conn.commit()
    finally:
        await db_conn.close()

    await state.clear()
    await msg.answer(
        f"✅ Вы вошли как <b>{row['name']}</b>!",
        reply_markup=kb.master_menu_kb(),
        parse_mode="HTML",
    )


# ── Menu ────────────────────────────────────────────────
@router.callback_query(F.data == "m_menu")
async def master_menu(cb: CallbackQuery):
    master = await db.get_master_by_tg(cb.from_user.id)
    if not master:
        await cb.message.edit_text("❌ Вы не авторизованы. Введите /master")
        return
    await cb.message.edit_text(
        f"👩‍🎨 <b>{master['name']}</b>
Выберите действие:",
        reply_markup=kb.master_menu_kb(),
        parse_mode="HTML",
    )


# ── Today's bookings ────────────────────────────────────
@router.callback_query(F.data == "m_today")
async def today_bookings(cb: CallbackQuery):
    master = await db.get_master_by_tg(cb.from_user.id)
    if not master:
        await cb.answer("Не авторизованы")
        return

    today = date.today().isoformat()
    bookings = await db.get_master_bookings(master["id"], today)

    if not bookings:
        await cb.message.edit_text(
            f"📋 На сегодня ({format_date(today)}) записей нет.",
            reply_markup=kb.master_menu_kb(),
        )
        return

    text = f"📋 <b>Записи на {format_date(today)}:</b>

"
    for b in bookings:
        text += (
            f"⏰ {b['time_slot']} — {b['service_name']}
"
            f"   👤 {b['client_name']}"
        )
        if b.get("client_phone"):
            text += f" ({b['client_phone']})"
        text += "

"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await cb.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅ Назад", callback_data="m_menu")]
        ]),
        parse_mode="HTML",
    )


# ── Pick date ───────────────────────────────────────────
@router.callback_query(F.data == "m_pick_date")
async def pick_date(cb: CallbackQuery):
    await cb.message.edit_text("📅 Выберите дату:", reply_markup=kb.master_dates_kb())


@router.callback_query(F.data.startswith("mdate_"))
async def date_bookings(cb: CallbackQuery):
    master = await db.get_master_by_tg(cb.from_user.id)
    if not master:
        await cb.answer("Не авторизованы")
        return

    date_iso = cb.data.split("_", 1)[1]
    bookings = await db.get_master_bookings(master["id"], date_iso)

    if not bookings:
        await cb.message.edit_text(
            f"📋 На {format_date(date_iso)} записей нет.",
            reply_markup=kb.master_dates_kb(),
        )
        return

    text = f"📋 <b>Записи на {format_date(date_iso)}:</b>

"
    for b in bookings:
        text += f"⏰ {b['time_slot']} — {b['service_name']} — {b['client_name']}
"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await cb.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅ Назад", callback_data="m_menu")]
        ]),
        parse_mode="HTML",
    )


# ── Stats ───────────────────────────────────────────────
@router.callback_query(F.data == "m_stats")
async def master_stats(cb: CallbackQuery):
    master = await db.get_master_by_tg(cb.from_user.id)
    if not master:
        await cb.answer("Не авторизованы")
        return

    today = date.today()
    month_start = today.replace(day=1).isoformat()
    all_bookings = await db.get_master_bookings(master["id"])
    month_bookings = [b for b in all_bookings if b["booking_date"] >= month_start and b["status"] == "confirmed"]
    rating, count = await db.get_master_rating(master["id"])

    from config import SLOT_DURATION
    total_hours = len(month_bookings) * SLOT_DURATION / 60

    await cb.message.edit_text(
        f"📊 <b>Статистика — {master['name']}</b>

"
        f"📅 За этот месяц:
"
        f"  Записей: {len(month_bookings)}
"
        f"  Часов работы: {total_hours:.1f}

"
        f"⭐ Рейтинг: {rating if count > 0 else 'нет отзывов'} ({count} отзывов)",
        reply_markup=kb.master_menu_kb(),
        parse_mode="HTML",
    )
