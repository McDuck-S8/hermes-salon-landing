"""
Salon Bot — Reminders (Cron)
Backend Architect: sends booking reminders 24h before appointment.
Run: python -m cron.reminders
"""

import asyncio
import logging
import sys
from datetime import datetime, date, timedelta
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config
import bot.db as db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("salon-reminder")


async def send_reminders():
    """Find bookings for tomorrow and send silent reminders with confirm button."""
    from aiogram import Bot
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    logger.info(f"🔍 Проверяю записи на {tomorrow}...")

    db_conn = await db.get_db()
    try:
        rows = await db_conn.execute_fetchall(
            """SELECT b.*, c.tg_user_id, c.name as client_name,
                      m.name as master_name, s.name as service_name, s.emoji
               FROM bookings b
               JOIN clients c ON b.client_id = c.id
               JOIN masters m ON b.master_id = m.id
               JOIN services s ON b.service_id = s.id
               WHERE b.booking_date=? AND b.status='confirmed' AND b.reminder_sent=0""",
            (tomorrow,),
        )
    finally:
        await db_conn.close()

    if not rows:
        logger.info("😴 Нет записей для напоминания")
        return

    bot = Bot(token=config.BOT_TOKEN)
    sent = 0
    for r in rows:
        b = dict(r)
        try:
            emoji = b.get("emoji", "💇")
            text = (
                f"⏰ <b>Напоминание!</b>\n\n"
                f"Завтра, <b>{b['booking_date']}</b> в <b>{b['time_slot']}</b>\n"
                f"{emoji} {b['service_name']}\n"
                f"👩‍🎨 {b['master_name']}\n\n"
                f"Ждём вас! 💖"
            )
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Да, буду!", callback_data=f"remind_ok_{b['id']}")],
                [InlineKeyboardButton(text="❌ Нужно перенести", callback_data=f"remind_reschedule_{b['id']}")],
            ])
            # Silent notification — no sound, no vibration
            await bot.send_message(
                b["tg_user_id"], text,
                parse_mode="HTML",
                reply_markup=kb,
                disable_notification=True,
            )

            # Mark reminder as sent
            db_conn2 = await db.get_db()
            try:
                await db_conn2.execute(
                    "UPDATE bookings SET reminder_sent=1 WHERE id=?",
                    (b["id"],),
                )
                await db_conn2.commit()
            finally:
                await db_conn2.close()

            await db.log_notification(b["id"], "reminder", "sent")
            sent += 1
            logger.info(f"✅ Напоминание отправлено: {b['client_name']} — {b['time_slot']}")

        except Exception as e:
            logger.error(f"❌ Ошибка отправки {b.get('client_name')}: {e}")
            try:
                await db.log_notification(b["id"], "reminder", "failed")
            except:
                pass

    await bot.session.close()
    logger.info(f"📨 Отправлено напоминаний: {sent}")


async def cleanup_old_bookings():
    """Mark past bookings with status 'confirmed' as 'completed'."""
    db_conn = await db.get_db()
    try:
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        await db_conn.execute(
            "UPDATE bookings SET status='completed', updated_at=datetime('now') WHERE booking_date<? AND status='confirmed'",
            (yesterday,),
        )
        await db_conn.commit()
        affected = db_conn.total_changes
        if affected:
            logger.info(f"✅ Завершено старых записей: {affected}")
    finally:
        await db_conn.close()


async def send_aftercare():
    """Send aftercare tips based on completed bookings."""
    from aiogram import Bot
    from bot.lumina import get_aftercare

    db_conn = await db.get_db()
    try:
        today = date.today().isoformat()
        # Find completed bookings where 1, 3, 7, or 14 days have passed
        rows = await db_conn.execute_fetchall(
            """SELECT b.*, c.tg_user_id, c.name as client_name,
                      s.name as service_name, s.category
               FROM bookings b
               JOIN clients c ON b.client_id = c.id
               JOIN services s ON b.service_id = s.id
               WHERE b.status='completed' AND b.booking_date <= ?""",
            (today,),
        )
    finally:
        await db_conn.close()

    if not rows:
        logger.info("😴 Нет записей для aftercare")
        return

    bot = Bot(token=config.BOT_TOKEN)
    sent = 0
    for r in rows:
        b = dict(r)
        try:
            booking_dt = date.fromisoformat(b["booking_date"])
            days_since = (date.today() - booking_dt).days
            category = b.get("category", "")
            aftercare = get_aftercare(category, days_since)
            if aftercare:
                await bot.send_message(
                    b["tg_user_id"], aftercare,
                    parse_mode="HTML",
                    disable_notification=True,
                )
                sent += 1
                logger.info(f"💌 Aftercare отправлено: {b['client_name']} — день {days_since}")
        except Exception as e:
            logger.error(f"❌ Aftercare ошибка {b.get('client_name')}: {e}")

    await bot.session.close()
    logger.info(f"💌 Отправлено aftercare: {sent}")


async def main():
    logger.info("🚀 Запуск напоминаний...")
    await db.seed_demo()  # ensure DB schema exists
    await cleanup_old_bookings()
    await send_reminders()
    await send_aftercare()
    logger.info("✅ Готово")


if __name__ == "__main__":
    asyncio.run(main())
