"""
Salon Bot — Fun Features (Telegram API 10.x)
Dice games, stories, reactions, photo gallery, polls
"""

import random
from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton,
    InputMediaPhoto, InputPollOption, PollOption,
)
from aiogram.enums import DiceEmoji, MessageEntityType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import bot.db as db
import bot.keyboards as kb
from config import config

router = Router()


# ══════════════════════════════════════════════════════════
# DICE GAME — "Брось кубик и получи скидку"
# ══════════════════════════════════════════════════════════

DISCOUNT_TABLE = {
    1: ("😐", "1% скидка", "Ну, это начало пути!"),
    2: ("🙂", "2% скидка", "Неплохо для начала!"),
    3: ("😊", "3% скидка", "Уже теплее!"),
    4: ("😄", "5% скидка", "Отлично! Запомни этот день!"),
    5: ("🤩", "7% скидка", "Ты везунчик! Почти идеально!"),
    6: ("🎉", "10% скидка", "ДЖЕКПОТ! Максимальная скидка!"),
}


@router.callback_query(F.data == "dice_game")
async def dice_game(cb: CallbackQuery, state: FSMContext):
    """Interactive dice game for discounts"""
    await state.set_state("dice_throwing")
    text = (
        "🎲 <b>ИГРА «БРОСЬ КУБИК»</b>\n\n"
        "Брось кубик и получи скидку на любую услугу!\n\n"
        "1️⃣ = 1%  ·  2️⃣ = 2%  ·  3️⃣ = 3%\n"
        "4️⃣ = 5%  ·  5️⃣ = 7%  ·  6️⃣ = 10% 🔥\n\n"
        "Нажми кнопку и жди результат!"
    )
    kb_dice = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Бросить кубик!", callback_data="throw_dice")],
        [InlineKeyboardButton(text="🏠 Меню", callback_data="main_menu")],
    ])
    await cb.message.edit_text(text, reply_markup=kb_dice, parse_mode="HTML")


@router.callback_query(F.data == "throw_dice")
async def throw_dice(cb: CallbackQuery, state: FSMContext, bot: Bot):
    """Send dice animation and process result"""
    from datetime import datetime, timedelta
    # Check if user already played today (simple cooldown)
    data = await state.get_data()
    last_dice = data.get("last_dice_time")
    if last_dice:
        try:
            last_dt = datetime.fromisoformat(last_dice)
            if datetime.now() - last_dt < timedelta(hours=12):
                await cb.answer("⏰ Кубик можно бросить раз в 12 часов!", show_alert=True)
                return
        except (ValueError, TypeError):
            pass

    # Send dice animation
    dice_msg = await bot.send_dice(
        chat_id=cb.message.chat.id,
        emoji=DiceEmoji.DICE,
    )
    value = dice_msg.dice.value

    await state.update_data(
        last_dice_time=datetime.now().isoformat(),
        dice_discount=value,
    )

    icon, discount, comment = DISCOUNT_TABLE[value]

    # React with emoji
    try:
        await bot.set_message_reaction(
            chat_id=cb.message.chat.id,
            message_id=cb.message.message_id,
            reaction=[{"type": "emoji", "emoji": icon}],
        )
    except Exception:
        pass

    result_text = (
        f"{icon} <b>Выпало: {value}!</b>\n\n"
        f"🎉 Твоя скидка: <b>{discount}</b>\n"
        f"<i>{comment}</i>\n\n"
        f"Скидка действует 7 дней. Покажи этот чек-ин при визите!"
    )
    kb_result = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Записаться со скидкой", callback_data="book_start")],
        [InlineKeyboardButton(text="🎲 Бросить ещё раз", callback_data="throw_dice")],
        [InlineKeyboardButton(text="🏠 Меню", callback_data="main_menu")],
    ])
    await cb.message.answer(result_text, reply_markup=kb_result, parse_mode="HTML")
    await cb.answer()


# ══════════════════════════════════════════════════════════
# PHOTO GALLERY — "Наши работы"
# ══════════════════════════════════════════════════════════

@router.callback_query(F.data == "gallery")
async def gallery_menu(cb: CallbackQuery):
    """Show gallery categories"""
    text = (
        "📸 <b>ГАЛЕРЕЯ РАБОТ</b>\n\n"
        "Выберите категорию:"
    )
    kb_gallery = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💇 Стрижки", callback_data="gallery_hair")],
        [InlineKeyboardButton(text="🎨 Окрашивание", callback_data="gallery_color")],
        [InlineKeyboardButton(text="💅 Маникюр", callback_data="gallery_nails")],
        [InlineKeyboardButton(text="🧖 Уходы", callback_data="gallery_care")],
        [InlineKeyboardButton(text="🏠 Меню", callback_data="main_menu")],
    ])
    await cb.message.edit_text(text, reply_markup=kb_gallery, parse_mode="HTML")


# Gallery photo data — demo URLs (replace with real salon photos)
GALLERY_PHOTOS = {
    "hair": [
        ("https://images.unsplash.com/photo-1562322140-8baeececf3df?w=600", "💇‍♀️ Стрижка каре"),
        ("https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600", "✂️ Каскад"),
        ("https://images.unsplash.com/photo-1605497788044-5a32c7078486?w=600", "💇 Пикси"),
    ],
    "color": [
        ("https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=600", "🎨 Мелирование"),
        ("https://images.unsplash.com/photo-1600948836101-f9ffda59d250?w=600", "🌈 Омбре"),
        ("https://images.unsplash.com/photo-1542599260-04951f4b2e85?w=600", "🎀 Балаяж"),
    ],
    "nails": [
        ("https://images.unsplash.com/photo-1604654894610-df63bc536371?w=600", "💅 Маникюр гель"),
        ("https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=600", "🎨 Дизайн ногтей"),
        ("https://images.unsplash.com/photo-1607779097040-26e80aa78e66?w=600", "✨ Педикюр"),
    ],
    "care": [
        ("https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=600", "🧖 Уход за лицом"),
        ("https://images.unsplash.com/photo-1540555700478-4be289fbec6d?w=600", "💆 Массаж головы"),
        ("https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?w=600", "🌿 Спа-уход"),
    ],
}


@router.callback_query(F.data.startswith("gallery_") & ~F.data.startswith("gallery_next_"))
async def gallery_category(cb: CallbackQuery):
    """Show photos for a gallery category."""
    category = cb.data.replace("gallery_", "")
    photos = GALLERY_PHOTOS.get(category)

    if not photos:
        await cb.answer("Фото скоро появятся! 📸")
        return

    # Send first photo with caption
    first_url, first_caption = photos[0]
    kb_back = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Следующее фото", callback_data=f"gallery_next_{category}_1")],
        [InlineKeyboardButton(text="📸 Галерея", callback_data="gallery")],
        [InlineKeyboardButton(text="🏠 Меню", callback_data="main_menu")],
    ])

    # Delete previous message (may be text or photo)
    try:
        await cb.message.delete()
    except Exception:
        pass

    try:
        await cb.message.answer_photo(
            photo=first_url,
            caption=f"📸 <b>ГАЛЕРЕЯ</b> — {first_caption}\n\n{1}/{len(photos)}",
            reply_markup=kb_back,
            parse_mode="HTML",
        )
    except Exception:
        # Fallback to text if photo fails
        await cb.message.answer(
            f"📸 <b>ГАЛЕРЕЯ</b> — {first_caption}\n\n{1}/{len(photos)}\n\n🔗 {first_url}",
            reply_markup=kb_back,
            parse_mode="HTML",
        )
    await cb.answer()


@router.callback_query(F.data.startswith("gallery_next_"))
async def gallery_next_photo(cb: CallbackQuery):
    """Navigate to next photo in category."""
    parts = cb.data.split("_")  # gallery_next_category_idx
    category = parts[2]
    idx = int(parts[3])
    photos = GALLERY_PHOTOS.get(category, [])

    if idx >= len(photos):
        # Back to category menu
        await cb.answer("Это все фото! 📸")
        return

    photo_url, caption = photos[idx]
    buttons = []
    if idx > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"gallery_next_{category}_{idx - 1}"))
    if idx < len(photos) - 1:
        buttons.append(InlineKeyboardButton(text="Далее ➡️", callback_data=f"gallery_next_{category}_{idx + 1}"))

    kb = InlineKeyboardMarkup(inline_keyboard=[
        buttons,
        [InlineKeyboardButton(text="📸 Галерея", callback_data="gallery")],
        [InlineKeyboardButton(text="🏠 Меню", callback_data="main_menu")],
    ])

    try:
        await cb.message.delete()
    except Exception:
        pass

    try:
        await cb.message.answer_photo(
            photo=photo_url,
            caption=f"📸 <b>ГАЛЕРЕЯ</b> — {caption}\n\n{idx + 1}/{len(photos)}",
            reply_markup=kb,
            parse_mode="HTML",
        )
    except Exception:
        await cb.message.answer(
            f"📸 <b>ГАЛЕРЕЯ</b> — {caption}\n\n{idx + 1}/{len(photos)}\n\n🔗 {photo_url}",
            reply_markup=kb,
            parse_mode="HTML",
        )
    await cb.answer()


# ══════════════════════════════════════════════════════════
# DAILY SPECIAL — "Спецпредложение дня"
# ══════════════════════════════════════════════════════════

SPECIALS = [
    ("🔥", "Горячее предложение", "Стрижка + уход = 2500₽ вместо 3200₽"),
    ("💎", "VIP день", "Все окрашивания -20% сегодня!"),
    ("🌸", "Новинка месяца", "Пилинг кожи головы в подарок к стрижке"),
    ("✨", "Счастливый час", "14:00-16:00 — маникюр за 990₽"),
    ("🎁", "Приведи друга", "Вам обоим скидка 15% на любой сервис"),
]


@router.callback_query(F.data == "daily_special")
async def daily_special(cb: CallbackQuery):
    """Show daily special offer"""
    # Pick based on day of year for consistency within a day
    from datetime import date
    day = date.today().toordinal()
    special = SPECIALS[day % len(SPECIALS)]
    emoji, title, description = special

    text = (
        f"{emoji} <b>СПЕЦПРЕДЛОЖЕНИЕ ДНЯ</b>\n\n"
        f"<b>{title}</b>\n\n"
        f"{description}\n\n"
        f"⏰ Действует только сегодня!\n"
        f"📞 Звоните: {config.SALON_PHONE}"
    )
    kb_special = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Записаться", callback_data="book_start")],
        [InlineKeyboardButton(text="🔄 Другое предложение", callback_data="daily_special")],
        [InlineKeyboardButton(text="🏠 Меню", callback_data="main_menu")],
    ])
    rich_sent = False
    try:
        from bot.rich import daily_special_card, available
        if available:
            rich = daily_special_card(
                title="СПЕЦПРЕДЛОЖЕНИЕ ДНЯ",
                description=f"{title}\n\n{description}\n\n📞 {config.SALON_PHONE}",
                promo=f"{emoji} {title}",
            )
            if rich:
                await cb.message.delete()
                await cb.message.answer(rich_message=rich, reply_markup=kb_special)
                rich_sent = True
    except Exception:
        pass
    if not rich_sent:
        try:
            await cb.message.edit_text(text, reply_markup=kb_special, parse_mode="HTML")
        except Exception:
            await cb.answer("Уже показано ✨")


# ══════════════════════════════════════════════════════════
# LOYALTY CARD — "Виртуальная карта"
# ══════════════════════════════════════════════════════════

@router.callback_query(F.data == "loyalty")
async def loyalty_card(cb: CallbackQuery):
    """Virtual loyalty card"""
    client = await db.get_or_create_client(cb.from_user.id, cb.from_user.full_name)
    bookings = await db.get_client_bookings(client["id"])
    completed = [b for b in bookings if b["status"] in ("completed", "confirmed")]
    count = len(completed)

    # Progress to next level
    levels = [
        (0, "🌱 Новичок", "Скидка 3%", 5),
        (5, "🌿 Постоялец", "Скидка 5%", 15),
        (15, "🌳 VIP", "Скидка 10%", 30),
        (30, "👑 Легенда", "Скидка 15%", 999),
    ]

    current_level = levels[0]
    next_level = levels[1]
    for i, (threshold, name, discount, next_thresh) in enumerate(levels):
        if count >= threshold:
            current_level = (threshold, name, discount, next_thresh)
            if i + 1 < len(levels):
                next_level = levels[i + 1]
            else:
                next_level = None

    # Visual progress bar
    if next_level:
        cur, _, _, target = next_level
        progress = min(count / target, 1.0)
        bar_len = 10
        filled = int(progress * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        progress_text = f"\n\nПрогресс до «{next_level[1]}»: {bar} ({count}/{target})"
    else:
        progress_text = "\n\n🏆 Ты уже на максимуме!"

    _, level_name, level_discount, _ = current_level

    text = (
        f"💳 <b>ВИРТУАЛЬНАЯ КАРТА</b>\n\n"
        f"Уровень: <b>{level_name}</b>\n"
        f"Скидка: <b>{level_discount}</b>\n"
        f"Визитов: <b>{count}</b>"
        f"{progress_text}\n\n"
        f"Каждый 5-й визит —.extra скидка!"
    )
    kb_loyalty = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Записаться", callback_data="book_start")],
        [InlineKeyboardButton(text="🏠 Меню", callback_data="main_menu")],
    ])
    await cb.message.edit_text(text, reply_markup=kb_loyalty, parse_mode="HTML")


# ══════════════════════════════════════════════════════════
# QUIZ — "Тест о волосах" (fun engagement)
# ══════════════════════════════════════════════════════════

QUIZ_QUESTIONS = [
    {
        "q": "🧪 Как часто нужно стричься?",
        "options": ["Каждый месяц", "Каждые 2-3 месяца", "Когда расщепляются", "Раз в год"],
        "correct": 1,
        "fact": "Правильный ответ: каждые 2-3 месяца! Это поддерживает форму и здоровье 💇",
    },
    {
        "q": "💧 Как часто мыть голову?",
        "options": ["Каждый день", "Через день", "2-3 раза в неделю", "Раз в неделю"],
        "correct": 2,
        "fact": "2-3 раза в неделю — оптимально для большинства типов волос! 🧴",
    },
    {
        "q": "🎨 Окрашивание без аммиака — это...",
        "options": ["Миф", "Безопаснее обычного", "Не держится", "Дороже в 10 раз"],
        "correct": 1,
        "fact": "Тонирование без аммиака действительно мягче для волос! 🌿",
    },
]


@router.callback_query(F.data == "quiz")
async def quiz_start(cb: CallbackQuery, state: FSMContext):
    """Start fun quiz about hair care"""
    await state.set_state("quiz_q")
    await state.update_data(q_idx=0, score=0)
    await _show_quiz_question(cb, state)


async def _show_quiz_question(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    idx = data.get("q_idx", 0)
    if idx >= len(QUIZ_QUESTIONS):
        score = data.get("score", 0)
        total = len(QUIZ_QUESTIONS)
        if score == total:
            result = "🏆 Идеально! Ты знаток волос!"
        elif score >= total // 2:
            result = "👍 Неплохо! Есть над чем поработать!"
        else:
            result = "📚 Читай наш блог — мы делимся секретами!"

        text = (
            f"🧠 <b>РЕЗУЛЬТАТЫ ТЕСТА</b>\n\n"
            f"Правильных ответов: <b>{score}/{total}</b>\n\n"
            f"{result}\n\n"
            f"Запишись к нам и получи персональные рекомендации!"
        )
        kb_end = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 Записаться", callback_data="book_start")],
            [InlineKeyboardButton(text="🧠 Пройти ещё раз", callback_data="quiz")],
            [InlineKeyboardButton(text="🏠 Меню", callback_data="main_menu")],
        ])
        await cb.message.edit_text(text, reply_markup=kb_end, parse_mode="HTML")
        await state.clear()
        return

    q = QUIZ_QUESTIONS[idx]
    buttons = []
    for i, opt in enumerate(q["options"]):
        buttons.append([InlineKeyboardButton(text=opt, callback_data=f"quiz_{idx}_{i}")])

    text = (
        f"🧠 <b>ТЕСТ О ВОЛОСАХ</b> ({idx + 1}/{len(QUIZ_QUESTIONS)})\n\n"
        f"{q['q']}"
    )
    await cb.message.edit_text(
        text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("quiz_"))
async def quiz_answer(cb: CallbackQuery, state: FSMContext):
    # Ignore non-answer callbacks (quiz_next, etc.)
    if cb.data == "quiz_next" or cb.data == "quiz":
        return
    
    parts = cb.data.split("_")  # quiz_questionIdx_answerIdx
    if len(parts) < 3 or not parts[1].isdigit() or not parts[2].isdigit():
        await cb.answer("Ошибка")
        return
    
    q_idx = int(parts[1])
    answer_idx = int(parts[2])

    q = QUIZ_QUESTIONS[q_idx]
    correct = answer_idx == q["correct"]

    data = await state.get_data()
    score = data.get("score", 0) + (1 if correct else 0)
    await state.update_data(q_idx=q_idx + 1, score=score)

    icon = "✅" if correct else "❌"
    text = f"{icon} <b>{'Верно!' if correct else 'Не угадал!'}</b>\n\n{q['fact']}"

    kb_next = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ Следующий вопрос", callback_data="quiz_next")],
    ])
    await cb.message.edit_text(text, reply_markup=kb_next, parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "quiz_next")
async def quiz_next(cb: CallbackQuery, state: FSMContext):
    await _show_quiz_question(cb, state)


# ══════════════════════════════════════════════════════════
# QUICK REACTIONS — respond to emoji messages
# ══════════════════════════════════════════════════════════

@router.message(F.text.in_(["🔥", "❤️", "👍", "😍", "✨", "💖"]))
async def emoji_reaction(msg: Message, bot: Bot):
    """React to common emoji messages with salon-related responses"""
    reactions = {
        "🔥": ("🔥 Огонь! Это про наши работы?", ["📅 Записаться", "📸 Галерея"]),
        "❤️": ("💖 Спасибо! Мы тоже вас любим!", ["🏠 Меню"]),
        "👍": ("👍 Рады нравиться! Чем помочь?", ["📅 Записаться", "ℹ️ Контакты"]),
        "😍": ("😍 Ух, кому-то тут нравится! Заходи в галерею!", ["📸 Галерея"]),
        "✨": ("✨ Блеск! Это про наши.results!", ["📸 Галерея"]),
        "💖": ("💖 Мурашки! Нам важно каждое ваше сердечко!", ["🏠 Меню"]),
    }
    response_text, btns = reactions.get(msg.text, ("😊", ["🏠 Меню"]))

    # React to the user's message
    try:
        await bot.set_message_reaction(
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            reaction=[{"type": "emoji", "emoji": "💖"}],
        )
    except Exception:
        pass

    buttons = [[InlineKeyboardButton(text=b, callback_data="main_menu" if "Меню" in b else "book_start")] for b in btns]
    await msg.answer(response_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


# ══════════════════════════════════════════════════════════
# NOTIFICATION HELPERS (for admin to use)
# ══════════════════════════════════════════════════════════

async def send_booking_reminder(bot: Bot, chat_id: int, booking: dict):
    """Send a fun booking reminder"""
    from datetime import date
    bdate = date.fromisoformat(booking["booking_date"])
    days_until = (bdate - date.today()).days

    if days_until == 0:
        urgency = "🔴 <b>СЕГОДНЯ!</b>"
    elif days_until == 1:
        urgency = "🟡 <b>ЗАВТРА</b>"
    else:
        urgency = f"📅 Через {days_until} дн."

    text = (
        f"🔔 <b>НАПОМИНАНИЕ</b>\n\n"
        f"{urgency}\n\n"
        f"💇 {booking.get('service_name', '?')}\n"
        f"👩‍🎨 {booking.get('master_name', '?')}\n"
        f"⏰ {booking['time_slot']}\n\n"
        f"Ждём вас! 💖"
    )
    kb_remind = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_remind_{booking['id']}")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data=f"del_{booking['id']}")],
    ])
    await bot.send_message(chat_id, text, reply_markup=kb_remind, parse_mode="HTML")


# ══════════════════════════════════════════════════════════
# REMINDER CALLBACKS — confirm/reschedule from silent reminders
# ══════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("remind_ok_"))
async def remind_confirm(cb: CallbackQuery):
    """User confirms they'll attend — silent ack."""
    booking_id = int(cb.data.split("_")[-1])
    try:
        await cb.message.edit_text(
            f"✅ <b>Отлично!</b> Ждём вас завтра.\n\n"
            f"Если что — пишите, перенесём 😊",
            parse_mode="HTML",
        )
    except Exception:
        await cb.answer("✅ Подтверждено!")
    await cb.answer("✅ Подтверждено!")


@router.callback_query(F.data.startswith("remind_reschedule_"))
async def remind_reschedule(cb: CallbackQuery):
    """User wants to reschedule — redirect to booking flow."""
    booking_id = int(cb.data.split("_")[-1])
    try:
        await cb.message.edit_text(
            "📅 <b>Хорошо, перенесём!</b>\n\n"
            "Нажмите 'Записаться' чтобы выбрать новое время:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📅 Выбрать новое время", callback_data="book_start", style="primary")],
                [InlineKeyboardButton(text="❌ Отменить запись", callback_data=f"del_{booking_id}", style="danger")],
            ]),
        )
    except Exception:
        await cb.answer("📅 Перейдите в меню")


@router.callback_query(F.data.startswith("confirm_remind_"))
async def confirm_remind_old(cb: CallbackQuery):
    """Old-style reminder confirm (backward compat)."""
    booking_id = int(cb.data.split("_")[-1])
    try:
        await cb.message.edit_text(
            "✅ <b>Отлично!</b> Ждём вас завтра! 💖",
            parse_mode="HTML",
        )
    except Exception:
        await cb.answer("✅ OK!")
    await cb.answer("✅ Подтверждено!")
