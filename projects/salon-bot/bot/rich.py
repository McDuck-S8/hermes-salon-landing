"""
Rich Messages helpers for salon-bot.
Uses aiogram 3.29+ send_rich_message / edit_message_text(rich_message=).
Falls back gracefully when RichMessage types are not available.
"""

try:
    from aiogram.types import (
        RichMessage, InputRichMessage,
        RichBlockParagraph, RichBlockTable, RichBlockTableCell,
        RichBlockDetails, RichBlockSectionHeading,
        RichBlockDivider,
        RichTextBold, RichTextItalic,
        RichBlockCaption,
    )
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Sentinel for callers to check
available = HAS_RICH


def price_table(services: list) -> "InputRichMessage | None":
    """Build a rich price table from service list. Returns None if unavailable."""
    if not HAS_RICH:
        return None
    header = [
        RichBlockTableCell(text=[RichTextBold(text="Услуга")], align="left", valign="middle", is_header=True),
        RichBlockTableCell(text=[RichTextBold(text="Время")], align="center", valign="middle", is_header=True),
        RichBlockTableCell(text=[RichTextBold(text="Цена")], align="right", valign="middle", is_header=True),
    ]
    rows = [header]
    for svc in services:
        emoji = svc.get("emoji", "💇")
        rows.append([
            RichBlockTableCell(text=f"{emoji} {svc['name']}", align="left", valign="middle"),
            RichBlockTableCell(text=f"{svc.get('duration_min', 60)} мин", align="center", valign="middle"),
            RichBlockTableCell(text=f"{svc['price']}₽", align="right", valign="middle"),
        ])

    table = RichBlockTable(cells=rows, is_bordered=True, is_striped=True)

    blocks = [
        RichBlockSectionHeading(text="📋 Прайс-лист салона", size=1),
        RichBlockDivider(),
        table,
        RichBlockDivider(),
        RichBlockParagraph(text="💡 Нажмите «Записаться», чтобы забронировать место"),
    ]
    return InputRichMessage(rich_message=RichMessage(blocks=blocks))


def master_profile(master: dict, services: list) -> "InputRichMessage | None":
    """Build a rich master profile card."""
    if not HAS_RICH:
        return None
    svc_names = ", ".join(s["name"] for s in services) if services else "—"
    rows = [
        [
            RichBlockTableCell(text=[RichTextBold(text="Параметр")], align="left", valign="middle", is_header=True),
            RichBlockTableCell(text=[RichTextBold(text="Значение")], align="left", valign="middle", is_header=True),
        ],
        [
            RichBlockTableCell(text="Имя", align="left", valign="middle"),
            RichBlockTableCell(text=master.get("name", "—"), align="left", valign="middle"),
        ],
        [
            RichBlockTableCell(text="Услуги", align="left", valign="middle"),
            RichBlockTableCell(text=svc_names, align="left", valign="middle"),
        ],
        [
            RichBlockTableCell(text="Стаж", align="left", valign="middle"),
            RichBlockTableCell(text=f"{master.get('experience_years', 1)} лет", align="left", valign="middle"),
        ],
    ]
    table = RichBlockTable(cells=rows, is_bordered=True, is_striped=True)

    blocks = [
        RichBlockSectionHeading(text=f"👩‍🎨 {master.get('name', 'Мастер')}", size=1),
        table,
    ]
    return InputRichMessage(rich_message=RichMessage(blocks=blocks))


def booking_summary(data: dict, ai_text: str = "") -> "InputRichMessage | None":
    """Build a rich booking confirmation card."""
    if not HAS_RICH:
        return None
    rows = [
        [
            RichBlockTableCell(text=[RichTextBold(text="Поле")], align="left", valign="middle", is_header=True),
            RichBlockTableCell(text=[RichTextBold(text="Деталь")], align="left", valign="middle", is_header=True),
        ],
        [
            RichBlockTableCell(text="Услуга", align="left", valign="middle"),
            RichBlockTableCell(text=f"{data.get('service_emoji', '💇')} {data.get('service_name', '?')}", align="left", valign="middle"),
        ],
        [
            RichBlockTableCell(text="Мастер", align="left", valign="middle"),
            RichBlockTableCell(text=data.get("master_name", "?"), align="left", valign="middle"),
        ],
        [
            RichBlockTableCell(text="Дата", align="left", valign="middle"),
            RichBlockTableCell(text=data.get("booking_date", "?"), align="left", valign="middle"),
        ],
        [
            RichBlockTableCell(text="Время", align="left", valign="middle"),
            RichBlockTableCell(text=data.get("chosen_time", "?"), align="left", valign="middle"),
        ],
        [
            RichBlockTableCell(text="Стоимость", align="left", valign="middle"),
            RichBlockTableCell(text=f"{data.get('service_price', 0)}₽", align="left", valign="middle"),
        ],
    ]
    table = RichBlockTable(cells=rows, is_bordered=True, is_striped=True)

    blocks = [
        RichBlockSectionHeading(text="📋 Подтверждение записи", size=1),
        table,
    ]
    if ai_text:
        blocks.append(RichBlockDivider())
        blocks.append(RichBlockDetails(
            summary="💡 Рекомендация AI",
            blocks=[RichBlockParagraph(text=ai_text)],
        ))

    return InputRichMessage(rich_message=RichMessage(blocks=blocks))


def daily_special_card(title: str, description: str, promo: str) -> "InputRichMessage | None":
    """Build a rich daily special card with collapsible details."""
    if not HAS_RICH:
        return None
    blocks = [
        RichBlockSectionHeading(text=f"⭐ {title}", size=1),
        RichBlockDivider(),
        RichBlockParagraph(text=promo),
        RichBlockDetails(
            summary="Подробнее о предложении",
            blocks=[RichBlockParagraph(text=description)],
        ),
    ]
    return InputRichMessage(rich_message=RichMessage(blocks=blocks))
