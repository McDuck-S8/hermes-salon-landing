# aiogram 3.29 Rich Messages — Verified Working (2026-06-22)

## Confirmed API

### Methods
- `bot.send_rich_message(chat_id, rich_message=InputRichMessage(...))` — send new
- `bot.edit_message_text(text=None, rich_message=InputRichMessage(...), chat_id=..., message_id=...)` — edit existing

### Type Hierarchy
```
InputRichMessage
  └── rich_message: RichMessage
        └── blocks: list[RichBlockUnion]
              ├── RichBlockParagraph(text=RichTextUnion)
              ├── RichBlockSectionHeading(text=RichTextUnion, size=int)  ← size REQUIRED
              ├── RichBlockTable(cells=list[list[RichBlockTableCell]], is_bordered=bool, is_striped=bool)
              ├── RichBlockDetails(summary=RichTextUnion, blocks=list[...], is_open=bool)
              ├── RichBlockDivider()
              ├── RichBlockList(items=list[RichBlockListItem])
              ├── RichBlockCollage(blocks=list[...])
              └── RichBlockThinking(text=RichTextUnion)

RichBlockTableCell
  ├── align: str        ← REQUIRED: "left" | "center" | "right"
  ├── valign: str       ← REQUIRED: "top" | "middle" | "bottom"
  ├── text: RichTextUnion
  ├── is_header: bool
  ├── colspan: int
  └── rowspan: int
```

### Validation Errors (pitfalls)
1. `RichBlockTableCell` without `align`/`valign` → `ValidationError: 2 validation errors`
2. `RichBlockSectionHeading` without `size` → `ValidationError: size required`

### Working Code: Salon Price Table
```python
from aiogram.types import (
    RichMessage, InputRichMessage,
    RichBlockTable, RichBlockTableCell, RichBlockSectionHeading,
    RichBlockDivider, RichBlockParagraph,
    RichTextBold,
)

def price_table(services):
    header = [
        RichBlockTableCell(text=[RichTextBold(text="Услуга")], align="left", valign="middle", is_header=True),
        RichBlockTableCell(text=[RichTextBold(text="Цена")], align="right", valign="middle", is_header=True),
    ]
    rows = [header]
    for svc in services:
        rows.append([
            RichBlockTableCell(text=f"{svc['name']}", align="left", valign="middle"),
            RichBlockTableCell(text=f"{svc['price']}₽", align="right", valign="middle"),
        ])
    return InputRichMessage(rich_message=RichMessage(blocks=[
        RichBlockSectionHeading(text="📋 Прайс", size=1),
        RichBlockTable(cells=rows, is_bordered=True, is_striped=True),
    ]))
```

### Integration Pattern (with fallback)
```python
try:
    from bot.rich import price_table
    rich = price_table(services)
    await cb.message.delete()
    await cb.message.answer(rich_message=rich, reply_markup=kb)
except Exception:
    await cb.message.edit_text("HTML fallback", reply_markup=kb, parse_mode="HTML")
```
