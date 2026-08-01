#!/usr/bin/env python3
"""
AI Tools Hub Auto-Poster — автопостинг в Telegram канал.
Посты с ссылками на микро-сайт https://mcduck-s8.github.io/ai-tools-hub/

> Revisit: when AI tools poster logic, content generation, or posting schedule changes. Last touched: 2026-07-02.

Запуск:
    python ai_tools_poster.py                    # отправить 1 пост
    python ai_tools_poster.py --preview          # показать без отправки
    python ai_tools_poster.py --loop 3600        # цикл каждые 3600 сек
"""

import os
import sys
import json
import random
import time
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path("D:/Portable_Soft/hermes")
sys.path.insert(0, str(HERMES_HOME / "scripts"))

from telegram_bridge import send_telegram_message

SITE_URL = "https://mcduck-s8.github.io/ai-tools-hub/"
CHANNEL = "@ai_frontier_you"

POSTS = [
    {
        "text": """🤖 5 AI-инструментов, которые заменят 2 сотрудников:

1. Автопостинг — AI пишет посты, вы одобряете
2. Telegram-бот — принимает записи 24/7
3. Аналитик данных — находит тренды за 2 минуты
4. Генератор контента — посты, статьи, рассылки
5. AI-CRM — автоматическая сегментация клиентов

Попробовать: {link}

#AI #автоматизация #бизнес""",
    },
    {
        "text": """💡 Хак: AI-бот для записи в салон = 1000-3000₽/мес пассивного дохода

Бот делает:
• Принимает записи 24/7
• Напоминает о визитах
• Ведёт базу клиентов
• Отправляет акции

Создание: 1 вечер. Поддержка: 10 мин/мес.

Подробнее: {link}

#салон #бот #пассивный_доход""",
    },
    {
        "text": """🚀 AI-аналитик данных — загрузите CSV, получите отчёт

Что умеет:
• Находит тренды и аномалии
• Делает прогнозы
• Генерирует графики
• Пишет выводы простым языком

Вместо аналитика за 50 000₽/мес → AI за 490₽/мес

Попробовать: {link}

#аналитика #данные #AI""",
    },
    {
        "text": """📈 Кейс: AI-постер увеличил охват на 340%

Что сделали:
• AI генерирует 10 постов в день
• Автопубликация в 3 соцсети
• А/B тестирование заголовков
• Автоматические хэштеги

Результат: +340% охвата, -80% времени на контент

Настроить у себя: {link}

#маркетинг #соцсети #AI""",
    },
    {
        "text": """🎯 AI-CRM для малого бизнеса — забудьте про Excel

Что получите:
• Автоматическая сегментация клиентов
• Прогноз оттока (кто уйдёт)
• Персональные рекомендации
• Напоминания о повторных продажах

Вместо CRM за 5000₽/мес → AI за 1990₽/мес

Подробнее: {link}

#CRM #клиенты #бизнес""",
    },
    {
        "text": """🧠 AI-репетитор — персональный учитель 24/7

Что умеет:
• Математика, языки, программирование
• Адаптируется под уровень ученика
• Объясняет простым языком
• Даёт практику с обратной связью

Вместо репетитора за 2000₽/час → AI за 590₽/мес

Попробовать: {link}

#обучение #образование #AI""",
    },
    {
        "text": """⚡ Как начать зарабатывать на AI сегодня:

Шаг 1: Выберите инструмент (бот, постер, аналитик)
Шаг 2: Настройте за 5 минут
Шаг 3: Предложите услугу 10 клиентам
Шаг 4: Получайте 1000-5000₽/мес за автоматизацию

Начать: {link}

#заработок #AI #бизнес""",
    },
]


def post_one(preview=False):
    """Отправить один случайный пост."""
    post = random.choice(POSTS)
    text = post["text"].format(link=SITE_URL)

    if preview:
        print("=" * 50)
        print("PREVIEW:")
        print("=" * 50)
        print(text)
        print("=" * 50)
        return True

    try:
        result = send_telegram_message(text=text, chat_id=CHANNEL)
        print(f"[{datetime.now()}] Posted to {CHANNEL}: OK")
        return True
    except Exception as e:
        print(f"[{datetime.now()}] ERROR: {e}")
        return False


def main():
    args = sys.argv[1:]

    if "--preview" in args:
        post_one(preview=True)
        return

    if "--loop" in args:
        idx = args.index("--loop")
        interval = int(args[idx + 1]) if idx + 1 < len(args) else 3600
        print(f"Starting loop, interval={interval}s")
        while True:
            post_one()
            time.sleep(interval)
    else:
        post_one()


if __name__ == "__main__":
    main()
