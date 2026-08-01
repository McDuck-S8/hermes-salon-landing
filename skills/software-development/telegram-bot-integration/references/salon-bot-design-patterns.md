# Salon Bot Design Patterns (2025-2026)

Research from real salon bots: Fashion Brand Studio (t.me/weFBS_bot), Botman.pro cases, Timeweb guide, Fuselab chatbot UX.

## Menu Structure
- 4-5 buttons max in main menu
- Every button = emoji + short text
- "🏠 Меню" or "⬅️ Назад" on EVERY screen

## Booking Flow (longest chain)
Master → Photo+description → Service → Date → Time → Confirmation
Each step: inline keyboard, not free text.

## Message Formatting
```
━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Дата: 15 января
⏰ Время: 14:00
💇 Стрижка женская
👩‍🎨 Анна
━━━━━━━━━━━━━━━━━━━━━━━━━
```
- Divider lines for visual blocks
- Bold for labels, plain for values
- Emoji prefix for each field

## Key Features for Beauty Salon Bots
1. Silent reminders (24h + 1h before) via `disable_notification=True`
2. Photo gallery with category navigation (delete+send_photo pattern)
3. Virtual loyalty card with levels
4. Daily special offer (rotating by day)
5. Dice game → discount reward
6. Quiz about hair/nails → brand engagement
7. Forward-to-admin for live chat

## What NOT to Do
- No template/greeting responses — user calls them "заглушки"
- No long text walls — break into visual blocks
- No buttons without handlers — silent "not handled" failures
- No Markdown parse_mode on dynamic content — use HTML or none

## Colored Buttons (Bot API 10.1+)
- `style="primary"` — blue, for main actions (book, share)
- `style="success"` — green, for confirm
- `style="danger"` — red, for destructive actions
