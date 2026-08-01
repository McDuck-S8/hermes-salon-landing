# Salon Bot Patterns — Reusable for Any Booking/Service Bot

## Silent Reminders with Inline Confirm

Send booking reminders that don't make sound (`disable_notification=True`) with confirm/reschedule buttons:

```python
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да, буду!", callback_data=f"remind_ok_{booking_id}")],
    [InlineKeyboardButton(text="❌ Нужно перенести", callback_data=f"remind_reschedule_{booking_id}")],
])

await bot.send_message(
    chat_id, text,
    parse_mode="HTML",
    reply_markup=kb,
    disable_notification=True,  # Silent — no sound/vibration
)
```

**Handler pattern:**
```python
@router.callback_query(F.data.startswith("remind_ok_"))
async def remind_confirm(cb: CallbackQuery):
    try:
        await cb.message.edit_text("✅ Ждём вас завтра! 💖", parse_mode="HTML")
    except Exception:
        await cb.answer("✅ Подтверждено!")
    await cb.answer("✅ Подтверждено!")

@router.callback_query(F.data.startswith("remind_reschedule_"))
async def remind_reschedule(cb: CallbackQuery):
    booking_id = int(cb.data.split("_")[-1])
    try:
        await cb.message.edit_text(
            "📅 Хорошо, перенесём!",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📅 Новое время", callback_data="book_start", style="primary")],
                [InlineKeyboardButton(text="❌ Отменить", callback_data=f"del_{booking_id}", style="danger")],
            ]),
        )
    except Exception:
        await cb.answer("📅 Перейдите в меню")
```

## Colored Button Guidelines

| Action Type | Style | Example |
|------------|-------|---------|
| Confirm/Approve | `success` | "Подтвердить запись" |
| Cancel/Delete | `danger` | "Отменить запись" |
| Primary CTA | `primary` | "Записаться", "Поделиться" |
| Neutral/Navigation | none | "Главное меню", "Назад" |

## Quiz Handler Safety

Always guard quiz handlers against prefix collisions:
```python
@router.callback_query(F.data.startswith("quiz_"))
async def quiz_answer(cb: CallbackQuery, state: FSMContext):
    if cb.data in ("quiz_next", "quiz"):  # Skip non-answer callbacks
        return
    parts = cb.data.split("_")
    if len(parts) < 3 or not parts[1].isdigit():
        return
    # ... process answer
```
