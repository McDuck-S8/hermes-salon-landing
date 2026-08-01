"""Client booking flow."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import keyboards as kb
from utils import format_date, format_booking, get_free_slots
from config import SALON_NAME, SALON_PHONE, SALON_ADDRESS

router = Router()


class BookingState(StatesGroup):
    choosing_service = State()
    choosing_master = State()
    choosing_date = State()
    choosing_time = State()
    confirming = State()


# ── Main menu ───────────────────────────────────────────
@router.callback_query(F.data == "main_menu")
async def main_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text(
        f"🏠 <b>{SALON_NAME}</b>

Выберите действие:",
        reply_markup=kb.main_menu_kb(),
        parse_mode="HTML",
    )


@router.message(F.text == "/start")
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    client = await db.get_or_create_client(msg.from_user.id, msg.from_user.full_name)
    await msg.answer(
        f"👋 Добро пожаловать в <b>{SALON_NAME}</b>!

"
        f"📍 {SALON_ADDRESS}
📞 {SALON_PHONE}

"
        "Выберите действие:",
        reply_markup=kb.main_menu_kb(),
        parse_mode="HTML",
    )


# ── Contacts ────────────────────────────────────────────
@router.callback_query(F.data == "contacts")
async def show_contacts(cb: CallbackQuery):
    await cb.message.edit_text(
        f"📞 <b>Контакты</b>

"
        f"📍 {SALON_ADDRESS}
"
        f"📞 {SALON_PHONE}

"
        "Для записи нажмите «Записаться»",
        reply_markup=kb.back_to_menu_kb(),
        parse_mode="HTML",
    )


# ── Step 1: Choose service ──────────────────────────────
@router.callback_query(F.data == "book_start")
async def book_start(cb: CallbackQuery, state: FSMContext):
    services = await db.get_services()
    if not services:
        await cb.message.edit_text("😔 Нет доступных услуг.", reply_markup=kb.back_to_menu_kb())
        return
    await state.set_state(BookingState.choosing_service)
    await cb.message.edit_text("💇 <b>Выберите услугу:</b>", reply_markup=kb.services_kb(services), parse_mode="HTML")


# ── Step 2: Choose master ───────────────────────────────
@router.callback_query(F.data.startswith("svc_"), BookingState.choosing_service)
async def choose_service(cb: CallbackQuery, state: FSMContext):
    service_id = int(cb.data.split("_")[1])
    service = next((s for s in await db.get_services() if s["id"] == service_id), None)
    if not service:
        await cb.answer("Услуга не найдена")
        return

    await state.update_data(service_id=service_id, service_name=service["name"], service_duration=service["duration_min"], service_price=service["price"])

    # Get masters who can do this service
    all_masters = await db.get_masters()
    masters = []
    for m in all_masters:
        specs = await db.get_master_services(m["id"])
        if any(s["id"] == service_id for s in specs):
            masters.append(m)

    if not masters:
        await cb.message.edit_text(
            "😔 Нет свободных мастеров для этой услуги.",
            reply_markup=kb.back_to_menu_kb(),
        )
        return

    await state.set_state(BookingState.choosing_master)
    await cb.message.edit_text(
        f"💇 <b>{service['name']}</b> — {service['price']}₽

👩‍🎨 Выберите мастера:",
        reply_markup=kb.masters_kb(masters),
        parse_mode="HTML",
    )


# ── Step 3: Choose date ─────────────────────────────────
@router.callback_query(F.data.startswith("mst_"), BookingState.choosing_master)
async def choose_master(cb: CallbackQuery, state: FSMContext):
    master_id = int(cb.data.split("_")[1])
    masters = await db.get_masters()
    master = next((m for m in masters if m["id"] == master_id), None)
    if not master:
        await cb.answer("Мастер не найден")
        return

    rating, count = await db.get_master_rating(master_id)
    rating_text = f"⭐ {rating} ({count} отзывов)" if count > 0 else "Нет отзывов"

    await state.update_data(master_id=master_id, master_name=master["name"])
    await state.set_state(BookingState.choosing_date)
    await cb.message.edit_text(
        f"👩‍🎨 <b>{master['name']}</b> — {rating_text}

📅 Выберите дату:",
        reply_markup=kb.dates_kb(),
        parse_mode="HTML",
    )


# ── Step 4: Choose time ─────────────────────────────────
@router.callback_query(F.data.startswith("date_"), BookingState.choosing_date)
async def choose_date(cb: CallbackQuery, state: FSMContext):
    date_iso = cb.data.split("_", 1)[1]
    data = await state.get_data()
    master_id = data["master_id"]
    duration = data.get("service_duration", 60)

    booked = await db.get_booked_slots(master_id, date_iso)
    free = get_free_slots(booked, duration)

    if not free:
        await cb.message.edit_text(
            f"😔 На {format_date(date_iso)} нет свободных слотов.
Выберите другую дату:",
            reply_markup=kb.dates_kb(),
        )
        return

    await state.update_data(chosen_date=date_iso)
    await state.set_state(BookingState.choosing_time)
    await cb.message.edit_text(
        f"📅 <b>{format_date(date_iso)}</b>

⏰ Выберите время:",
        reply_markup=kb.times_kb(free, date_iso),
        parse_mode="HTML",
    )


# ── Step 5: Confirm ─────────────────────────────────────
@router.callback_query(F.data.startswith("time_"), BookingState.choosing_time)
async def choose_time(cb: CallbackQuery, state: FSMContext):
    parts = cb.data.split("_")  # time_2026-05-28_10:00
    date_iso = parts[1]
    time_slot = parts[2]

    data = await state.get_data()
    await state.update_data(chosen_time=time_slot)

    params = f"{data['master_id']}_{data['service_id']}_{date_iso}_{time_slot}"
    await cb.message.edit_text(
        f"📋 <b>Подтвердите запись:</b>

"
        f"💇 {data['service_name']} — {data['service_price']}₽
"
        f"👩‍🎨 {data['master_name']}
"
        f"📅 {format_date(date_iso)}
"
        f"⏰ {time_slot}
",
        reply_markup=kb.confirm_kb(params),
        parse_mode="HTML",
    )


# ── Final: Create booking ───────────────────────────────
@router.callback_query(F.data.startswith("confirm_"))
async def confirm_booking(cb: CallbackQuery, state: FSMContext):
    parts = cb.data.split("_")  # confirm_masterId_serviceId_date_time
    master_id = int(parts[1])
    service_id = int(parts[2])
    date_iso = parts[3]
    time_slot = parts[4]

    client = await db.get_or_create_client(cb.from_user.id, cb.from_user.full_name)
    booking_id = await db.create_booking(client["id"], master_id, service_id, date_iso, time_slot)

    if not booking_id:
        await cb.message.edit_text(
            "❌ Этот слот уже занят. Выберите другое время.",
            reply_markup=kb.back_to_menu_kb(),
        )
        await state.clear()
        return

    data = await state.get_data()
    await state.clear()

    await cb.message.edit_text(
        f"✅ <b>Запись подтверждена!</b>

"
        f"💇 {data.get('service_name', '?')}
"
        f"👩‍🎨 {data.get('master_name', '?')}
"
        f"📅 {format_date(date_iso)} в {time_slot}

"
        f"Ждём вас! 💖",
        reply_markup=kb.booking_actions_kb(booking_id),
        parse_mode="HTML",
    )


# ── Cancel flow ─────────────────────────────────────────
@router.callback_query(F.data == "cancel_flow")
async def cancel_flow(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("❌ Запись отменена.", reply_markup=kb.main_menu_kb())


# ── My bookings ─────────────────────────────────────────
@router.callback_query(F.data == "my_bookings")
async def my_bookings(cb: CallbackQuery):
    client = await db.get_or_create_client(cb.from_user.id, cb.from_user.full_name)
    bookings = await db.get_client_bookings(client["id"])

    if not bookings:
        await cb.message.edit_text("📋 У вас пока нет записей.", reply_markup=kb.main_menu_kb())
        return

    text = "📋 <b>Ваши записи:</b>

"
    for b in bookings[:10]:
        status_icon = "✅" if b["status"] == "confirmed" else "❌"
        text += (
            f"{status_icon} {format_date(b['booking_date'])} в {b['time_slot']} — "
            f"{b['service_name']} ({b['master_name']})
"
        )

    # Action buttons for most recent confirmed booking
    rows = []
    confirmed = [b for b in bookings if b["status"] == "confirmed"]
    if confirmed:
        b = confirmed[0]
        rows.append([InlineKeyboardButton(text="❌ Отменить последнюю", callback_data=f"del_{b['id']}")])
    rows.append([InlineKeyboardButton(text="🏠 Меню", callback_data="main_menu")])

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")


# ── Cancel booking ──────────────────────────────────────
@router.callback_query(F.data.startswith("del_"))
async def delete_booking(cb: CallbackQuery):
    booking_id = int(cb.data.split("_")[1])
    booking = await db.get_booking(booking_id)
    if not booking:
        await cb.answer("Запись не найдена")
        return
    if booking["client_tg"] != cb.from_user.id:
        await cb.answer("Это не ваша запись")
        return

    await db.cancel_booking(booking_id)
    await cb.message.edit_text(
        f"❌ Запись отменена:
"
        f"{format_date(booking['booking_date'])} в {booking['time_slot']}
"
        f"{booking['service_name']} — {booking['master_name']}",
        reply_markup=kb.main_menu_kb(),
    )


# ── Review ──────────────────────────────────────────────
@router.callback_query(F.data.startswith("review_"))
async def leave_review(cb: CallbackQuery):
    booking_id = int(cb.data.split("_")[1])
    booking = await db.get_booking(booking_id)
    if not booking:
        await cb.answer("Запись не найдена")
        return

    await cb.message.edit_text(
        f"⭐ Оцените визит:
"
        f"{booking['service_name']} — {booking['master_name']}
"
        f"{format_date(booking['booking_date'])}",
        reply_markup=kb.rating_kb(booking_id),
    )


@router.callback_query(F.data.startswith("rate_"))
async def process_rating(cb: CallbackQuery, state: FSMContext):
    parts = cb.data.split("_")  # rate_bookingId_rating
    booking_id = int(parts[1])
    rating = int(parts[2])

    booking = await db.get_booking(booking_id)
    if not booking:
        await cb.answer("Запись не найдена")
        return

    client = await db.get_or_create_client(cb.from_user.id, cb.from_user.full_name)
    await db.add_review(booking_id, client["id"], booking["master_id"], rating)

    stars = "⭐" * rating
    await cb.message.edit_text(
        f"Спасибо за отзыв! {stars}",
        reply_markup=kb.main_menu_kb(),
    )
