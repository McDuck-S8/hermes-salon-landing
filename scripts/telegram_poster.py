#!/usr/bin/env python3
"""
Telegram Channel Poster — красивые посты с кнопками, форматированием, превью, картинками.
Работает через python-telegram-bot v22+ (async).
"""
import asyncio
import json
import logging
import os
import random
import sys
from datetime import datetime, time as dt_time
from pathlib import Path
from typing import Optional

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from telegram.constants import ParseMode

# ─── Config ─────────────────────────────────────────────────────────────
HERMES_HOME = Path("D:/Portable_Soft/hermes")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")  # ТВОЙ токен @max_brain_chef_bot

# Proxy configuration for V2RayN (shadowsocks)
PROXY_URL = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")

# Auto-detect V2RayN local proxy (default SOCKS5 on 10808)
if not PROXY_URL:
    # Try common V2RayN ports
    import socket
    for port in [10808, 10809, 1080, 1081, 8080, 8081]:
        try:
            sock = socket.create_connection(("127.0.0.1", port), timeout=1)
            sock.close()
            PROXY_URL = f"socks5://127.0.0.1:{port}"
            break
        except:
            pass

DB_PATH = HERMES_HOME / "cache" / "tg_poster.db"
LOG_PATH = HERMES_HOME / "logs" / "tg_poster.log"
IMAGES_DIR = HERMES_HOME / "assets" / "content_warehouse" / "images"

# Каналы (username -> chat_id)
CHANNELS = {
    "max_brain_chef_official": -1003777013964,
    "ai_frontier_you": -1003705792421,
    "max_brain_chef_ai": -1003882833000,
    "neuro_kitchen_ai": -1003525498743,
}

# Расписание постов (время UTC+3 / MSK)
POST_TIMES = ["09:00", "12:00", "15:00", "18:00", "21:00"]

# ─── Logging ────────────────────────────────────────────────────────────
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("tg_poster")

# ─── Prepared Posts Queue (5 posts × 4 channels = 20 posts over 5 days) ────────────────
PREPARED_POSTS = [
    {
        "id": "post1_problem_solution",
        "title": "Problem → Solution: Stop Manual Offer Hunting",
        "channel": "max_brain_chef_official",
        "day": 1,
        "time": "09:00",
        "text": """🛑 Перестал вручную искать офферы — сэкономил 10 ч/нед

Раньше: каждую утру 40 мин листал MyLead, Cpagrip, OfferVault. Вручную проверял: geo, payout, conversion, approval rate. В неделю терял ~3.5 часа на рутину.

Теперь: один бот делает это за 2 минуты.

🔧 Как настроил за 3 шага:
1. Добавил @max_brain_chef_bot
2. Нажал /offers — получил 7 горячих офферов под India cricket + crypto
3. Настроил фильтры: payout > $5, CR > 15%, approval < 24h

📊 Результат за неделю:
• 10 часов сэкономлено
• 0 пропущенных топ-офферов
• 3 новых GEO открыл (KE, NG, ZA)

Хочешь конфиг бота? Пиши в личку — скину .json + инструкцию 5 минут.

#CPA #арбитраж #автоматизация #офферы #India #крипто""",
        "image": "post1_problem_solution.png",
        "keyboard": [
            [InlineKeyboardButton("🤖 Получить конфиг бота", url="https://t.me/max_brain_chef_bot")],
            [InlineKeyboardButton("📢 Все каналы", url="https://t.me/max_brain_chef_official"),
             InlineKeyboardButton("💬 Чат", url="https://t.me/+nVpNjeTXzXE5YTRi")]
        ]
    },
    {
        "id": "post2_before_after",
        "title": "Before → After: 20 hrs/month saved on trend monitoring",
        "channel": "ai_frontier_you",
        "day": 1,
        "time": "12:00",
        "text": """📉 БЫЛО → 📈 СТАЛО: как перестал утонуть в RSS и начал ловить тренды

БЫЛО (2024):
• 15 RSS-фидов, 40 мин/день — только заголовки
• 60% трендов упускал (не успевал прочитать)
• Ручной перенос в Notion, теги, категории
• CTR постов: 1.2%

СТАЛО (2025):
• 1 бот (signal_daemon) сканирует 50+ источников за 15 мин
• Ловит 47 трендов/неделю — 0 пропусков
• Авто-разметка: тема, urgency, actionable insight
• CTR постов: 3.8% (+216%)

💡 Секрет: не «читать всё», а «фильтровать шум».
Signal daemon делает тяжелую работу:
• RSS/YouTube/Telegram/Reddit → единый поток
• LLM-классификация: tool launch / funding / regulation / trend
• Экспорт в JSON → в контент-пайплайн

📊 Метрики за месяц:
✅ 20 hrs saved
✅ CTR 1.2% → 3.8%
✅ 340% больше лидов с постов

Полный чек-лист внедрения — в закреплённом посте канала.

#AIтренды #автоматизация #signal_daemon #контент_стратегия #Pinterest #YouTube""",
        "image": "post2_before_after.png",
        "keyboard": [
            [InlineKeyboardButton("📋 Чек-лист внедрения", callback_data="checklist_implementation")],
            [InlineKeyboardButton("📢 Все каналы", url="https://t.me/max_brain_chef_official"),
             InlineKeyboardButton("🤖 Бот", url="https://t.me/max_brain_chef_bot")]
        ]
    },
    {
        "id": "post3_mistake_analysis",
        "title": "Mistake Analysis: Lost $200 on TikTok Ads in 48h",
        "channel": "max_brain_chef_ai",
        "day": 2,
        "time": "15:00",
        "text": """💸 Слил $200 за 48 часов на TikTok Ads — разбор ошибок

Ситуация: запустил креатив под India cricket betting (PWA). Бюджет $10/день. Ожидал CPA $5-8.

Что произошло:
🔴 День 1: Spend $10, 0 installs, CPA ∞
🔴 День 2: Spend $10, 1 install, CPA $20
🔴 День 3: Spend $180 (auto-scaled 🤦), 3 installs, CPA $60

Почему провалилось (мой post-mortem):
❌ 1. Overlap аудиторий — 3 креатива в одной ad group бились за одних юзеров. Frequency 3.2 к дню 2.
❌ 2. Нет creative testing — запустил 1 вариацию, не тестил hook/angle/CTA.
❌ 3. Нет auto-stop rules — TikTok радостно списал $180 за 3 лида.
❌ 4. Geo targeting — India слишком широкое. Нужны штаты с cricket affinity (MH, KA, TN, DL).

✅ Как исправил (второй запуск):
✅ Overlap check: 1 ad group = 1 creative angle
✅ Creative matrix: 3 hooks × 2 angles × 2 CTAs = 12 вариаций
✅ Auto-rules: stop if CPA > $15, frequency > 2.5, spend > $20/day
✅ Geo: Maharashtra + Karnataka + Tamil Nadu + Delhi

📊 Второй запуск (те же $10/день):
Spend $150 → 18 installs → CPA $8.3 → ROI 180% (payout $15)

🎯 Урок: $200 урок дешевле, чем $2000 на том же граблях.
Пиши в бот — скину чек-лист «TikTok Ads Audit: 12 пунктов перед запуском».

#TikTokAds #арбитраж #ошибки #case_study #India #cricket #CPA""",
        "image": "post3_mistake.png",
        "keyboard": [
            [InlineKeyboardButton("📋 Чек-лист TikTok Ads Audit", url="https://t.me/max_brain_chef_bot")],
            [InlineKeyboardButton("📢 Все каналы", url="https://t.me/max_brain_chef_official"),
             InlineKeyboardButton("💬 Чат", url="https://t.me/+nVpNjeTXzXE5YTRi")]
        ]
    },
    {
        "id": "post4_tool_closeup",
        "title": "Tool Close-up: Fal.ai — GPU inference for $0.003/pin",
        "channel": "neuro_kitchen_ai",
        "day": 2,
        "time": "18:00",
        "text": """⚡ ОДИН ИНСТРУМЕНТ: Fal.ai — генерация пинов за $0.003/шт

Проблема: нужен 50 пинов в неделю для Pinterest. Canva руками — 2 часа. Midjourney — $30/мес + дискорд. DALL-E 3 API — дорого и нет батчинга.

Решение: Fal.ai (serverless GPU)

🎯 Что умеет за мои задачи:
• Flux 2 (Nano Banana) — $0.0039/pin, лучший текст на картинке
• SDXL Turbo — $0.002/pin, скорость 1.5 сек
• Whisper v3 — $0.02/30 мин (транскрипт видео для контента)
• Llama 3.1 70B — $0.001/1k токенов (генерация промптов)

💻 Мой пайплайн (Python, 30 строк):
```python
import fal_client

def generate_pin(prompt: str, model="fal-ai/flux-pro/kontext") -> str:
    result = fal_client.subscribe(model, arguments={
        "prompt": f"Pinterest pin 1000x1500: {prompt}, clean modern design, readable text, high contrast",
        "image_size": "portrait_4_3",
        "num_images": 1
    }, with_logs=True)
    return result["images"][0]["url"]

# Batch 50 pins:
prompts = [f"AI tool: {tool}, benefit: {benefit}" for tool, benefit in zip(tools, benefits)]
urls = [generate_pin(p) for p in prompts]  # Параллельно через asyncio.gather
```

💰 Экономика: 50 пинов × $0.0039 = $0.195/неделя vs $30/мес Midjourney
⚡ Скорость: 50 пинов за 2 минуты (параллельно)
🔗 Бесплатно попробовать: fal.ai/playground (демо, без депозита)
💡 Альтернатива БЕЗ депозита: Bing Image Creator (DALL-E 3, 100/день) — bing.com/create

Сохрани пост — не потеряешь код пайплайна 🔑

#Fal_ai #Flux #AI_генерация #Pinterest #автоматизация #Python #GPU #serverless""",
        "image": "post4_tool_closeup.png",
        "keyboard": [
            [InlineKeyboardButton("🚀 Fal.ai Playground", url="https://fal.ai/playground"),
             InlineKeyboardButton("🎨 Bing Image Creator (FREE)", url="https://www.bing.com/images/create")],
            [InlineKeyboardButton("📢 Все каналы", url="https://t.me/max_brain_chef_official"),
             InlineKeyboardButton("🤖 Бот", url="https://t.me/max_brain_chef_bot")]
        ]
    },
    {
        "id": "post5_top3_comparison",
        "title": "Top 3 AI Image Tools 2025 — Real Comparison",
        "channel": "max_brain_chef_official",
        "day": 3,
        "time": "21:00",
        "text": """⚔️ ТОП-3 ИНСТРУМЕНТА ДЛЯ GEN КРЕАТИВОВ В 2025 (реально протестил)

Тестил 7 сервисов на задаче: 50 пинов в неделю для арбитража (India cricket, crypto, AI tools).

🥇 1. BING IMAGE CREATOR (DALL-E 3)
✅ Бесплатно, 100 генераций/день
✅ Лучшее следование промпту, читаемый текст на картинке
✅ Прямые ссылки на скачивание
❌ Медленно после 15 ускорений
❌ Нет батчинга, нет API

🥈 2. LEONARDO AI
✅ 150 кредитов/день (~50-70 пинов)
✅ ControlNet, Canvas, обучение своих LoRA
✅ Есть API (платный)
✅ Хорошие фотореалистичные люди
❌ Текст на картинках кривой
❌ Очередь в часы пик

🥉 3. PLAYGROUND AI
✅ 500 генераций/день БЕСПЛАТНО
✅ Быстрый SDXL Turbo
✅ Удобный интерфейс для батчинга
❌ Качество ниже DALL-E 3
❌ Нет апскейла встроенного

💡 МОЯ СХЕМА (вместе = 650+ пинов/день за $0):
• Идеи/тексты → Bing (DALL-E 3) — для главных пинов с текстом
• Массовые вариации → Playground — для A/B тестов
• Спецзадачи (ControlNet, фото люди) → Leonardo

🎯 Какой используешь ты? Голосуй реакцией:
👍 — Bing  ❤️ — Leonardo  🔥 — Playground  🎯 — Fal.ai (плачу)

#AI_инструменты #генерация_картинок #DALL_E_3 #Leonardo_AI #Playground #бесплатно #Pinterest #автоматизация""",
        "image": "post5_top3_comparison.png",
        "keyboard": [
            [InlineKeyboardButton("👍 Bing (DALL-E 3)", callback_data="vote_bing"),
             InlineKeyboardButton("❤️ Leonardo", callback_data="vote_leonardo"),
             InlineKeyboardButton("🔥 Playground", callback_data="vote_playground"),
             InlineKeyboardButton("🎯 Fal.ai", callback_data="vote_fal")],
            [InlineKeyboardButton("📢 Все каналы", url="https://t.me/max_brain_chef_official"),
             InlineKeyboardButton("💬 Чат", url="https://t.me/+nVpNjeTXzXE5YTRi")]
        ]
    },
]

# ─── Database ───────────────────────────────────────────────────────────
def init_db():
    import sqlite3
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel TEXT, category TEXT, content TEXT,
        status TEXT DEFAULT 'pending', msg_id INTEGER,
        posted_at TEXT, views INTEGER DEFAULT 0,
        post_id TEXT, image_path TEXT, created_at TEXT,
        scheduled_date TEXT, scheduled_time TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel TEXT, time TEXT, category TEXT, active INTEGER DEFAULT 1,
        post_id TEXT, scheduled_date TEXT
    )""")
    # Default schedule
    for ch in CHANNELS:
        for t in POST_TIMES:
            conn.execute(
                "INSERT OR IGNORE INTO schedule (channel, time, category, scheduled_date) VALUES (?,?,?,?)",
                (ch, t, "ai_news", datetime.now().strftime("%Y-%m-%d")),
            )
    conn.commit()
    conn.close()

def log_post(channel: str, category: str, content: str, status: str, msg_id: int = None, post_id: str = None, image_path: str = None):
    import sqlite3
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT INTO posts (channel, category, content, status, msg_id, posted_at, post_id, image_path) VALUES (?,?,?,?,?,?,?,?)",
        (channel, category, content, status, msg_id, datetime.now().isoformat(), post_id, image_path),
    )
    conn.commit()
    conn.close()

def get_pending_posts():
    """Get posts that are scheduled for today and not yet posted"""
    import sqlite3
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    today = datetime.now().strftime("%Y-%m-%d")
    rows = conn.execute(
        "SELECT * FROM posts WHERE status='pending' AND date(created_at)=? ORDER BY created_at",
        (today,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def queue_prepared_posts():
    """Insert the 5 prepared posts into DB for scheduling across 4 channels over 5 days (20 posts total)"""
    import sqlite3
    from datetime import timedelta
    
    conn = sqlite3.connect(str(DB_PATH))
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Get base date for scheduling
    base_date = datetime.now().date()
    
    # Channels and their assigned base times (rotating through POST_TIMES)
    channels = list(CHANNELS.keys())
    post_times = POST_TIMES  # ["09:00", "12:00", "15:00", "18:00", "21:00"]
    
    # Schedule: 5 posts × 4 channels = 20 posts over 5 days
    # Day 1: post1→ch1@09:00, post2→ch2@12:00, post3→ch3@15:00, post4→ch4@18:00
    # Day 2: post2→ch1@09:00, post3→ch2@12:00, post4→ch3@15:00, post5→ch4@18:00
    # Day 3: post3→ch1@09:00, post4→ch2@12:00, post5→ch3@15:00, post1→ch4@18:00
    # Day 4: post4→ch1@09:00, post5→ch2@12:00, post1→ch3@15:00, post2→ch4@18:00
    # Day 5: post5→ch1@09:00, post1→ch2@12:00, post2→ch3@15:00, post3→ch4@18:00
    # (post5 also gets 21:00 slot on day 1 for ch1 as bonus)
    
    for day_offset in range(5):  # 5 days
        schedule_date = base_date + timedelta(days=day_offset)
        date_str = schedule_date.strftime("%Y-%m-%d")
        
        for ch_idx, channel in enumerate(channels):
            # Each channel gets 1 post per day, rotating through posts
            # post_index = (day_offset + ch_idx) % 5
            post_index = (day_offset + ch_idx) % len(PREPARED_POSTS)
            post = PREPARED_POSTS[post_index]
            
            # Assign time slot based on channel index (rotate through POST_TIMES)
            time_slot = post_times[ch_idx % len(post_times)]
            
            # Insert into schedule table
            conn.execute(
                "INSERT OR IGNORE INTO schedule (channel, time, category, post_id, scheduled_date) VALUES (?,?,?,?,?)",
                (channel, time_slot, "prepared", post["id"], date_str)
            )
            
            # Insert into posts table as pending for this specific date/channel
            conn.execute(
                """INSERT OR IGNORE INTO posts (channel, category, content, status, post_id, image_path, created_at, scheduled_date, scheduled_time)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (channel, "prepared", post["text"], "pending", post["id"], post["image"], date_str, date_str, time_slot)
            )
    
    conn.commit()
    conn.close()
    print(f"Queued {len(PREPARED_POSTS) * len(CHANNELS)} prepared posts across {len(CHANNELS)} channels over 5 days")

# ─── Content Rendering ──────────────────────────────────────────────────
def get_prepared_post(post_id: str) -> dict:
    for p in PREPARED_POSTS:
        if p["id"] == post_id:
            return p
    return None

def render_prepared_post(post_id: str) -> tuple[str, InlineKeyboardMarkup, str]:
    """Returns (html_text, keyboard, image_path)"""
    post = get_prepared_post(post_id)
    if not post:
        return None, None, None
    
    # Build keyboard
    kb_rows = []
    for row in post["keyboard"]:
        kb_rows.append(row)
    kb = InlineKeyboardMarkup(kb_rows)
    
    image_path = str(IMAGES_DIR / post["image"]) if post["image"] else None
    return post["text"], kb, image_path

# ─── Posting ────────────────────────────────────────────────────────────
async def post_to_channel(bot: Bot, channel_key: str, post_id: str = None) -> bool:
    chat_id = CHANNELS[channel_key]
    
    if post_id:
        # Prepared post
        text, kb, image_path = render_prepared_post(post_id)
        if not text:
            log.error(f"Prepared post {post_id} not found")
            return False
        category = "prepared"
    else:
        # Fallback to random template (legacy)
        from_old = render_random_post()
        text, kb, image_path = from_old[0], from_old[1], None
        category = from_old[2]
    
    try:
        if image_path and Path(image_path).exists():
            # Post with photo
            with open(image_path, 'rb') as photo:
                msg = await bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=kb,
                )
        else:
            # Text only
            msg = await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=kb,
                disable_web_page_preview=False,
            )
        
        log_post(channel_key, category, text, "posted", msg.message_id, post_id, image_path)
        log.info(f"Posted [{category}] to {channel_key} (msg #{msg.message_id})")
        return True
    except TelegramError as e:
        log.error(f"Post failed [{channel_key}]: {e}")
        log_post(channel_key, category, text, f"error: {e}", post_id=post_id, image_path=image_path)
        return False

def render_random_post():
    """Legacy random post generation"""
    cat = random.choices(
        list(TEMPLATES.keys()),
        weights=[0.35, 0.25, 0.15, 0.15, 0.10],
        k=1
    )[0]
    text, kb = render_post(cat)
    return text, kb, cat

# ... (keep existing render_post, TEMPLATES, TOOLS_DB, etc. from original)

async def run_cycle():
    if not BOT_TOKEN:
        log.error("TELEGRAM_BOT_TOKEN not set")
        return 0

    # Ensure prepared posts are queued
    queue_prepared_posts()
    
    # Proxy configuration
    proxy_request = None
    if PROXY_URL:
        from telegram.request import HTTPXRequest
        proxy_request = HTTPXRequest(proxy_url=PROXY_URL)
        log.info(f"Using proxy: {PROXY_URL}")
    
    bot = Bot(token=BOT_TOKEN, request=proxy_request)
    posted = 0

    # Check for pending prepared posts for current time slot
    now = datetime.now().strftime("%H:%M")
    if now in POST_TIMES:
        import sqlite3
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        
        # Find scheduled posts for this time
        rows = conn.execute(
            """SELECT s.channel, s.post_id FROM schedule s
               JOIN posts p ON p.post_id = s.post_id
               WHERE s.time = ? AND p.status = 'pending' AND s.active = 1""",
            (now,)
        ).fetchall()
        conn.close()
        
        for row in rows:
            success = await post_to_channel(bot, row["channel"], row["post_id"])
            if success:
                posted += 1
            await asyncio.sleep(2)  # Rate limit

    await bot.close()
    return posted

# ─── CLI ────────────────────────────────────────────────────────────────
def status():
    import sqlite3
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    total = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    posted = conn.execute("SELECT COUNT(*) FROM posts WHERE status='posted'").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM posts WHERE status='pending'").fetchone()[0]
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
    print(f"  Pending: {pending}")
    print(f"  Schedule: {', '.join(POST_TIMES)} (MSK)")
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

def test_post(channel_key: str = None, post_id: str = None):
    """Send one test post"""
    async def _test():
        if not BOT_TOKEN:
            print("TELEGRAM_BOT_TOKEN not set")
            return
        bot = Bot(token=BOT_TOKEN)
        ch = channel_key or list(CHANNELS.keys())[0]
        success = await post_to_channel(bot, ch, post_id)
        await bot.close()
        print("OK" if success else "FAILED")
    asyncio.run(_test())

def queue_posts():
    queue_prepared_posts()
    print("Prepared posts queued for scheduling")

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
        channel = sys.argv[2] if len(sys.argv) > 2 else None
        post_id = sys.argv[3] if len(sys.argv) > 3 else None
        # Handle old format: test channel category post_id
        if post_id == "prepared" and len(sys.argv) > 4:
            post_id = sys.argv[4]
        test_post(channel, post_id)
    elif cmd == "queue":
        queue_posts()
    else:
        print(f"Usage: {sys.argv[0]} [cycle|status|gen|test|queue]")