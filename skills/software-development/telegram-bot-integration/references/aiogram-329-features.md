# aiogram 3.29+ Features (Bot API 9.5–10.1)

## Colored Bot Buttons (Bot API 9.5)

`InlineKeyboardButton` has a `style` parameter: `"primary"`, `"danger"`, `"success"`.

```python
from aiogram.types import InlineKeyboardButton

InlineKeyboardButton(text="✅ Подтвердить", callback_data="ok", style="success")
InlineKeyboardButton(text="❌ Отменить", callback_data="del", style="danger")
InlineKeyboardButton(text="📅 Записаться", callback_data="book", style="primary")
```

## Rich Messages (Bot API 10.1) — FULL SUPPORT in aiogram 3.29

**aiogram 3.29 has typed wrappers for ALL Rich Message types.** Verified working 2026-06-22. No raw HTTP needed.

### Methods:
- `bot.send_rich_message(chat_id, rich_message=InputRichMessage(...))` 
- `bot.edit_message_text(rich_message=..., chat_id=..., message_id=...)`

### Block types:
```python
RichMessage(blocks=[...])
RichBlockParagraph(text=[...])
RichBlockSectionHeading(text=[...], size=1)   # size is REQUIRED
RichBlockTable(cells=[[...]], is_bordered=True, is_striped=True)
RichBlockTableCell(text=[...], align="left", valign="middle", is_header=True)  # align+valign REQUIRED
RichBlockList(items=[RichBlockListItem(label="...", blocks=[...])])
RichBlockDetails(summary=[...], blocks=[...], is_open=False)
RichBlockDivider()
RichBlockCollage / Slideshow / Thinking / Photo / Video / Map
```

### CRITICAL: RichBlockTableCell requires align AND valign
```python
# WRONG — ValidationError: 2 missing required fields
RichBlockTableCell(text="Hello", is_header=True)

# CORRECT
RichBlockTableCell(text="Hello", align="left", valign="middle", is_header=True)
# align: "left" | "center" | "right"
# valign: "top" | "middle" | "bottom"
```

### CRITICAL: RichBlockSectionHeading requires size
```python
# WRONG — ValidationError: size required
RichBlockSectionHeading(text="Title")

# CORRECT
RichBlockSectionHeading(text="Title", size=1)
```

### RichText inline types:
```python
RichTextBold / Italic / Code / Spoiler / Url / Strikethrough / Underline / CustomEmoji
```

### text field: str OR list[RichText]
```python
# Simple string
RichBlockTableCell(text="Hello", align="left", valign="middle")

# Formatted list
RichBlockTableCell(text=[RichTextBold(text="Bold")], align="left", valign="middle")

# Mixed
RichBlockDetails(summary="Click me", blocks=[...])  # summary=str is fine
```

### Working pattern:
```python
rich = InputRichMessage(rich_message=RichMessage(blocks=[
    RichBlockSectionHeading(text=[RichTextBold(text="Прайс-лист")], size=1),
    RichBlockTable(cells=[header_row, ...], is_bordered=True, is_striped=True),
]))
await msg.answer(rich_message=rich)
```

### Key: Rich messages are NEW messages. Cannot edit_text → rich. Always delete() first.

### Fallback pattern:
```python
try:
    await cb.message.delete()
    await cb.message.answer(rich_message=rich, reply_markup=kb)
except Exception:
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
```

## Draft Streaming / Guest Bots / Live Photos / Polls

See Bot API 10.0–10.1 changelog for details.
