#!/usr/bin/env python3
"""Post fresh AI tools content to Telegram channel @ai_frontier_you"""

import json

> Revisit: when AI tools poster logic, content freshness, or multi-channel posting changes. Last touched: 2026-07-02.
import sys
import os
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path("D:/Portable_Soft/hermes")
sys.path.insert(0, str(HERMES_HOME / "scripts"))

from telegram_bridge import send_telegram_message

CHANNEL = "@ai_frontier_you"
SITE_URL = "https://mcduck-s8.github.io/ai-tools-hub/"
POSTED_FILE = HERMES_HOME / "cache" / "posted_links.json"

# Fresh posts with links to real AI tools and resources
FRESH_POSTS = [
    {
        "text": """🔥 ТОП-3 бесплатных AI инструмента июля 2026:

1️⃣ Claude (Anthropic) — лучший бесплатный чат для анализа документов и кода. До 100 кредитов/мес бесплатно.

2️⃣ Gemini + Google Workspace — AI встроенный в Gmail, Docs, Sheets. Бесплатно с Google аккаунтом.

3️⃣ Perplexity — AI-поиск с цитатами из источников. Заменяет Google для исследований.

📌 Бонус: NotebookLM — бесплатный AI для анализа ваших документов (PDF, заметки, ссылки).

Как начать: {link}

#AITools #Бесплатно #Claude #Gemini #Perplexity"""
    },
    {
        "text": """🧠 AI для бизнеса: 3 инструмента, которые реально экономят время

✅ AI-автопостинг — генерирует посты для соцсетей за 2 минуты
✅ AI-бот для записи — принимает заявки 24/7, напоминает о визитах  
✅ AI-аналитик данных — загрузите CSV, получите отчёт с трендами

Вместо 3 сотрудников → 1 AI-инструмент = 1000-3000₽/мес

Попробовать бесплатно: {link}

#Бизнес #Автоматизация #AI #Экономия"""
    },
    {
        "text": """⚡ 10 AI-инструментов, которые должен знать каждый в 2026:

💬 Чат: Claude, ChatGPT, Gemini
🔍 Поиск: Perplexity, Grok  
🎨 Дизайн: Canva AI, Midjourney
📹 Видео: Veo, Synthesia
🎙️ Голос: ElevenLabs, Wispr Flow
⚡ Автоматизация: Make, n8n, Gumloop
📝 Заметки: Notion AI, Mem

Полный гайд с ссылками: {link}

#AI #Инструменты #Подборка #2026"""
    },
    {
        "text": """💡 Как заработать на AI без технических навыков:

1. Создайте Telegram-бота для записи в салон (1 вечер)
2. Предложите услугу 10 салонам в вашем городе
3. Получайте 1000-3000₽/мес за поддержку

Бот делает:
• Принимает записи 24/7
• Напоминает о визитах
• Ведёт базу клиентов

Инструкция: {link}

#Заработок #AI #Пассивный_Доход #Бизнес"""
    },
    {
        "text": """🚀 AI-обучение за 30 минут:

Уровень 1 (5 мин): Зарегистрируйтесь в Claude или ChatGPT
Уровень 2 (10 мин): Задайте 10 вопросов по вашей работе
Уровень 3 (15 мин): Попросите AI написать пост, письмо или отчёт
Уровень 4 (30 мин): Автоматизируйте рутину с AI

Результат: вы экономите 2-4 часа в неделю на рутине.

Начать: {link}

#Обучение #AI #Продуктивность #Тайм_Менеджмент"""
    },
]

def load_posted():
    """Load list of posted URLs/texts."""
    if POSTED_FILE.exists():
        try:
            return json.loads(POSTED_FILE.read_text(encoding="utf-8"))
        except:
            return []
    return []

def save_posted(data):
    """Save posted list."""
    POSTED_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def post_one(preview=False):
    """Post one fresh item."""
    posted = load_posted()
    
    # Find a post we haven't sent yet
    available = []
    for i, post in enumerate(FRESH_POSTS):
        post_id = f"fresh_{i}"
        if post_id not in [p.get("id") for p in posted]:
            available.append((i, post))
    
    if not available:
        # Reset — all posts sent, start over
        posted = []
        save_posted(posted)
        available = list(enumerate(FRESH_POSTS))
    
    idx, post = available[0]
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
        # Mark as posted
        posted.append({
            "id": f"fresh_{idx}",
            "url": SITE_URL,
            "posted_at": datetime.now().isoformat(),
            "preview": text[:100]
        })
        save_posted(posted)
        print(f"[{datetime.now()}] Posted to {CHANNEL}: OK")
        return True
    except Exception as e:
        print(f"[{datetime.now()}] ERROR: {e}")
        return False

if __name__ == "__main__":
    if "--preview" in sys.argv:
        post_one(preview=True)
    else:
        post_one()
