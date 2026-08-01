# Telegram Rich Posting — Integration Notes (2026-07-17)

## Channels & Bot (Verified Working)

| Channel | Username | Chat ID | Title |
|---------|----------|---------|-------|
| MAX BRAIN CHEF OFFICIAL | `@max_brain_chef_official` | `-1003777013964` | MAX BRAIN \| AI & Agents |
| AI FRONTIER YOU | `@ai_frontier_you` | `-1003705792421` | AI: Фронтир \| Агентные системы |
| MAX BRAIN CHEF AI | `@max_brain_chef_ai` | `-1003882833000` | MAX BRAIN \| AI & Agents |
| NEURO KITCHEN AI | `@neuro_kitchen_ai` | `-1003525498743` | НейроКухня \| AI Recipes |

**Bot:** `@max_brain_chef_bot` (ID: 8656692973)
**Token:** `8656692973:AAG7ooiscNBGaYTd5wLq5-FFdKRHHDc4ItM` (stored in env TELEGRAM_BOT_TOKEN)

## Posting Script: `scripts/telegram_poster.py`

Created in this session. Features:
- **Rich HTML formatting** (bold, italic, blockquote, code blocks, links)
- **Inline keyboards** per post type + global footer buttons
- **5 content categories** with weighted selection: ai_news (35%), ai_tool (25%), code_tip (15%), analytics (15%), motivation (10%)
- **SQLite tracking** (posts, schedule, metrics)
- **Rate limiting** (2s between channels)
- **CLI commands**: `cycle`, `status`, `gen`, `test`, `sched-add`, `sched-list`

### Post Templates (examples)

```html
<!-- ai_tool -->
🛠 <b>Инструмент дня:</b> <a href="https://fal.ai">Fal.ai</a>

Запускай Flux, SDXL, Whisper, Llama на серверлесс GPU. Платишь за секунды.

✨ <b>Фишки:</b> Flux/SDXL/Whisper, serverless, OpenAI-совместимый API

👉 <a href="https://fal.ai">Попробовать бесплатно</a>
```

```html
<!-- code_tip -->
💻 <b>Сниппет:</b> Async HTTP клиент с retry

<pre><code>import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def fetch(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=30)
        r.raise_for_status()
        return r.json()</code></pre>

📝 Экспоненциальный бэкофф + автоматический ретрай. Экономит нервы при флакинге API.
```

### Inline Keyboard Structure

```python
# Category-specific button (row 1)
InlineKeyboardMarkup([[
    InlineKeyboardButton("🚀 Попробовать", url=tool_url)
]])

# Global footer buttons (rows 2-3)
InlineKeyboardMarkup([
    [InlineKeyboardButton("📢 Все каналы", url="https://t.me/max_brain_chef_official"),
     InlineKeyboardButton("🤖 Бот", url="https://t.me/max_brain_chef_bot")],
    [InlineKeyboardButton("💬 Чат", url="https://t.me/+nVpNjeTXzXE5YTRi"),
     InlineKeyboardButton("🔥 Топ", callback_data="top_posts")]
])
```

## Integration with Ghost-Surfer

Add to `posting.py`:
```python
class TelegramPoster:
    """Rich Telegram channel poster using python-telegram-bot v22."""
    
    def __init__(self, bot_token: str, channels: dict[str, int]):
        self.bot = Bot(token=bot_token)
        self.channels = channels  # {"channel_key": chat_id}
    
    async def post(self, channel_key: str, html: str, keyboard: InlineKeyboardMarkup = None):
        chat_id = self.channels[channel_key]
        return await self.bot.send_message(
            chat_id=chat_id,
            text=html,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=False,
        )
```

## Cron Schedule (MSK / UTC+3)

```
09:00, 12:00, 15:00, 18:00, 21:00  →  5 posts/day × 4 channels = 20 posts/day
```

## Pitfalls & Fixes

| Issue | Fix |
|-------|-----|
| `Bot` has no `session` attr | Use `await bot.close()` not `bot.session.close()` |
| SSL timeout to api.telegram.org | Use proxy/V2RayN or increase timeout to 60s |
| Channel not found | Bot must be **admin** in channel; use `getChat` to verify |
| HTML parse errors | Escape `<`, `>`, `&` in user content; use `html.escape()` |
| Rate limit (429) | `await asyncio.sleep(2)` between channels; exponential backoff on retry |

## Channel Marketplace Research (User Request)

**Goal:** Find where US channels sell for $5+ in crypto.

**Targets to investigate:**
- Fragment (Telegram official) — premium usernames, some channels
- Telemetr.io / Telemetr.me — analytics + marketplace
- P2P forums: BlackHatWorld, EpicNPC, Telegram groups
- Direct outreach via channel admins (check "Advertise" links)

**Status:** Not yet started. Next session task.