#!/usr/bin/env python3
"""
TG CPA Auto-Poster — автоматический постинг CPA-контента в Telegram каналы.


> Revisit: when CPA poster logic, offer selection, or posting strategy changes. Last touched: 2026-07-02.
Контент: AI-бизнес идеи, техно-новости, лайфхаки.
CPA-ссылки: FinCPANetwork / Admitad офферы.

Запуск:
    python tg_cpa_poster.py                    # отправить 1 пост в каждый канал
    python tg_cpa_poster.py --preview          # показать пост без отправки
    python tg_cpa_poster.py --loop 3600        # цикл каждые 3600 сек (1 час)
    python tg_cpa_poster.py --channels ch1 ch2 # конкретные каналы
"""

import json
import os
import random
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERMES_HOME / "scripts"))
from telegram_bridge import _load_env_if_missing

# --- CONFIG ---
POSTS_FILE = HERMES_HOME / "cache" / "tg_cpa_posts.json"
CHANNELS_FILE = HERMES_HOME / "cache" / "tg_channels.json"
POST_LOG = HERMES_HOME / "cache" / "tg_post_log.json"

# --- CONTENT TEMPLATES ---
# Each post: {text, category, cpa_link}
POSTS = [
    # AI Tips
    {
        "text": "🤖 5 способов заработать на AI в 2026:\n\n1. AI-ассистент для бизнеса (500-2000₽/мес за клиента)\n2. Автопостинг в соцсети (100-500₽/пост)\n3. Обработка документов (300-1000₽/день)\n4. AI-боты для записи (салоны, врачи)\n5. Генерация контента для блогеров\n\nПодробно: {link}\n\n#AI #заработок #бизнес",
        "category": "ai_tips",
    },
    {
        "text": "💡 Хак дня: Используй ChatGPT для написания постов в соцсети.\n\nПромпт: \"Напиши 5 постов для Instagram на тему [ниша]. Стиль: экспертный, с эмодзи, с призывом к действию.\"\n\nРезультат: 5 готовых постов за 2 минуты.\n\nА чтобы автоматизировать — {link}\n\n#ChatGPT #автоматизация #лайфхак",
        "category": "ai_tips",
    },
    {
        "text": "🚀 Telegram-бот для записи = пассивный доход.\n\nСалон красоты платит 1000-3000₽/мес за бота, который:\n• Принимает записи 24/7\n• Напоминает о визитах\n• Присылает акции\n\nСоздание: 1 вечер. Поддержка: 10 мин/мес.\n\nПодробнее: {link}\n\n#Telegram #боты #пассивный_доход",
        "category": "business_ideas",
    },
    {
        "text": "📊 AI-агент для анализа конкурентов:\n\nСканирует соцсети, сайты, отзывы → формирует отчёт.\n\nСтоимость для клиента: 3000-10000₽\nВремя на создание: 2-3 часа\nМаржинальность: 95%\n\nКак создать: {link}\n\n#AI #аналитика #бизнес",
        "category": "business_ideas",
    },
    {
        "text": "💰 ТОП-3 ниши для AI-ботов в 2026:\n\n1. Салоны красоты — запись + напоминания\n2. Кафе и рестораны — заказы + бронь\n3. Фитнес-клубы — расписание + абонементы\n\nКаждый бот = 1000-5000₽/мес recurring.\n\nКак начать: {link}\n\n#AI_боты #бизнес_идеи #пассивный_доход",
        "category": "business_ideas",
    },
    {
        "text": "🔧 Автоматизация рутины с AI:\n\n• Ответы на типичные вопросы → AI-бот\n• Расписание постов → автопостер\n• Отчётность → генератор отчётов\n\nЭкономия: 2-4 часа/день.\n\nНастроить за тебя: {link}\n\n#автоматизация #AI #продуктивность",
        "category": "ai_tips",
    },
    {
        "text": "🎯 Кейс: Салон красоты в Симферополе\n\nДо AI-бота: администратор тратит 4 часа/день на звонки.\nПосле: бот записывает 24/7, администратор — 30 мин/день.\n\nРезультат: +30% записей, -70% времени на звонки.\n\nТакой же бот для тебя: {link}\n\n#кейс #AI #салон_красоты",
        "category": "business_ideas",
    },
    {
        "text": "📈 Как я зарабатываю на AI:\n\n1. Создаю ботов (Telegram)\n2. Продаю бизнесу (1000-5000₽/мес)\n3. Поддерживаю (10 мин/мес)\n\nИтого: 10 клиентов = 10,000-50,000₽/мес\n\nНачать: {link}\n\n#заработок #AI #Telegram",
        "category": "business_ideas",
    },
    {
        "text": "⚡ Быстрый старт: Создай AI-ассистента за 15 минут\n\n1. Открой chat.openai.com\n2. Создай GPT с инструкцией\n3. Поделись ссылкой с друзьями\n\nПродвинутый вариант: {link}\n\n#AI #ChatGPT #быстрый_старт",
        "category": "ai_tips",
    },
    {
        "text": "🌍 AI-переводчик для бизнеса:\n\nПереводит документы, переписку, презентации.\n\nКлиенты: малый бизнес, экспортёры\nЦена: 500-2000₽/документ\nСкорость: 10 сек на страницу\n\nПодробнее: {link}\n\n#AI #перевод #бизнес",
        "category": "ai_tips",
    },
]


def load_channels():
    """Load channel list from cache."""
    if CHANNELS_FILE.exists():
        try:
            return json.loads(CHANNELS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def save_channels(channels):
    """Save channel list."""
    CHANNELS_FILE.write_text(json.dumps(channels, ensure_ascii=False, indent=2), encoding="utf-8")


def log_post(channel, post, success, error=None):
    """Log post result."""
    log = []
    if POST_LOG.exists():
        try:
            log = json.loads(POST_LOG.read_text(encoding="utf-8"))
        except Exception:
            pass

    log.append({
        "ts": datetime.now().isoformat(),
        "channel": channel,
        "category": post.get("category", "unknown"),
        "success": success,
        "error": str(error) if error else None,
    })
    log = log[-200:]  # keep last 200
    POST_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")


def send_post(channel_id, text, token):
    """Send post via TG Bot API with proxy."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": channel_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})

    proxy_handler = urllib.request.ProxyHandler({
        "http": "http://127.0.0.1:10809",
        "https": "http://127.0.0.1:10809",
    })
    opener = urllib.request.build_opener(proxy_handler)

    with opener.open(req, timeout=15) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        if not result.get("ok"):
            raise RuntimeError(f"TG API error: {result.get('description', 'unknown')}")
    return True


def preview():
    """Preview posts without sending."""
    print("=" * 50)
    print("TG CPA POSTER — PREVIEW")
    print("=" * 50)
    for i, post in enumerate(POSTS):
        print(f"\n--- Post {i+1} [{post['category']}] ---")
        print(post["text"].format(link="[CPA_LINK]"))
    print(f"\nTotal: {len(POSTS)} posts")


def main():
    _load_env_if_missing()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")

    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN not set")
        sys.exit(1)

    if "--preview" in sys.argv:
        preview()
        return

    channels = load_channels()
    if not channels:
        print("No channels configured!")
        print(f"Create {CHANNELS_FILE} with format:")
        print('  [{"id": "-1001234567890", "name": "My Channel"}]')
        print("Or pass --add-channel @channel_username")
        sys.exit(1)

    # Parse args
    target_channels = [c for c in channels if c.get("active", True)]

    # Filter by --channels arg
    if "--channels" in sys.argv:
        idx = sys.argv.index("--channels")
        ids = sys.argv[idx + 1:]
        target_channels = [c for c in target_channels if str(c["id"]) in ids]

    print(f"Posting to {len(target_channels)} channels...")

    post = random.choice(POSTS)
    text = post["text"].format(link="[Зарегистрируйтесь по ссылке в описании канала]")

    for ch in target_channels:
        try:
            send_post(ch["id"], text, token)
            print(f"  OK: {ch.get('name', ch['id'])}")
            log_post(ch["id"], post, True)
        except Exception as e:
            print(f"  FAIL: {ch.get('name', ch['id'])} — {e}")
            log_post(ch["id"], post, False, str(e))

    # Loop mode
    if "--loop" in sys.argv:
        idx = sys.argv.index("--loop")
        interval = int(sys.argv[idx + 1]) if idx + 1 < len(sys.argv) else 3600
        print(f"\nLoop mode: posting every {interval}s")
        while True:
            time.sleep(interval)
            post = random.choice(POSTS)
            text = post["text"].format(link="[Ссылка в описании канала]")
            for ch in target_channels:
                try:
                    send_post(ch["id"], text, token)
                    print(f"  [{datetime.now().strftime('%H:%M')}] OK: {ch.get('name', ch['id'])}")
                    log_post(ch["id"], post, True)
                except Exception as e:
                    print(f"  [{datetime.now().strftime('%H:%M')}] FAIL: {e}")
                    log_post(ch["id"], post, False, str(e))


if __name__ == "__main__":
    main()
