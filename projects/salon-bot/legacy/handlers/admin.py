"""Admin panel — masters, services, bookings, stats."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import keyboards as kb
from utils import format_date
from config import SUPERADMIN_ID
from datetime import date, timedelta

router = Router()


class AddMaster(StatesGroup):
    name = State()
    phone = State()


class AddService(StatesGroup):
    name = State()
    duration = State()
    price = State()


class LinkMaster(StatesGroup):
    waiting_tg_id = State()


# ── Admin check ─────────────────────────────────────────
async def require_admin(cb: CallbackQuery) -> bool:
    if not await db.is_admin(cb.from_user.id):
        await cb.answer("⛔ Нет доступа")
        return False
    return True


# ── Menu ────────────────────────────────────────────────
@router.message(F.text == "/admin")
async def admin_panel(msg: Message):
    if not await db.is_admin(msg.from_user.id):
        await msg.answer("⛔ Нет доступа")
        return
    await msg.answer("🔧 <b>Панель администратора</b>", reply_markup=kb.admin_menu_kb(), parse_mode="HTML")


@router.callback_query(F.data == "a_menu")
async def admin_menu(cb: CallbackQuery):
    if not await require_admin(cb): return
    await cb.message.edit_text("🔧 <b>Панель администратора</b>", reply_markup=kb.admin_menu_kb(), parse_mode="HTML")


# ── Stats ───────────────────────────────────────────────
@router.callback_query(F.data == "a_stats")
async def admin_stats(cb: CallbackQuery):
    if not await require_admin(cb): return
    stats = await db.get_stats()
    await cb.message.edit_text(
        f"📊 <b>Статистика</b>

"
        f"📅 Сегодня записей: {stats['bookings_today']}
"
        f"📅 За месяц: {stats['bookings_month']}
"
        f"💰 Доход за месяц: {stats['revenue_month']}₽
"
        f"👥 Всего клиентов: {stats['clients_total']}",
        reply_markup=kb.admin_menu_kb(),
        parse_mode="HTML",
    )


# ── Masters management ──────────────────────────────────
@router.callback_query(F.data == "a_masters")
async def admin_masters(cb: CallbackQuery):
    if not await require_admin(cb): return
    masters = await db.get_masters(active_only=False)
    await cb.message.edit_text(
        "👩‍🎨 <b>Мастера:</b>",
        reply_markup=kb.admin_masters_list_kb(masters),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("am_"))
async def master_detail(cb: CallbackQuery):
    if not await require_admin(cb): return
    master_id = int(cb.data.split("_")[1])
    masters = await db.get_masters(active_only=False)
    master = next((m for m in masters if m["id"] == master_id), None)
    if not master:
        await cb.answer("Не найден")
        return

    services = await db.get_master_services(master_id)
    all_services = await db.get_services()
    svc_names = ", ".join(s["name"] for s in services) if services else "нет"
    status = "✅ Активен" if master["active"] else "❌ Неактивен"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await cb.message.edit_text(
        f"👩‍🎨 <b>{master['name']}</b>
"
        f"📞 {master['phone'] or 'не указан'}
"
        f"📊 {status}
"
        f"💇 Услуги: {svc_names}
",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="❌ Деактивировать" if master["active"] else "✅ Активировать",
                callback_data=f"am_toggle_{master_id}"
            )],
            [InlineKeyboardButton(text="🔗 Выдать код", callback_data=f"am_code_{master_id}")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="a_masters")],
        ]),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("am_toggle_"))
async def toggle_master(cb: CallbackQuery):
    if not await require_admin(cb): return
    master_id = int(cb.data.split("_")[2])
    import aiosqlite
    from database import DB_PATH
    conn = await aiosqlite.connect(DB_PATH)
    try:
        await conn.execute("UPDATE masters SET active=1-active WHERE id=?", (master_id,))
        await conn.commit()
    finally:
        await conn.close()
    await cb.answer("Готово")
    # Refresh
    cb.data = f"am_{master_id}"
    await master_detail(cb)


@router.callback_query(F.data.startswith("am_code_"))
async def master_code(cb: CallbackQuery):
    if not await require_admin(cb): return
    master_id = int(cb.data.split("_")[2])
    code = await db.generate_master_code(master_id)
    masters = await db.get_masters(active_only=False)
    master = next((m for m in masters if m["id"] == master_id), None)
    await cb.message.edit_text(
        f"🔑 Код для <b>{master['name'] if master else '?'}:</b>

"
        f"<code>{code}</code>

"
        f"Передайте мастеру. Он введёт /master и этот код.",
        reply_markup=kb.admin_menu_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "am_add")
async def add_master_start(cb: CallbackQuery, state: FSMContext):
    if not await require_admin(cb): return
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
    master_id = await db.add_master(data["name"], phone)
    await state.clear()
    await msg.answer(
        f"✅ Мастер <b>{data['name']}</b> добавлен!

"
        f"Теперь назначьте ему услуги через панель администратора.",
        reply_markup=kb.admin_menu_kb(),
        parse_mode="HTML",
    )


# ── Services management ─────────────────────────────────
@router.callback_query(F.data == "a_services")
async def admin_services(cb: CallbackQuery):
    if not await require_admin(cb): return
    services = await db.get_services(active_only=False)
    await cb.message.edit_text(
        "💇 <b>Услуги:</b>",
        reply_markup=kb.admin_services_list_kb(services),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("as_"))
async def toggle_service(cb: CallbackQuery):
    if not await require_admin(cb): return
    service_id = int(cb.data.split("_")[1])
    await db.toggle_service(service_id)
    await cb.answer("Статус изменён")
    services = await db.get_services(active_only=False)
    await cb.message.edit_text("💇 <b>Услуги:</b>", reply_markup=kb.admin_services_list_kb(services), parse_mode="HTML")


@router.callback_query(F.data == "as_add")
async def add_service_start(cb: CallbackQuery, state: FSMContext):
    if not await require_admin(cb): return
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


# ── All bookings ────────────────────────────────────────
@router.callback_query(F.data == "a_bookings")
async def admin_bookings(cb: CallbackQuery):
    if not await require_admin(cb): return
    today = date.today().isoformat()
    week_end = (date.today() + timedelta(days=7)).isoformat()
    bookings = await db.get_all_bookings_range(today, week_end)

    if not bookings:
        await cb.message.edit_text("📅 На неделю записей нет.", reply_markup=kb.admin_menu_kb())
        return

    text = "📅 <b>Записи на неделю:</b>

"
    current_date = ""
    for b in bookings:
        if b["booking_date"] != current_date:
            current_date = b["booking_date"]
            text += f"
<b>{format_date(current_date)}</b>
"
        text += f"  {b['time_slot']} — {b['master_name']} — {b['service_name']} ({b['client_name']})
"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await cb.message.edit_text(
        text[:4000],
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅ Назад", callback_data="a_menu")]
        ]),
        parse_mode="HTML",
    )


# ── Clients ─────────────────────────────────────────────
@router.callback_query(F.data == "a_clients")
async def admin_clients(cb: CallbackQuery):
    if not await require_admin(cb): return
    import aiosqlite
    from database import DB_PATH
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    try:
        rows = await conn.execute_fetchall("SELECT * FROM clients ORDER BY created_at DESC LIMIT 20")
        clients = [dict(r) for r in rows]
    finally:
        await conn.close()

    if not clients:
        await cb.message.edit_text("👥 Клиентов пока нет.", reply_markup=kb.admin_menu_kb())
        return

    text = "👥 <b>Клиенты:</b>

"
    for c in clients:
        text += f"• {c['name'] or 'Без имени'} — {c['phone'] or 'нет телефона'}
"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await cb.message.edit_text(
        text[:4000],
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅ Назад", callback_data="a_menu")]
        ]),
        parse_mode="HTML",
    )


# ── Master codes ────────────────────────────────────────
@router.callback_query(F.data == "a_master_codes")
async def admin_master_codes(cb: CallbackQuery):
    if not await require_admin(cb): return
    masters = await db.get_masters(active_only=False)
    text = "🔑 <b>Коды доступа мастеров:</b>

"
    for m in masters:
        code = await db.generate_master_code(m["id"])
        text += f"• {m['name']}: <code>{code}</code>
"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await cb.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅ Назад", callback_data="a_menu")]
        ]),
        parse_mode="HTML",
    )
