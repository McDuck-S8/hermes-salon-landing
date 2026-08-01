"""Utility helpers — calendar, time formatting."""
from datetime import date, timedelta, datetime
from config import WORK_START_HOUR, WORK_END_HOUR, SLOT_DURATION, BOOKING_DAYS_AHEAD


def get_available_dates() -> list[tuple[str, str]]:
    """Return list of (iso_date, display_label) for next N days."""
    today = date.today()
    result = []
    for i in range(BOOKING_DAYS_AHEAD):
        d = today + timedelta(days=i)
        weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        label = f"{d.day:02d}.{d.month:02d} {weekdays[d.weekday()]}"
        result.append((d.isoformat(), label))
    return result


def generate_time_slots(service_duration: int = None) -> list[str]:
    """Generate all possible time slots for a day."""
    dur = service_duration or SLOT_DURATION
    slots = []
    h, m = WORK_START_HOUR, 0
    while h < WORK_END_HOUR:
        slots.append(f"{h:02d}:{m:02d}")
        m += dur
        if m >= 60:
            h += m // 60
            m = m % 60
    return slots


def get_free_slots(booked: list[str], service_duration: int = None) -> list[str]:
    """Filter out already booked slots."""
    all_slots = generate_time_slots(service_duration)
    return [s for s in all_slots if s not in booked]


def format_date(iso_date: str) -> str:
    """2026-05-28 → 28.05 (Ср)"""
    d = date.fromisoformat(iso_date)
    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    return f"{d.day:02d}.{d.month:02d} ({weekdays[d.weekday()]})"


def format_booking(b: dict) -> str:
    """Format booking dict into readable string."""
    return (
        f"📅 {format_date(b['booking_date'])} в {b['time_slot']}
"
        f"💇 {b.get('service_name', '?')}
"
        f"👩‍🎨 {b.get('master_name', '?')}
"
        f"📊 Статус: {b.get('status', '?')}"
    )
