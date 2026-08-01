"""
Lumina AI — Personal Beauty Concierge
Smart booking, aftercare, photo analysis, predictive recommendations.
"""

import random
from datetime import date, timedelta

AI_GREETINGS = {
    "morning": [
        "☀️ Доброе утро, {name}! Готова к новому дню красоты?",
        "🌅 Утро, {name}! Как твои волосы после вчерашней укладки?",
        "☀️ Доброе утро! Сегодня идеальный день для нового образа, {name}",
    ],
    "afternoon": [
        "🌸 Добрый день, {name}! Как настроение?",
        "☀️ Привет, {name}! Чем могу помочь сегодня?",
        "🌸 День в разгаре, {name}! Запишись на процедуру — освободилось окно!",
    ],
    "evening": [
        "🌙 Добрый вечер, {name}! Успеешь записаться на завтра?",
        "✨ Привет, {name}! Вечер — время для планов на красоту",
        "🌙 Добрый вечер! Пока ты отдыхаешь, я подобрала для тебя идеальное окно завтра",
    ],
}


def get_time_of_day() -> str:
    from datetime import datetime
    hour = datetime.now().hour
    if hour < 12:
        return "morning"
    elif hour < 17:
        return "afternoon"
    return "evening"


def get_greeting(client_name: str) -> str:
    tod = get_time_of_day()
    template = random.choice(AI_GREETINGS[tod])
    return template.format(name=client_name or "красавица")


# ── AI-Like Booking Messages ──────────────────────────────

SMART_BOOKING_REASONS = [
    "Я подобрала именно этот слот, потому что {master} обычно делает {service} в это время — у неё руки настроены! ✨",
    "Отличный выбор! В {time} у {master} есть окно, а после неё обычно идёт перерыв — не придётся ждать.",
    "{time} — идеальное время: салон не будет переполнен, и {master} сможет уделить тебе максимум внимания 💖",
    "Я нашла это окно специально для тебя: {master} только что закончила курс по {service} и уже ждёт! 🎓",
]


def smart_booking_reason(master_name: str, service_name: str, time_slot: str) -> str:
    template = random.choice(SMART_BOOKING_REASONS)
    return template.format(master=master_name, service=service_name, time=time_slot)


# ── Aftercare Messages ────────────────────────────────────

AFTERCARE = {
    "hair_color": {
        1: [
            "🎨 <b>День 1 после окрашивания</b>\n\n"
            "Сегодня моем голову только <b>прохладной водой</b> (до 35°C). "
            "Шампунь только для окрашенных волос!\n\n"
            "💡 <b>Совет:</b> Не используй кондиционер на корни — только на длину.",
        ],
        3: [
            "🎨 <b>День 3</b>\n\n"
            "Можно использовать <b>бальзам-уход</b> для закрепления цвета. "
            "Избегай горячего фена — пусть сохнет естественно 🌿",
        ],
        7: [
            "🎨 <b>Неделя после окрашивания</b>\n\n"
            "Как себя чувствуют волосы? Скинь фото — я оценю, как смывается цвет! 📸",
        ],
        14: [
            "🎨 <b>Две недели</b>\n\n"
            "Цвет стабилизировался! Если хочешь освежить — записывайся, "
            "а пока — уходовая маска раз в неделю 💖",
        ],
    },
    "hair_cut": {
        1: [
            "✂️ <b>День 1 после стрижки</b>\n\n"
            "Волшебство свершилось! 💇‍♀️\n"
            "Совет: Не собирай волосы в тугой хвост первые 2 дня.",
        ],
        7: [
            "✂️ <b>Неделя после стрижки</b>\n\n"
            "Волосы привыкли к новой форме? Если нужна коррекция — пиши!",
        ],
    },
    "manicure": {
        1: [
            "💅 <b>День 1 после маникюра</b>\n\n"
            "Твои ноготки выглядят шикарно! ✨\n"
            "Совет: Не контактируй с горячей водой первые 2 часа.",
        ],
        7: [
            "💅 <b>Неделя маникюра</b>\n\n"
            "Как держится покрытие? Если появились сколы — исправим бесплатно!",
        ],
    },
}


def get_aftercare(service_category: str, day: int) -> str | None:
    """Get aftercare message for service category and day post-visit."""
    cat = AFTERCARE.get(service_category, {})
    return cat.get(day)


# ── Photo Analysis (simulated) ────────────────────────────

PHOTO_RESPONSES = [
    "📸 Вижу! На основе твоего фото я рекомендую:\n\n"
    "• 💇 {service} — для обновления стиля\n"
    "• 🧴 {treatment} — для улучшения состояния\n\n"
    "Запишешься? 😊",

    "📸 Отличное фото! Мои рекомендации:\n\n"
    "• {service} — это то, что тебе нужно сейчас\n"
    "• {treatment} — для поддержания результата\n\n"
    "Хочешь записаться? ✨",
]

PHOTO_SERVICES = [
    ("Стрижка каскадом", "Уход кератиновый"),
    ("Окрашивание мелирование", "Маска восстанавливающая"),
    ("Укладка объёмная", "Спа-процедура для волос"),
    ("Маникюр гель-лак", "Педикюрspa"),
    ("Коррекция бровей", "Ламинирование бровей"),
]


def suggest_from_photo() -> str:
    service, treatment = random.choice(PHOTO_SERVICES)
    template = random.choice(PHOTO_RESPONSES)
    return template.format(service=service, treatment=treatment)


# ── Weather-Aware Notifications ────────────────────────────

WEATHER_TIPS = {
    "rain": [
        "🌧 Завтра дождь! Возьми зонт, чтобы не испортить укладку. "
        "А мы уже готовим для тебя полотенце и кофе ☕",
    ],
    "hot": [
        "☀️ Завтра жарко! Рекомендую лёгкую укладку с фиксацией — "
        "волосы не будут пушились от влаги 🌊",
    ],
    "cold": [
        "❄️ На улице холодно! Возьми шапку — но записывайся к нам, "
        "мы сделаем тебя самой красивой этой зимой 🎀",
    ],
    "default": [
        "📅 Завтра у тебя запись! Ждём тебя в {time} 💖",
        "🌸 Напоминание: завтра в {time} у тебя процедура!",
    ],
}


def weather_tip(weather: str = "default", time_slot: str = "14:00") -> str:
    tips = WEATHER_TIPS.get(weather, WEATHER_TIPS["default"])
    return random.choice(tips).format(time=time_slot)


# ── Gift Certificate ──────────────────────────────────────

GIFT_CERT_TEMPLATES = [
    "🎁 <b>Подарочный сертификат</b>\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "💎 {amount}₽ на любую услугу\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "От: {sender}\n"
    "Для: {recipient}\n\n"
    "Сертификат действителен 30 дней.\n"
    "Скопируй код: <code>{code}</code>",
]


def gift_certificate(amount: int, sender_name: str, recipient_name: str) -> str:
    code = f"GIFT-{random.randint(1000, 9999)}-{amount}"
    return GIFT_CERT_TEMPLATES[0].format(
        amount=amount, sender=sender_name, recipient=recipient_name, code=code
    )


# ── Predictive Recommendations ─────────────────────────────

def predict_next_visit(service_history: list[dict]) -> str | None:
    """Based on visit history, predict when client should return."""
    if not service_history:
        return None

    last = service_history[0]
    service = last.get("service_name", "процедуру")
    last_date = last.get("booking_date")
    if not last_date:
        return None

    try:
        last_dt = date.fromisoformat(last_date)
    except ValueError:
        return None

    days_since = (date.today() - last_dt).days

    if "стрижк" in service.lower() and days_since >= 28:
        return (
            f"💇 Прошло {days_since} дней с последней стрижки!\n"
            f"Идеальное время для обновления. Хочешь записаться?"
        )
    elif "окрашиван" in service.lower() and days_since >= 42:
        return (
            f"🎨 Прошло {days_since} дней с последнего окрашивания.\n"
            f"Корневая зона может быть заметна. Запишешься на освежение?"
        )
    elif "маникюр" in service.lower() and days_since >= 18:
        return (
            f"💅 Прошло {days_since} дней с маникюра.\n"
            f"Ноготки пора обновить! Запишешься?"
        )
    return None
