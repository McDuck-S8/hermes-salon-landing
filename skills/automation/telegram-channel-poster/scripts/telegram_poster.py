#!/usr/bin/env python3
"""
Telegram Channel Poster — красивые посты с кнопками в 4 канала.
Работает через python-telegram-bot v22+ (async).
"""
import asyncio
import json
import logging
import os
import random
import sqlite3
import sys
from datetime import datetime, time as dt_time
from pathlib import Path
from typing import Optional

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from telegram.constants import ParseMode

# ─── Config ─────────────────────────────────────────────────────────────
HERMES_HOME = Path("D:/Portable_Soft/hermes")
DB_PATH = HERMES_HOME / "cache" / "tg_poster.db"
LOG_PATH = HERMES_HOME / "logs" / "tg_poster.log"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("tg_poster")

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
POST_TO_TELEGRAM = True  # Set False for dry-run

# Каналы: username -> chat_id (получены через getChat)
CHANNELS = {
    "max_brain_chef_official": -1003777013964,
    "ai_frontier_you": -1003705792421,
    "max_brain_chef_ai": -1003882833000,
    "neuro_kitchen_ai": -1003525498743,
}

# Расписание постов (MSK)
POST_TIMES = ["09:00", "12:00", "15:00", "18:00", "21:00"]

# ─── Content Templates ──────────────────────────────────────────────────
TEMPLATES = {
    "ai_news": [
        "🚀 <b>{title}</b>\n\n{summary}\n\n🔗 <a href=\"{url}\">Читать подробнее</a>",
        "🤖 <b>Новость ИИ:</b> {title}\n\n{summary}\n\n👇 Подробности тут: {url}",
        "⚡ <b>{title}</b>\n\n{summary}\n\n💡 <i>Мнение MAX-BRAIN:</i> {opinion}",
    ],
    "ai_tool": [
        "🛠 <b>Инструмент дня:</b> <a href=\"{url}\">{name}</a>\n\n{description}\n\n✨ <b>Фишки:</b> {features}\n\n👉 <a href=\"{url}\">Попробовать бесплатно</a>",
        "🔥 <b>{name}</b> — {tagline}\n\n{description}\n\n💰 <b>Прайс:</b> {pricing}\n\n🚀 <a href=\"{url}\">Запустить</a>",
    ],
    "code_tip": [
        "💻 <b>Сниппет:</b> {title}\n\n<pre><code>{code}</code></pre>\n\n📝 {explanation}\n\n#coding #python #ai",
        "⚡ <b>Быстрый совет:</b> {title}\n\n<pre><code>{code}</code></pre>\n\n💡 {explanation}",
    ],
    "analytics": [
        "📊 <b>Аналитика:</b> {title}\n\n{insight}\n\n📈 <b>Вывод:</b> {conclusion}\n\n🔗 Источник: {url}",
        "📈 <b>Тренд:</b> {title}\n\n{insight}\n\n💡 <b>Что делать:</b> {action}\n\n🔗 {url}",
    ],
    "motivation": [
        "💭 <b>Мысль дня</b>\n\n<blockquote>\"{quote}\"</blockquote>\n\n— {author}\n\n#motivation #mindset",
        "🎯 <b>Фокус:</b> {title}\n\n{body}\n\n✅ <b>Действие на сегодня:</b> {action}",
    ],
}

# Данные для подстановки
TOOLS_DB = [
    {"name": "Fal.ai", "url": "https://fal.ai", "tagline": "GPU inference для генеративных моделей", "description": "Запускай Flux, SDXL, Whisper, Llama на серверлесс GPU. Платишь за секунды.", "features": "Flux/SDXL/Whisper, serverless, OpenAI-совместимый API", "pricing": "от $0.0005/сек"},
    {"name": "Leonardo AI", "url": "https://leonardo.ai", "tagline": "Профессиональный AI-арт", "description": "Качественная генерация, ControlNet, Canvas, тренировка своих моделей.", "features": "ControlNet, Canvas, Fine-tuning, API", "pricing": "150 кредитов/день бесплатно"},
    {"name": "Bing Image Creator", "url": "https://www.bing.com/images/create", "tagline": "DALL-E 3 бесплатно", "description": "Microsoft даёт доступ к DALL-E 3 через аккаунт Microsoft. 100 генераций в день.", "features": "DALL-E 3, бесплатно, быстрый", "pricing": "бесплатно"},
    {"name": "Runway Gen-3", "url": "https://runwayml.com", "tagline": "Видео от текста SOTA", "description": "Генерация видео высокого качества. Gen-3 Alpha Turbo — быстрее и дешевле.", "features": "Text-to-Video, Image-to-Video, Director Mode", "pricing": "от $12/мес"},
    {"name": "Cursor", "url": "https://cursor.sh", "tagline": "AI-first IDE", "description": "VS Code форк с встроенным AI. Composer, Chat, Tab — пишешь код на естественном языке.", "features": "Composer, Chat, Tab, @Codebase", "pricing": "Pro $20/мес"},
]

NEWS_DB = [
    {"title": "GPT-5 анонсирован OpenAI", "summary": "Новая модель с рассуждением уровня PhD. Доступ через API и ChatGPT Plus.", "url": "https://openai.com/gpt-5", "opinion": "Гейм-чейнджер для агентов. Ждём доступ к API."},
    {"title": "Claude 4 Sonnet — лучший для кода", "summary": "Anthropic выпустила модель, обгоняющую GPT-4o по кодингу на 15%.", "url": "https://anthropic.com/claude-4", "opinion": "Стандарт для dev-агентов. Переключаемся."},
    {"title": "Llama 4 — open source мультимодалка", "summary": "Meta анонсировала Llama 4 с нативной поддержкой изображений и видео.", "url": "https://ai.meta.com/llama-4", "opinion": "Открытый вес = полный контроль. Важно для приватности."},
    {"title": "Google Veo 3 — видео SOTA", "summary": "Новая модель генерации видео с аудио. Качество близко к кинопрокату.", "url": "https://deepmind.google/technologies/veo", "opinion": "Для креативов — must try. API пока ограничен."},
]

CODE_SNIPPETS = [
    {"title": "Async HTTP клиент с retry", "code": "import httpx\nfrom tenacity import retry, stop_after_attempt, wait_exponential\n\n@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))\nasync def fetch(url: str) -> dict:\n    async with httpx.AsyncClient() as client:\n        r = await client.get(url, timeout=30)\n        r.raise_for_status()\n        return r.json()", "explanation": "Экспоненциальный бэкофф + автоматический ретрай. Экономит нервы при флакинге API."},
    {"title": "Параллельные LLM вызовы", "code": "import asyncio\nfrom openai import AsyncOpenAI\n\nclient = AsyncOpenAI()\n\nasync def parallel_llm(prompts: list[str]) -> list[str]:\n    tasks = [client.chat.completions.create(\n        model=\"gpt-4o-mini\",\n        messages=[{\"role\": \"user\", \"content\": p}]\n    ) for p in prompts]\n    return [(await t).choices[0].message.content for t in asyncio.gather(*tasks)]", "explanation": "asyncio.gather запускает все запросы одновременно. В 5-10x быстрее последовательно."},
    {"title": "BeautifulSoup + lxml парсинг", "code": "from bs4 import BeautifulSoup\nimport httpx\n\nasync def parse_article(url: str) -> dict:\n    async with httpx.AsyncClient() as client:\n        html = (await client.get(url)).text\n    soup = BeautifulSoup(html, 'lxml')\n    return {\n        'title': soup.select_one('h1')?.get_text(strip=True),\n        'content': '\\n'.join(p.get_text() for p in soup.select('article p')),\n        'links': [a['href'] for a in soup.select('article a[href]')]\n    }", "explanation": "lxml в 10x быстрее html.parser. Селекторы CSS = устойчивая выборка."},
]

ANALYTICS_DB = [
    {"title": "CPA в India: cricket betting ROI", "insight": "Крикет в Индии — 80% трафика. Ставки на IPL дают ROI 200-400% в сезон.", "conclusion": "Фокус на PWA/Telegram Mini App для крикета. Тренд: UPI + USDT.", "url": "https://example.com", "action": "Запустить тестовый креатив на TikTok India"},
    {"title": "AI tools affiliate: LTV > $50", "insight": "Подписки на AI (Cursor, Leonardo, Runway) держат юзеров 6+ месяцев. LTV $50-200.", "conclusion": "Писать evergreen-контент про инструменты. Афилиатки платят 20-30% recurring.", "url": "https://example.com", "action": "Добавить реф-ссылки в посты про AI"},
]

QUOTES = [
    ("Единственный способ делать великую работу — любить то, что делаешь.", "Стив Джобс"),
    ("Сложнее всего начать действовать, всё остальное зависит только от упорства.", "Амелия Эрхарт"),
    ("Богатство — это способность в полной мере прочувствовать жизнь.", "Генри Девид Торо"),
    ("Инвестируйте в себя. Ваш мозг — ваш самый ценный актив.", "Уоррен Баффетт"),
    ("Не ждите идеального момента, берите момент и делайте его идеальным.", "Неизвестен"),
]

MOTIVATION_DB = [
    {"title": "Правило 2 минут", "body": "Если задача занимает < 2 минут — сделай сразу. Не планируй, не откладывай.", "action": "Проверь входящие: что можно закрыть за 2 минуты?"},
    {"title": "Глубокая работа", "body": "4 часа фокуса > 12 часов мультитаскинга. Выдели блок 9-13 без телефона.", "action": "Поставь телефон в другую комнату на 4 часа."},
]

# ─── Database ───────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel TEXT, category TEXT, content TEXT,
        status TEXT DEFAULT 'pending', msg_id INTEGER,
        posted_at TEXT, error TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel TEXT, time TEXT, category TEXT, active INTEGER DEFAULT 1
    )""")
    # Default schedule
    for ch in CHANNELS:
        for t in POST_TIMES:
            conn.execute(
                "INSERT OR IGNORE INTO schedule (channel, time, category) VALUES (?,?,?)",
                (ch, t, "ai_news"),
            )
    conn.commit()
    conn.close()

def log_post(channel: str, category: str, content: str, status: str, msg_id: int = None, error: str = None):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO posts (channel, category, content, status, msg_id, posted_at, error) VALUES (?,?,?,?,?,?,?)",
        (channel, category, content, status, msg_id, datetime.now().isoformat(), error),
    )
    conn.commit()
    conn.close()

# ─── Content Generation ─────────────────────────────────────────────────
def pick_template(category: str) -> str:
    return random.choice(TEMPLATES.get(category, TEMPLATES["ai_news"]))

def render_post(category: str) -> tuple[str, InlineKeyboardMarkup]:
    """Returns (html_text, keyboard)"""
    if category == "ai_tool":
        tool = random.choice(TOOLS_DB)
        tpl = pick_template(category)
        text = tpl.format(**tool)
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("🚀 Попробовать", url=tool["url"]),
        ]])
    elif category == "code_tip":
        snippet = random.choice(CODE_SNIPPETS)
        tpl = pick_template(category)
        text = tpl.format(**snippet)
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("💾 Сохранить", callback_data=f"save_{snippet['title'][:20]}"),
        ]])
    elif category == "analytics":
        data = random.choice(ANALYTICS_DB)
        tpl = pick_template(category)
        text = tpl.format(**data)
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("📊 Подробнее", url=data["url"]),
        ]])
    elif category == "motivation":
        data = random.choice(MOTIVATION_DB)
        tpl = pick_template(category)
        text = tpl.format(**data)
        kb = None
    else:  # ai_news
        news = random.choice(NEWS_DB)
        tpl = pick_template(category)
        text = tpl.format(**news)
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔗 Источник", url=news["url"]),
        ]])

    # Add global buttons
    if kb:
        global_rows = kb.inline_keyboard + [
            [
                InlineKeyboardButton("📢 Все каналы", url="https://t.me/max_brain_chef_official"),
                InlineKeyboardButton("🤖 Бот", url="https://t.me/max_brain_chef_bot"),
            ],
            [
                InlineKeyboardButton("💬 Чат", url="https://t.me/+nVpNjeTXzXE5YTRi"),
                InlineKeyboardButton("🔥 Топ", callback_data="top_posts"),
            ],
        ]
        kb = InlineKeyboardMarkup(global_rows)
    else:
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📢 Все каналы", url="https://t.me/max_brain_chef_official"),
                InlineKeyboardButton("🤖 Бот", url="https://t.me/max_brain_chef_bot"),
            ],
            [
                InlineKeyboardButton("💬 Чат", url="https://t.me/+nVpNjeTXzXE5YTRi"),
                InlineKeyboardButton("🔥 Топ", callback_data="top_posts"),
            ],
        ])

    return text, kb

# ─── Posting ────────────────────────────────────────────────────────────
async def post_to_channel(bot: Bot, channel_key: str, category: str = None) -> bool:
    chat_id = CHANNELS[channel_key]
    cat = category or random.choices(
        list(TEMPLATES.keys()),
        weights=[0.35, 0.25, 0.15, 0.15, 0.10],
        k=1
    )[0]

    text, kb = render_post(cat)

    try:
        if POST_TO_TELEGRAM:
            msg = await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=kb,
                disable_web_page_preview=False,
            )
            log_post(channel_key, cat, text, "posted", msg.message_id)
            log.info(f"Posted [{cat}] to {channel_key} (msg #{msg.message_id})")
        else:
            log.info(f"[DRY-RUN] Would post [{cat}] to {channel_key}")
            log_post(channel_key, cat, text, "dry-run")
        return True
    except TelegramError as e:
        log.error(f"Post failed [{channel_key}]: {e}")
        log_post(channel_key, cat, text, f"error: {e}")
        return False

async def run_cycle():
    if not BOT_TOKEN:
        log.error("TELEGRAM_BOT_TOKEN not set")
        return 0

    bot = Bot(token=BOT_TOKEN)
    posted = 0

    now = datetime.now().strftime("%H:%M")
    if now not in POST_TIMES:
        next_slots = [s for s in POST_TIMES if s > now]
        if next_slots:
            log.debug(f"Next post at {next_slots[0]}")
        return 0

    for channel_key in CHANNELS:
        success = await post_to_channel(bot, channel_key)
        if success:
            posted += 1
        await asyncio.sleep(2)  # Rate limit

    await bot.close()
    return posted

# ─── CLI ────────────────────────────────────────────────────────────────
def status():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    total = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    posted = conn.execute("SELECT COUNT(*) FROM posts WHERE status='posted'").fetchone()[0]
    recent = conn.execute(
        "SELECT channel, category, substr(content,1,80) as preview, posted_at "
        "FROM posts WHERE status='posted' ORDER BY posted_at DESC LIMIT 10"
    ).fetchall()
    conn.close()

    print(f"Telegram Channel Poster")
    print(f"{'='*40}")
    print(f"  Channels: {len(CHANNELS)}")
    for k, v in CHANNELS.items():
        print(f"    @{k} -> {v}")
    print(f"  Total posts: {total}")
    print(f"  Posted: {posted}")
    print(f"  Schedule: {', '.join(POST_TIMES)} (MSK)")
    print(f"  Mode: {'LIVE' if POST_TO_TELEGRAM else 'DRY-RUN'}")
    print(f"\n  Recent:")
    for r in recent:
        print(f"    [{r['channel']}] {r['category']}: {r['preview']}...")

def gen_preview(count: int = 3):
    for _ in range(count):
        cat = random.choice(list(TEMPLATES.keys()))
        text, kb = render_post(cat)
        print(f"\n[{cat}]")
        print(text[:500])
        print("---")

async def test_post(channel_key: str, category: str):
    if not BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN not set")
        return
    bot = Bot(token=BOT_TOKEN)
    success = await post_to_channel(bot, channel_key, category)
    await bot.close()
    print("OK" if success else "FAILED")

def schedule_add(channel: str, time_str: str, category: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO schedule (channel, time, category) VALUES (?,?,?)", (channel, time_str, category))
    conn.commit()
    conn.close()
    print(f"Added: {channel} @ {time_str} [{category}]")

def schedule_list():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT channel, time, category, active FROM schedule ORDER BY time").fetchall()
    conn.close()
    for r in rows:
        status = "✅" if r[3] else "❌"
        print(f"  {status} {r[0]} @ {r[1]} [{r[2]}]")

if __name__ == "__main__":
    init_db()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "cycle"

    if cmd == "cycle":
        asyncio.run(run_cycle())
    elif cmd == "status":
        status()
    elif cmd == "gen":
        gen_preview(int(sys.argv[2]) if len(sys.argv) > 2 else 3)
    elif cmd == "test":
        channel = sys.argv[2] if len(sys.argv) > 2 else list(CHANNELS.keys())[0]
        category = sys.argv[3] if len(sys.argv) > 3 else None
        asyncio.run(test_post(channel, category))
    elif cmd == "sched-add":
        schedule_add(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "ai_news")
    elif cmd == "sched-list":
        schedule_list()
    else:
        print(f"Usage: {sys.argv[0]} [cycle|status|gen|test|sched-add|sched-list]")