#!/usr/bin/env python3
"""Telegram Channel Auto-Poster — контент-лента для CPA-воронки.

Генерирует и постит контент в Telegram канал по расписанию.
Трафик → CPA бот → офферы.
"""
import json, logging, os, random, sqlite3, sys, time, hashlib
from datetime import datetime, timedelta
from pathlib import Path
from telegram import Bot
from telegram.error import TelegramError

HERMES_HOME = Path("D:/Portable_Soft/hermes")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
# Если не указан отдельный канальный токен, используем основной
CHANNEL_ID = os.environ.get("TG_CHANNEL_ID", "@test_channel_name")

DB_PATH = HERMES_HOME / "cache" / "tg_channel.db"
POST_LOG = HERMES_HOME / "logs" / "tg_channel.log"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    handlers=[logging.FileHandler(str(POST_LOG), encoding="utf-8"), logging.StreamHandler()],
)
log = logging.getLogger("tg_channel")

# ── Content templates ──────────────────────────────────────────────────
CONTENT = {
    "ai_tips": [
        "🤖 *Лайфхак:* Используй {tool} для {task} — это экономит {hours} часов в неделю!",
        "🚀 *Гайд:* Как настроить {tool} за 5 минут и забыть о {problem}",
        "💡 *Совет:* {tool} теперь умеет {feature} — переходи по ссылке ниже 👇",
        "🔥 *Новинка:* Вышло обновление {tool} — {feature} доступно всем!",
        "📊 *Кейс:* Наш подписчик заработал {amount} с помощью {tool} за месяц",
    ],
    "finance": [
        "💰 *Заработок:* {method} — реально ли заработать {amount} в месяц?",
        "📈 *Стратегия:* {method} для начинающих — пошаговый гайд",
        "💎 *Кейс:* Пассивный доход {amount}/мес с помощью {method}",
        "📊 *Аналитика:* Топ-5 {method} в 2026 году",
        "🎯 *Цель:* Как накопить {amount} за год с помощью {method}",
    ],
    "tech": [
        "📱 *Обзор:* {product} — стоит ли покупать в 2026?",
        "⚡ *Сравнение:* {product} vs конкурент — что выбрать?",
        "🔧 *Инструкция:* Как настроить {product} под себя за 10 минут",
        "🎁 *Бонус:* Секретные функции {product}, о которых мало кто знает",
        "📊 *Тест:* {product} — реальные отзывы и тесты",
    ],
    "lifestyle": [
        "🌅 *Утро:* 3 привычки успешных людей, которые изменят твою жизнь",
        "📚 *Книга:* Рекомендуем к прочтению — меняет мышление",
        "🧠 *Мысль:* \"{quote}\" — {author}",
        "⭐ *Совет:* Как повысить продуктивность на {percent}% без выгорания",
        "🎯 *Фокус:* Одна вещь, которая делает твой день эффективнее",
    ],
}

TOOLS = ["ChatGPT", "Midjourney", "Claude", "Copilot", "Gemini", "Notion AI", "Perplexity"]
TASKS = ["генерации контента", "анализа данных", "написания кода", "создания картинок", "перевода текстов"]
PROBLEMS = ["рутиной", "повторяющимися задачами", "поиском информации", "написанием текстов"]
FEATURES = ["голосовой ввод", "анализ изображений", "создание видео", "распознавание речи"]
METHODS = ["крипто-трейдинг", "инвестиции в ETF", "арбитраж трафика", "фриланс", "инфобизнес"]
PRODUCTS = ["iPhone 17", "MacBook Air M4", "Samsung Galaxy S26", "Apple Vision Pro 2", "Meta Quest 4"]
AMOUNTS = ["$500", "$1000", "$2500", "$5000", "$10000"]
AUTHORS = ["Сенека", "Марк Аврелий", "Нассим Талеб", "Рэй Далио", "Джеймс Клир", "Роберт Кийосаки"]
QUOTES = [
    "Единственный способ делать великую работу — любить то, что делаешь",
    "Сложнее всего начать действовать, всё остальное зависит только от упорства",
    "Богатство — это способность в полной мере прочувствовать жизнь",
    "Инвестируйте в себя. Ваш мозг — ваш самый ценный актив",
    "Не ждите идеального момента, берите момент и делайте его идеальным",
]

HOURS = [2, 3, 5, 8, 10]
PERCENTS = [20, 30, 40, 50]

NICHE_PROBABILITIES = {"ai_tips": 0.35, "finance": 0.30, "tech": 0.20, "lifestyle": 0.15}

# ── Schedule ────────────────────────────────────────────────────────────
POST_TIMES = ["09:00", "12:00", "15:00", "18:00", "21:00"]
TG_CHANNEL_POSTS = HERMES_HOME / "cache" / "cpa_offers.json"  # reuse links

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT, category TEXT, status TEXT DEFAULT 'pending',
        posted_at TEXT, views INTEGER DEFAULT 0
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS offers (
        offer_id TEXT PRIMARY KEY, title TEXT, url TEXT, category TEXT
    )""")
    conn.commit()
    return conn

def pick_category():
    r = random.random()
    cumulative = 0
    for cat, prob in NICHE_PROBABILITIES.items():
        cumulative += prob
        if r <= cumulative:
            return cat
    return "ai_tips"

def generate_post(category: str) -> str:
    templates = CONTENT.get(category, CONTENT["ai_tips"])
    tpl = random.choice(templates)
    return tpl.format(
        tool=random.choice(TOOLS),
        task=random.choice(TASKS),
        hours=random.choice(HOURS),
        problem=random.choice(PROBLEMS),
        feature=random.choice(FEATURES),
        amount=random.choice(AMOUNTS),
        method=random.choice(METHODS),
        product=random.choice(PRODUCTS),
        quote=random.choice(QUOTES),
        author=random.choice(AUTHORS),
        percent=random.choice(PERCENTS),
    )

def get_offer_link():
    """Pick a CPA offer link to append to posts."""
    offers_path = HERMES_HOME / "cache" / "cpa_offers.json"
    if offers_path.exists():
        try:
            data = json.loads(offers_path.read_text(encoding="utf-8"))
            offers = data.get("offers", [])
            if offers:
                off = random.choice(offers)
                return f"\n\n👉 {off['title']}: {off['url']}"
        except: pass
    return ""

def run_cycle():
    now = datetime.now()
    current_hour = now.strftime("%H:%M")
    today = now.strftime("%Y-%m-%d")

    if current_hour not in POST_TIMES:
        next_slots = [s for s in POST_TIMES if s > current_hour]
        if next_slots:
            log.debug(f"Next post at {next_slots[0]}")
        return 0

    conn = init_db()
    existing = conn.execute(
        "SELECT COUNT(*) FROM posts WHERE date(posted_at)=?", (today,)
    ).fetchone()[0]

    slot_index = POST_TIMES.index(current_hour)
    if existing > slot_index:
        log.debug(f"Slot {current_hour} already filled")
        conn.close()
        return 0

    cat = pick_category()
    post_text = generate_post(cat)
    offer_link = get_offer_link()
    full_text = post_text + offer_link

    # Post to Telegram
    token = BOT_TOKEN
    if not token:
        log.error("TELEGRAM_BOT_TOKEN not set")
        conn.close()
        return 0

    try:
        bot = Bot(token=token)
        msg = bot.send_message(chat_id=CHANNEL_ID, text=full_text, parse_mode="Markdown")
        conn.execute(
            "INSERT INTO posts (content, category, posted_at, status) VALUES (?,?,?,?)",
            (full_text, cat, now.isoformat(), "posted"),
        )
        conn.commit()
        log.info(f"Posted [{cat}] to {CHANNEL_ID} (msg #{msg.message_id})")
        conn.close()
        return 1
    except TelegramError as e:
        log.error(f"Telegram post failed: {e}")
        conn.execute(
            "INSERT INTO posts (content, category, posted_at, status) VALUES (?,?,?,?)",
            (full_text, cat, now.isoformat(), f"error: {e}"),
        )
        conn.commit()
        conn.close()
        return 0

def status():
    conn = init_db()
    total = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    posted = conn.execute("SELECT COUNT(*) FROM posts WHERE status='posted'").fetchone()[0]
    last_posts = conn.execute(
        "SELECT category, substr(content,1,60) as preview, posted_at FROM posts WHERE status='posted' ORDER BY posted_at DESC LIMIT 5"
    ).fetchall()
    conn.close()
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"Telegram Channel Auto-Poster")
    print(f"{'='*40}")
    print(f"  Channel:    {CHANNEL_ID}")
    print(f"  Total:      {total}")
    print(f"  Posted:     {posted}")
    print(f"  Schedule:   {', '.join(POST_TIMES)}")

def config(tg_channel: str):
    """Set channel ID in .env or config."""
    global CHANNEL_ID
    CHANNEL_ID = tg_channel
    print(f"Channel set to: {CHANNEL_ID}. Add TG_CHANNEL_ID={tg_channel} to .env to persist.")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "cycle"
    if cmd == "cycle":
        run_cycle()
    elif cmd == "status":
        status()
    elif cmd == "config" and len(sys.argv) > 2:
        config(sys.argv[2])
    elif cmd == "gen":
        for _ in range(3):
            cat = pick_category()
            print(f"[{cat}] {generate_post(cat)}\n")
    else:
        print(f"Usage: {sys.argv[0]} [cycle|status|config @channel]")
