"""
Salon Bot — Admin Panel
Backend Architect: CRUD for masters, services, bookings, stats.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import bot.db as db
import bot.keyboards as kb
from config import config
from datetime import date, timedelta

router = Router()


class AddMaster(StatesGroup):
    name = State()
    phone = State()


class AddService(StatesGroup):
    name = State()
    duration = State()
    price = State()


class Broadcast(StatesGroup):
    text = State()


# ── Guard ───────────────────────────────────────────────────
async def require_admin(cb: CallbackQuery) -> bool:
    if not await db.is_admin(cb.from_user.id):
        await cb.answer("⛔ Нет доступа")
        return False
    return True


# ── Menu ────────────────────────────────────────────────────
@router.message(F.text == "/admin")
async def admin_panel(msg: Message):
    if not await db.is_admin(msg.from_user.id):
        await msg.answer("⛔ Нет доступа")
        return
    await msg.answer(
        "🔧 <b>Панель администратора</b>",
        reply_markup=kb.admin_menu_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "a_menu")
async def admin_menu(cb: CallbackQuery):
    if not await require_admin(cb):
        return
    await cb.message.edit_text(
        "🔧 <b>Панель администратора</b>",
        reply_markup=kb.admin_menu_kb(),
        parse_mode="HTML",
    )


# ── Stats ───────────────────────────────────────────────────
@router.callback_query(F.data == "a_stats")
async def admin_stats(cb: CallbackQuery):
    if not await require_admin(cb):
        return
    stats = await db.get_stats()
    await cb.message.edit_text(
        f"📊 <b>Статистика</b>\n\n"
        f"📅 Сегодня записей: <b>{stats['bookings_today']}</b>\n"
        f"📅 За месяц: <b>{stats['bookings_month']}</b>\n"
        f"💰 Доход за месяц: <b>{stats['revenue_month']:,}₽</b>\n"
        f"📈 За неделю записей: <b>{stats['bookings_week']}</b>\n"
        f"👥 Всего клиентов: <b>{stats['clients_total']}</b>\n"
        f"🆕 Новых за неделю: <b>{stats['new_clients_week']}</b>\n"
        f"👩‍🎨 Активных мастеров: <b>{stats['masters_active']}</b>",
        reply_markup=kb.admin_menu_kb(),
        parse_mode="HTML",
    )


# ── Clients ─────────────────────────────────────────────────
@router.callback_query(F.data == "a_clients")
async def admin_clients(cb: CallbackQuery):
    if not await require_admin(cb):
        return

    db_conn = await db.get_db()
    try:
        rows = await db_conn.execute_fetchall(
            "SELECT * FROM clients ORDER BY created_at DESC LIMIT 20"
        )
        clients = [dict(r) for r in rows]
    finally:
        await db_conn.close()

    if not clients:
        await cb.message.edit_text("👥 Клиентов пока нет.", reply_markup=kb.admin_menu_kb())
        return

    text = "👥 <b>Клиенты (последние 20):</b>\n\n"
    for c in clients:
        visits = c.get("total_visits", 0)
        last = c.get("last_visit_date", "")
        last_str = f", последний: {last}" if last else ""
        text += f"• {c['name'] or 'Без имени'} — {visits} визитов{last_str}\n"
        if c.get("phone"):
            text += f"  📞 {c['phone']}\n"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await cb.message.edit_text(
        text[:4000],
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="a_menu")]
        ]),
        parse_mode="HTML",
    )


# ── Masters management ─────────────────────────────────────
@router.callback_query(F.data == "a_masters")
async def admin_masters(cb: CallbackQuery):
    if not await require_admin(cb):
        return
    masters = await db.get_masters(active_only=False)
    await cb.message.edit_text(
        "👩‍🎨 <b>Мастера:</b>",
        reply_markup=kb.admin_masters_list_kb(masters),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("am_"), ~F.data.startswith("am_"))
async def master_detail(cb: CallbackQuery):
    if not await require_admin(cb):
        return
    master_id = int(cb.data.split("_")[1])
    master = await db.get_master(master_id)
    if not master:
        await cb.answer("❌ Не найден")
        return

    services = await db.get_master_services(master_id)
    svc_names = ", ".join(s["name"] for s in services) if services else "нет"
    status = "✅ Активен" if master.get("is_active") else "❌ Неактивен"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await cb.message.edit_text(
        f"👩‍🎨 <b>{master['name']}</b>\n"
        f"📞 {master.get('phone') or 'не указан'}\n"
        f"📊 {status}\n"
        f"💇 Услуги: {svc_names}\n",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="❌ Деактивировать" if master.get("is_active") else "✅ Активировать",
                callback_data=f"am_toggle_{master_id}"
            )],
            [InlineKeyboardButton(text="🔗 Выдать код", callback_data=f"am_code_{master_id}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="a_masters")],
        ]),
        parse_mode="HTML",
    )


@router.callback_query(lambda c: c.data.startswith("am_toggle_"))
async def toggle_master(cb: CallbackQuery):
    if not await require_admin(cb):
        return
    master_id = int(cb.data.split("_")[2])
    await db.toggle_master(master_id)
    await cb.answer("✅ Статус изменён")
    # Refresh
    await admin_masters(cb)


@router.callback_query(F.data.startswith("am_code_"))
async def master_code(cb: CallbackQuery):
    if not await require_admin(cb):
        return
    master_id = int(cb.data.split("_")[2])
    code = await db.generate_master_code(master_id)
    master = await db.get_master(master_id)
    await cb.message.edit_text(
        f"🔑 Код для <b>{master['name'] if master else '?'}:</b>\n\n"
        f"<code>{code}</code>\n\n"
        f"Передайте мастеру. Он введёт /master и этот код.",
        reply_markup=kb.admin_menu_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "am_add")
async def add_master_start(cb: CallbackQuery, state: FSMContext):
    if not await require_admin(cb):
        return
    await state.set_state(AddMaster.name)
    await cb.message.edit_text("👤 Введите имя мастера:")


@router.message(AddMaster.name)
async def add_master_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text.strip())
    await state.set_state(AddMaster.phone)
    await msg.answer("📞 Телефон мастера (или - пропустить):")


@router.message(AddMaster.phone)
async def add_master_phone(msg: Message, state: FSMContext):
    data = await state.get_data()
    phone = "" if msg.text.strip() == "-" else msg.text.strip()
    await db.add_master(data["name"], phone)
    await state.clear()
    await msg.answer(
        f"✅ Мастер <b>{data['name']}</b> добавлен!\n\n"
        f"Теперь назначьте ему услуги через панель.",
        reply_markup=kb.admin_menu_kb(),
        parse_mode="HTML",
    )


# ── Services management ────────────────────────────────────
@router.callback_query(F.data == "a_services")
async def admin_services(cb: CallbackQuery):
    if not await require_admin(cb):
        return
    services = await db.get_services(active_only=False)
    await cb.message.edit_text(
        "💇 <b>Услуги:</b>",
        reply_markup=kb.admin_services_list_kb(services),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("as_"))
async def toggle_service(cb: CallbackQuery):
    if not await require_admin(cb):
        return
    service_id = int(cb.data.split("_")[1])
    await db.toggle_service(service_id)
    await cb.answer("✅ Статус изменён")
    await admin_services(cb)


@router.callback_query(F.data == "as_add")
async def add_service_start(cb: CallbackQuery, state: FSMContext):
    if not await require_admin(cb):
        return
    await state.set_state(AddService.name)
    await cb.message.edit_text("💇 Введите название услуги:")


@router.message(AddService.name)
async def add_service_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text.strip())
    await state.set_state(AddService.duration)
    await msg.answer("⏱ Длительность в минутах (60):")


@router.message(AddService.duration)
async def add_service_duration(msg: Message, state: FSMContext):
    dur = int(msg.text.strip()) if msg.text.strip().isdigit() else 60
    await state.update_data(duration=dur)
    await state.set_state(AddService.price)
    await msg.answer("💰 Цена в рублях:")


@router.message(AddService.price)
async def add_service_price(msg: Message, state: FSMContext):
    data = await state.get_data()
    price = int(msg.text.strip()) if msg.text.strip().isdigit() else 0
    await db.add_service(data["name"], data["duration"], price)
    await state.clear()
    await msg.answer(
        f"✅ Услуга <b>{data['name']}</b> добавлена!",
        reply_markup=kb.admin_menu_kb(),
        parse_mode="HTML",
    )


# ── Bookings ────────────────────────────────────────────────
@router.callback_query(F.data == "a_bookings")
async def admin_bookings(cb: CallbackQuery):
    if not await require_admin(cb):
        return
    today = date.today().isoformat()
    week_end = (date.today() + timedelta(days=7)).isoformat()
    bookings = await db.get_all_bookings_range(today, week_end)

    if not bookings:
        await cb.message.edit_text(
            "📅 На неделю записей нет.",
            reply_markup=kb.admin_menu_kb(),
        )
        return

    text = "📅 <b>Записи на неделю:</b>\n\n"
    current_date = ""
    for b in bookings:
        if b["booking_date"] != current_date:
            current_date = b["booking_date"]
            from handlers.client import _fmt_date
            text += f"\n<b>{_fmt_date(current_date)}</b>\n"
        text += f"  {b['time_slot']} — {b['master_name']} — {b['service_name']} ({b['client_name']})\n"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await cb.message.edit_text(
        text[:4000],
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="a_menu")]
        ]),
        parse_mode="HTML",
    )


# ── Master codes ────────────────────────────────────────────
@router.callback_query(F.data == "a_master_codes")
async def admin_master_codes(cb: CallbackQuery):
    if not await require_admin(cb):
        return
    masters = await db.get_masters(active_only=False)
    text = "🔑 <b>Коды доступа мастеров:</b>\n\n"
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    buttons = []
    for m in masters:
        code = await db.generate_master_code(m["id"])
        text += f"• {m['name']}: <code>{code}</code>\n"
        buttons.append([InlineKeyboardButton(text=f"🔑 {m['name']}", callback_data=f"am_code_{m['id']}")])

    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="a_menu")])

    await cb.message.edit_text(
        text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML"
    )


# ── Broadcast ───────────────────────────────────────────────
@router.callback_query(F.data == "a_broadcast")
async def broadcast_start(cb: CallbackQuery, state: FSMContext):
    if not await require_admin(cb):
        return
    await state.set_state(Broadcast.text)
    await cb.message.edit_text(
        "📤 Введите текст для рассылки всем клиентам:\n\n"
        "<i>Будет отправлено всем, кто хоть раз писал боту.</i>",
        parse_mode="HTML",
    )


@router.message(Broadcast.text)
async def broadcast_send(msg: Message, state: FSMContext):
    from aiogram import Bot
    from config import config

    text = msg.text.strip()
    db_conn = await db.get_db()
    try:
        rows = await db_conn.execute_fetchall(
            "SELECT DISTINCT tg_user_id FROM clients WHERE is_blocked=0 AND tg_user_id IS NOT NULL"
        )
        user_ids = [r["tg_user_id"] for r in rows]
    finally:
        await db_conn.close()

    bot = Bot(token=config.BOT_TOKEN)
    sent = 0
    failed = 0
    for uid in user_ids:
        try:
            await bot.send_message(uid, f"📢 <b>Рассылка</b>\n\n{text}", parse_mode="HTML")
            sent += 1
        except Exception:
            failed += 1
    await bot.session.close()

    await state.clear()
    await msg.answer(
        f"📤 Рассылка завершена:\n"
        f"✅ Доставлено: {sent}\n"
        f"❌ Ошибок: {failed}\n"
        f"👥 Всего получателей: {len(user_ids)}",
        reply_markup=kb.admin_menu_kb(),
    )
