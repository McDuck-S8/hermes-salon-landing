# Telegram Poster Technical Reference — python-telegram-bot v22+ Async Patterns

## Why python-telegram-bot (NOT direct HTTP)

| Approach | Result | Reason |
|----------|--------|--------|
| `urllib.request` / `requests` to `api.telegram.org` | **TIMEOUT** | V2RayN shadowsocks proxy doesn't route Python HTTP correctly |
| `python-telegram-bot` v22+ (async) | **WORKS** | Manages own connection pooling, handles proxy via env |

**Key insight**: The library's internal `httpx` client respects system proxy / handles connection reuse properly. Direct HTTP calls hang on `api.telegram.org` through the proxy.

---

## Working Configuration

```python
# Environment (in .env)
TELEGRAM_BOT_TOKEN=8656692973:AAH_...  # @max_brain_chef_bot

# Channel IDs (resolved via bot.get_chat())
CHANNELS = {
    "max_brain_chef_official": -1003777013964,  # @max_brain_chef_official
    "ai_frontier_you": -1003705792421,           # @ai_frontier_you
    "max_brain_chef_ai": -1003882833000,         # @max_brain_chef_ai
    "neuro_kitchen_ai": -1003525498743,          # @neuro_kitchen_ai
}
```

---

## Core Async Pattern (from `telegram_poster.py`)

```python
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.error import TelegramError

async def post_to_channel(bot: Bot, channel_id: int, text: str, 
                          image_path: str = None, 
                          keyboard: InlineKeyboardMarkup = None) -> bool:
    try:
        if image_path and Path(image_path).exists():
            with open(image_path, 'rb') as photo:
                msg = await bot.send_photo(
                    chat_id=channel_id,
                    photo=photo,
                    caption=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard,
                )
        else:
            msg = await bot.send_message(
                chat_id=channel_id,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
                disable_web_page_preview=False,
            )
        
        # Log success
        logger.info(f"Posted to {channel_id} (msg #{msg.message_id})")
        return True
        
    except TelegramError as e:
        logger.error(f"Post failed [{channel_id}]: {e}")
        return False
    finally:
        # CRITICAL: Close session to avoid "bot already closed" errors
        await bot.session.close()
```

---

## Keyboard Builders

```python
def build_post_keyboard(channel_key: str) -> InlineKeyboardMarkup:
    """Standard footer keyboard for all posts"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 Все каналы", url="https://t.me/max_brain_chef_official"),
            InlineKeyboardButton("🤖 Бот", url="https://t.me/max_brain_chef_bot"),
        ],
        [
            InlineKeyboardButton("💬 Чат", url="https://t.me/+nVpNjeTXzXE5YTRi"),
            InlineKeyboardButton("🔥 Топ", callback_data="top_posts"),
        ],
    ])

def build_cta_keyboard(primary_url: str, primary_text: str, 
                        secondary: list = None) -> InlineKeyboardMarkup:
    """Post-specific CTA + footer"""
    rows = [[InlineKeyboardButton(primary_text, url=primary_url)]]
    if secondary:
        rows.append([InlineKeyboardButton(t, url=u) for t, u in secondary])
    rows.extend(build_post_keyboard("").inline_keyboard)
    return InlineKeyboardMarkup(rows)
```

---

## Scheduling Pattern (Cron-compatible)

```python
# In run_cycle() - called every 30 min via cron
POST_TIMES = ["09:00", "12:00", "15:00", "18:00", "21:00"]  # MSK

async def run_cycle():
    bot = Bot(token=BOT_TOKEN)
    now = datetime.now().strftime("%H:%M")
    
    if now not in POST_TIMES:
        return 0
    
    # Get pending posts for this time slot from DB
    pending = get_pending_posts(now)  # [(channel, post_id), ...]
    
    for channel, post_id in pending:
        await post_to_channel(bot, channel, post_id)
        await asyncio.sleep(2)  # Rate limit: 30 msg/sec global, but be nice
    
    await bot.session.close()
    return len(pending)
```

---

## Database Schema (SQLite)

```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel TEXT,           -- channel key
    category TEXT,          -- prepared / ai_news / ai_tool / etc
    content TEXT,           -- full HTML
    status TEXT DEFAULT 'pending',  -- pending / posted / error
    msg_id INTEGER,         -- Telegram message_id
    posted_at TEXT,         -- ISO timestamp
    post_id TEXT,           -- our prepared post ID (e.g., "post1_problem_solution")
    image_path TEXT         -- local image path
);

CREATE TABLE schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel TEXT,
    time TEXT,              -- "09:00"
    category TEXT,
    active INTEGER DEFAULT 1,
    post_id TEXT            -- links to prepared_posts
);
```

---

## Prepared Posts Queue (from `telegram_poster.py`)

```python
PREPARED_POSTS = [
    {
        "id": "post1_problem_solution",
        "title": "Problem → Solution: Stop Manual Offer Hunting",
        "channel": "max_brain_chef_official",
        "day": 1, "time": "09:00",
        "text": "...",  # full HTML
        "image": "post1_problem_solution.png",
        "keyboard": [...]  # InlineKeyboardMarkup rows
    },
    # ... 4 more posts across 4 channels over 5 days
]
```

**Queue on startup:**
```python
def queue_prepared_posts():
    """Insert prepared posts into DB for scheduling"""
    today = datetime.now().strftime("%Y-%m-%d")
    for post in PREPARED_POSTS:
        # Schedule table
        conn.execute(
            "INSERT OR IGNORE INTO schedule (channel, time, category, post_id) VALUES (?,?,?,?)",
            (post["channel"], post["time"], "prepared", post["id"])
        )
        # Posts table (pending)
        conn.execute(
            """INSERT OR IGNORE INTO posts (channel, category, content, status, post_id, image_path, created_at)
               VALUES (?,?,?,?,?,?,?)""",
            (post["channel"], "prepared", post["text"], "pending", 
             post["id"], post["image"], today)
        )
```

---

## Rate Limits & Safety

| Limit | Value | Handling |
|-------|-------|----------|
| Global | 30 msg/sec | `asyncio.sleep(2)` between channels |
| Per chat | 1 msg/sec | Sequential per channel |
| Per user (bot) | 20 msg/min | Not applicable (channels) |
| File size (photo) | 10 MB | Compress if needed |
| Photo dimensions | Max 10000x10000 | Pinterest pins 1000x1500 OK |

---

## Debugging Checklist

- [ ] `TELEGRAM_BOT_TOKEN` set in env (correct bot: @max_brain_chef_bot)
- [ ] Bot is admin in all 4 channels
- [ ] Channel IDs resolved via `bot.get_chat("@username")`
- [ ] `python-telegram-bot>=22.0` installed
- [ ] V2RayN running (proxy for API connectivity)
- [ ] DB writable: `D:/Portable_Soft/hermes/cache/tg_poster.db`

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Unauthorized` / `Invalid token` | Wrong bot token | Use @max_brain_chef_bot token (8656692973:...) |
| `Chat not found` | Wrong channel ID | Resolve via `bot.get_chat("@username")` |
| `Forbidden: bot is not a member` | Bot not admin | Add bot to channel as admin |
| `Timed out` | Proxy issue | Check V2RayN, use python-telegram-bot not raw HTTP |
| `Bad Request: The bot has already been closed` | Double close | Only close once in `finally` block |

---

## Image Generation Integration

```python
async def post_with_generated_image(bot: Bot, channel_id: int, post_data: dict):
    \"\"\"Generate image via Bing/Leonardo, then post\"\"\"
    # 1. Generate image (external script or API)
    image_path = await generate_pin_image(
        prompt=post_data["image_prompt"],
        style=post_data.get("style", "clean_modern"),
        output=f"assets/content_warehouse/images/{post_data['id']}.png"
    )
    
    # 2. Post with image
    return await post_to_channel(
        bot, channel_id, 
        post_data["text"], 
        image_path, 
        build_cta_keyboard(post_data["cta_url"], post_data["cta_text"])
    )
```

---

## Proxy Note (Critical)

**V2RayN Shadowsocks (`ss://...`) works with python-telegram-bot but NOT with raw `requests`/`urllib`.**

The library's `httpx` client properly routes through system proxy. Raw HTTP calls hang on `api.telegram.org`.

**Test connectivity:**
```bash
# This works (uses library internals)
python -c "
import asyncio
from telegram import Bot
bot = Bot(token='8656692973:...')
asyncio.run(bot.get_me())
"

# This HANGS (raw HTTP)
curl -x socks5://127.0.0.1:1080 https://api.telegram.org/bot8656692973:.../getMe
```