# Telegram Bot API 10.x Features — Availability in aiogram 3.29

Researched: 2026-06-22. Updated: 2026-06-22 (post-session).
Source: https://core.telegram.org/bots/api-changelog

## Bot API 10.1 (June 11, 2026) — Rich Messages

**aiogram 3.29 support: TYPES exist, but no helper wrappers yet**

### New Classes (text formatting)
- `RichText` — base formatted text
- `RichTextBold` — bold
- `RichTextItalic` — italic
- `RichTextCode` — monospaced
- `RichTextSpoiler` — spoiler
- `RichTextCustomEmoji` — custom emoji

### New Classes (block elements)
- `RichBlockParagraph` — paragraph
- `RichBlockList` — ordered/unordered list
- `RichBlockTable` — table with `RichBlockTableCell`
- `RichBlockCollage` — photo collage
- `RichBlockSlideshow` — slideshow
- `RichBlockThinking` — "AI thinking" animation
- `RichBlockCaption` — caption for blocks

### New Methods
```python
# Send rich message (direct HTTP — aiogram doesn't have wrapper yet)
await bot.send_rich_message(
    chat_id=chat_id,
    rich_message=InputRichMessage(blocks=[...])
)

# Stream partial rich messages (30s preview)
await bot.send_rich_message_draft(
    chat_id=chat_id,
    rich_message=InputRichMessage(blocks=[...])
)

# Edit existing message with rich content
await bot.edit_message_text(
    rich_message=InputRichMessage(blocks=[...]),
    message_id=msg_id,
    chat_id=chat_id
)
```

### Workaround: direct HTTP when aiogram wrapper missing
```python
import aiohttp, json

async def send_rich(bot_token, chat_id, blocks):
    url = f"https://api.telegram.org/bot{bot_token}/sendRichMessage"
    payload = {
        "chat_id": chat_id,
        "rich_message": {"blocks": blocks}
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()

# Example: table with services
blocks = [
    {
        "type": "paragraph",
        "text": [{"type": "bold", "text": "Прайс-лист салона"}]
    },
    {
        "type": "table",
        "columns": [
            {"header": True, "text": "Услуга"},
            {"header": True, "text": "Цена"}
        ],
        "rows": [
            [{"text": "Стрижка"}, {"text": "800₽"}],
            [{"text": "Окрашивание"}, {"text": "2500₽"}],
            [{"text": "Маникюр"}, {"text": "1200₽"}]
        ]
    }
]
```

### Practical for salon bot
1. **Service catalog** — table with prices instead of hand-drawn ASCII
2. **Collapsible details** — expand descriptions of procedures
3. **Thinking animation** — while AI picks recommendation
4. **Collage** — gallery of work photos
5. **Streaming** — answer appears as AI generates it

## Bot API 10.0 (May 8, 2026) — Guest Mode + Live Photos + Bot-to-Bot

| Feature | aiogram 3.29 | Notes |
|---------|-------------|-------|
| Guest Mode | NO | Not in aiogram yet |
| Live Photos | NO | Not in aiogram yet |
| Bot-to-Bot | NO | Not in aiogram yet |
| Poll Media | YES | sendPoll has media param |
| sendMessageDraft | YES | Bot.send_message_draft() |
| Chat Reactions | YES | Bot.set_message_reaction() |
| Colored Buttons | YES | InlineKeyboardButton(style="primary"/"success"/"danger") |

## Bot API 9.4 (Feb 9, 2026) — Custom Keyboard Styling
```python
from aiogram.types import InlineKeyboardButton
InlineKeyboardButton(text="✅ OK", callback_data="ok", style="success")     # green
InlineKeyboardButton(text="❌ No", callback_data="no", style="danger")      # red
InlineKeyboardButton(text="📅 Book", callback_data="book", style="primary") # blue
```

## Confirmed Available in aiogram 3.29
```python
await bot.send_dice(chat_id, emoji=DiceEmoji.DICE)
await bot.set_message_reaction(chat_id, msg_id, reaction=[...])
await bot.post_story(chat_id, content=...)
await bot.send_media_group(chat_id, media=[...])
await bot.send_message_draft(chat_id, text="typing...")
# Colored buttons
InlineKeyboardButton(text="Button", callback_data="data", style="primary")
```

## Global Error Recovery Pattern (NEW)
When user clicks button on a photo message → `edit_text` crashes. Global handler:
```python
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ErrorEvent

@dp.error()
async def handle_errors(event: ErrorEvent):
    exc = event.exception
    if not isinstance(exc, TelegramBadRequest):
        return
    if "there is no text in the message to edit" not in str(exc):
        return
    cb = event.update.callback_query
    if cb:
        await cb.answer()
        try:
            await cb.message.answer("🏠 Меню:", reply_markup=main_menu_kb())
        except Exception:
            pass
```
This catches ALL handlers that might hit photo messages — better than per-handler try/except.
