"""
Salon Bot — Mini App WebHandler
Backend Architect: processes data from Telegram WebApp.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import json

import bot.db as db
import bot.keyboards as kb
from config import config

router = Router()


@router.message(F.web_app_data)
async def webapp_data(msg: Message):
    """Receive booking data from Mini App form."""
    try:
        data = json.loads(msg.web_app_data.data)
    except (json.JSONDecodeError, TypeError):
        await msg.answer("❌ Ошибка обработки данных.")
        return

    # Expected: {service_id, master_id, date, time}
    service_id = data.get("service_id")
    master_id = data.get("master_id")
    date_iso = data.get("date")
    time_slot = data.get("time")

    if not all([service_id, master_id, date_iso, time_slot]):
        await msg.answer("❌ Неполные данные для бронирования.")
        return

    service = await db.get_service(service_id)
    master = await db.get_master(master_id)
    if not service or not master:
        await msg.answer("❌ Услуга или мастер не найдены.")
        return

    client = await db.get_or_create_client(msg.from_user.id, msg.from_user.full_name)
    booking_id = await db.create_booking(
        client["id"], master_id, service_id, date_iso, time_slot,
        service.get("duration_min", 60), service.get("price", 0),
    )

    if not booking_id:
        await msg.answer(
            "❌ Это время уже занято. Пожалуйста, выберите другое.",
            reply_markup=kb.back_to_menu_kb(),
        )
        return

    await msg.answer(
        f"✅ <b>Запись подтверждена!</b>\n\n"
        f"{service.get('emoji', '💇')} {service['name']} — {service['price']}₽\n"
        f"👩‍🎨 {master['name']}\n"
        f"📅 {date_iso} в {time_slot}\n\n"
        f"Ждём вас! 💖",
        reply_markup=kb.booking_actions_kb(booking_id),
        parse_mode="HTML",
    )


@router.message(F.text == "/webapp")
async def webapp_link(msg: Message):
    """Send the Mini App link."""
    if not config.WEBAPP_URL:
        await msg.answer(
            "🌐 Mini App не настроен.\n"
            "Администратор может установить WEBAPP_URL в переменных окружения."
        )
        return

    await msg.answer(
        "✨ <b>Mini App запись</b>\n\n"
        "Нажмите кнопку ниже для удобной записи через веб-интерфейс:",
        reply_markup=kb.mini_app_kb(),
        parse_mode="HTML",
    )
