# 🎨 Fun Features for Salon Bot — Based on Telegram Bot API 10.1 (June 2026)

> **Research date**: June 22, 2026
> **Current bot**: @HotelCrimeaBot, aiogram 3.24, Python 3.11, SQLite
> **Target aiogram**: Upgrade to 3.29.0 for Bot API 10.1 support

---

## 📋 Summary of New Telegram Features (Feb–Jun 2026)

| API Version | Date | Key Features |
|-------------|------|-------------|
| 10.1 | Jun 11, 2026 | Rich Messages (`sendRichMessage`), draft streaming, guest queries |
| 10.0 | May 8, 2026 | Guest bots, bot-to-bot, streaming text, live photos, polls upgrade |
| 9.6 | Mar 31, 2026 | AI Editor, Mighty Polls, Live Photos, Bots Managed by Bots |
| 9.5 | Feb 9, 2026 | Colored bot buttons, Gift Crafting, custom emoji in buttons, bot avatar mgmt |

---

## 🚀 TOP 15 Fun Features to Add

### 1. 🎨 COLORED BOT BUTTONS (Priority: HIGH — Easy Win)
**API**: Bot API 9.5+ (`InlineKeyboardButton.style`)
**aiogram**: 3.24+ supports via raw API, 3.29+ typed support

```python
# New button styles: "primary", "danger", "success"
button = InlineKeyboardButton(
    text="✅ Подтвердить запись",
    callback_data="confirm_booking",
    # aiogram 3.29+ or raw API:
    # style="success"  # green button!
)
```

**Salon use cases**:
- 🟢 `success` style for "Подтвердить" (Confirm booking) — green = go!
- 🔴 `danger` for "Отменить запись" (Cancel booking) — red = warning
- 🔵 `primary` for "Записаться" (Book now) — blue = main action
- Apply to ALL keyboards: confirm, cancel, review submission

**Implementation**:
- `bot/keyboards.py`: Add `style` parameter to `confirm_kb()`, `booking_actions_kb()`
- If aiogram 3.24 doesn't have typed `style`, use `button.__dict__['style'] = 'danger'` or raw JSON
- Upgrade aiogram to 3.29 for proper typed support

---

### 2. ✨ RICH MESSAGES — Beautiful Service Cards (Priority: HIGH — Wow Factor)
**API**: Bot API 10.1 (`sendRichMessage`, `InputRichMessage`)
**aiogram**: 3.29+ (raw API calls until typed support)

```python
# Send rich service catalog with tables, headings, media
from aiogram import Bot

# Rich message with table of services
rich_content = [
    {"type": "heading", "text": "💇 Наши услуги", "level": 2},
    {"type": "text", "text": "Выберите процедуру из каталога:"},
    {"type": "table", "headers": ["Услуга", "Цена", "Длительность"],
     "rows": [
         ["Стрижка", "1500₽", "45 мин"],
         ["Окрашивание", "3500₽", "120 мин"],
         ["Маникюр", "2000₽", "60 мин"],
     ]},
    {"type": "details", "summary": "🎁 Акции этого месяца", 
     "content": "2=1 на все стрижки!"},
    {"type": "media", "url": "https://example.com/salon-interior.jpg"},
]

# Using raw API (aiogram 3.29+):
await bot(
    SendRichMessage(
        chat_id=msg.chat.id,
        content=rich_content,
    )
)
```

**Salon use cases**:
- 📊 Service catalog with price tables
- 🎁 Promotional blocks with collapsible details
- 📸 Before/After photo collages inline
- 🗺️ Map embeds showing salon location
- 💰 Pricing comparison tables

**Implementation**:
- New handler: `handlers/catalog.py` — rich service showcase
- Helper: `utils/rich_messages.py` — builder functions for common patterns
- Fallback: If API not available, use MarkdownV2 tables

---

### 3. 🎁 GIFT CRAFTING & SEND GIFTS (Priority: MEDIUM — Engagement)
**API**: Bot API 9.5+ (Gift Crafting), 9.0+ (`sendGift`)
**aiogram**: 3.24+ via raw API

```python
# Send a gift to a client after successful booking
await bot.send_gift(
    user_id=client_id,
    gift_id="unique_gift_id",  # or use star proceeds
    text="Спасибо за запись! 🎁 Вот подарок от нашего салона"
)

# Gift crafting: combine elements to create unique gifts
# (requires Premium features or stars)
```

**Salon use cases**:
- 🎉 Birthday gift: Send special emoji gift on client's birthday
- ⭐ Loyalty reward: Gift after N visits
- 🏆 Top client: Crafted exclusive gift for VIP
- 📅 Anniversary: 1-year booking anniversary gift

**Implementation**:
- DB field: `client.birthdate` for birthday tracking
- Cron job: `cron/birthday_gifts.py` — daily check for birthdays
- Stars balance: Use `sendGift` with star proceeds from Mini App payments

---

### 4. 🖼️ LIVE PHOTOS for Before/After (Priority: MEDIUM — Visual Impact)
**API**: Bot API 10.0 (`sendLivePhoto`, `InputMediaLivePhoto`)
**aiogram**: 3.29+ typed support

```python
# Send live photo of salon work
await bot.send_live_photo(
    chat_id=client_chat_id,
    photo=InputMediaLivePhoto(
        static_photo=InputFile("before.jpg"),
        video=InputFile("after_reveal.mp4"),
    ),
    caption="✨ До и После — результат работы мастера Анны"
)
```

**Salon use cases**:
- 📸 Before/After transformations (static photo → animated reveal)
- 🎬 Portfolio showcase: Masters' best work
- 🏠 Salon tour: Static image → video walkthrough
- 💇 Service preview: What to expect

**Implementation**:
- Master panel: Upload before/after live photos per service
- DB table: `portfolio` with live_photo static + video paths
- Client menu: "📸 Портфолио" button → gallery of live photos

---

### 5. 📊 ENHANCED POLLS — "Which Service Next?" (Priority: MEDIUM — Fun)
**API**: Bot API 10.0/10.1 (Mighty Polls, limits, statistics, revoting)
**aiogram**: 3.29+ typed support

```python
# Create poll with country limits (Russia only!)
poll = await bot.send_poll(
    chat_id=channel_id,
    question="Какую услугу добавить в салон? 💇",
    options=["Ногтевой сервис", "Ламинирование бровей", "SPA-процедуры", "Детские стрижки"],
    is_anonymous=False,
    # New fields:
    members_only=True,        # Only salon subscribers can vote
    country_codes=["RU", "UA"],  # CIS clients only
    allows_revoting=True,     # Let people change their mind
)
```

**Salon use cases**:
- 🗳️ "What service should we add?" — client voting
- 🏆 "Best Master of the Month" — member-only voting
- 📈 Service popularity tracking via poll statistics
- 🎯 Regional promotions (country-code limited polls)

**Implementation**:
- Admin command: `/poll "question" option1 option2`
- Channel: Post polls to salon channel for engagement
- Track statistics: Use poll statistics endpoint for analytics

---

### 6. 💬 STREAMING TEXT — Live Booking Status (Priority: LOW-MEDIUM)
**API**: Bot API 10.0 (`sendMessageDraft`), 10.1 (`sendRichMessageDraft`)
**aiogram**: 3.29+ raw API

```python
# Stream booking confirmation as it's being processed
draft_msg = await bot.send_message_draft(
    chat_id=client_chat_id,
    text="⏳ Проверяем расписание мастера Анны..."
)
# Update as processing continues
await bot.edit_message_text(
    chat_id=client_chat_id,
    message_id=draft_msg.message_id,
    text="✅ Мастер Анна свободна!\n📝 Создаём запись..."
)
# Final rich message
await bot.edit_message_text(
    chat_id=client_chat_id,
    message_id=draft_msg.message_id,
    text="✅ Запись создана!\n💇 Стрижка\n👩‍🎨 Анна\n📅 Завтра 15:00"
)
```

**Salon use cases**:
- ⏳ Real-time booking processing feedback
- 🤖 AI concierge: Stream style recommendations
- 📊 Live availability check results

---

### 7. 🤖 GUEST BOT — "Salon Assistant in Any Chat" (Priority: MEDIUM — Innovation)
**API**: Bot API 10.0 (Guest mode: `answerGuestQuery`, `supports_guest_queries`)
**aiogram**: 3.29+ raw API

```python
# Bot can respond when mentioned @HotelCrimeaBot in ANY chat
@router.message(F.via_bot)
async def guest_query(msg: Message):
    # User mentioned @HotelCrimeaBot in a group chat
    query = msg.text
    if "запись" in query.lower():
        # Help book directly from the group chat
        await bot.answer_guest_query(
            guest_query_id=msg.guest_query_id,
            result=InlineQueryResultArticle(
                title="📅 Записаться в салон",
                description="Открыть форму записи",
                reply_message_content=InputTextMessageContent(
                    message_text="✨ Откройте /start для записи"
                )
            )
        )
```

**Salon use cases**:
- 👥 Group chat: Friends discuss salon, bot offers to book
- 📱 Channel comments: Bot responds to "How to book?" questions
- 🏪 Business chat: Auto-respond when salon is mentioned

**Implementation**:
- Handle `guest_message` updates
- Parse intent: booking, price inquiry, location
- Respond with inline results linking back to bot

---

### 8. 📍 MINI APP GEOLOCATION — "Find Nearest Salon" (Priority: MEDIUM)
**API**: Mini Apps — Geolocation Access (Bot API 9.0+)
**Frontend**: JavaScript `Telegram.WebApp.LocationManager`

```javascript
// In Mini App (webapp/index.html)
const tg = window.Telegram.WebApp;

// Request user location
tg.LocationManager.getLocation((location) => {
    // location.latitude, location.longitude
    fetch('/api/nearest-salon', {
        method: 'POST',
        body: JSON.stringify({ lat: location.latitude, lng: location.longitude })
    });
});
```

**Salon use cases**:
- 🗺️ "Show nearest salon" with map
- 📍 Distance-based pricing ("Far? Get discount!")
- 🧭 Turn-by-turn directions from user location
- 🏪 Multi-location: Show nearest branch

---

### 9. 💾 DEVICE STORAGE — Offline Booking Cache (Priority: LOW)
**API**: Mini Apps — `DeviceStorage`, `SecureStorage` (Bot API 9.0+)
**Frontend**: JavaScript API

```javascript
// Save booking draft locally
Telegram.WebApp.DeviceStorage.setItem('draft_booking', JSON.stringify({
    service: 'Стрижка',
    master: 'Анна',
    date: '2026-06-23'
}));

// Load on next visit
const draft = JSON.parse(Telegram.WebApp.DeviceStorage.getItem('draft_booking'));
```

**Salon use cases**:
- 💾 Save booking draft if user closes Mini App
- 📱 Remember preferred service/master
- 🔐 SecureStorage for payment tokens

---

### 10. ⭐ PAID MEDIA — Premium Content (Priority: LOW — Monetization)
**API**: Bot API 8.0+ (`sendPaidMedia`, `InputPaidMedia`)
**aiogram**: 3.24+ raw API

```python
# Send premium tutorial content
await bot.send_paid_media(
    chat_id=client_id,
    star_count=50,  # 50 Telegram Stars
    media=[
        InputPaidMediaPhoto(photo=InputFile("tutorial_step1.jpg")),
        InputPaidMediaPhoto(photo=InputFile("tutorial_step2.jpg")),
    ],
    caption="💅 Мастер-класс по гель-лаку (50⭐)"
)
```

**Salon use cases**:
- 💅 Paid masterclasses for clients
- 📸 Premium portfolio content
- 🎓 Hair care tips video series
- 💰 Revenue stream via Telegram Stars

---

### 11. 🏷️ CUSTOM EMOJI IN BUTTONS (Priority: HIGH — Easy Branding)
**API**: Bot API 9.5+ (`icon_custom_emoji_id` on buttons)
**aiogram**: 3.24+ raw API, 3.29+ typed

```python
# Button with custom salon emoji
button = InlineKeyboardButton(
    text="Записаться",
    callback_data="book_start",
    icon_custom_emoji_id="5368324170671202286",  # salon scissor emoji
)
```

**Salon use cases**:
- 🏪 Brand emoji on main menu buttons
- 💅 Service-specific icons (nail emoji for manicure)
- ⭐ VIP badge for premium clients
- 🎨 Seasonal emoji (🌸 spring, ❄️ winter promotions)

**Implementation**:
- Create custom emoji set via @EmojiBot
- Map service_id → custom_emoji_id in DB
- Add to all keyboard builders

---

### 12. 🤖 BOT-TO-BOT — AI Style Advisor (Priority: LOW-MEDIUM — Advanced)
**API**: Bot API 10.0 (Bot-to-Bot communication)
**aiogram**: 3.29+ raw API

```python
# Salon bot asks AI bot for style recommendation
@router.callback_query(F.data.startswith("ai_style_"))
async def get_ai_recommendation(cb: CallbackQuery):
    # Send message to AI style advisor bot
    ai_response = await bot.send_message(
        chat_id="@StyleAdvisorBot",
        text=f"Предложи причёску для клиента: {user_prefs}"
    )
    # Forward AI response to client
    await cb.message.edit_text(ai_response.text)
```

**Salon use cases**:
- 💇 AI-powered hairstyle recommendations
- 🎨 Color matching suggestions
- 📸 Virtual try-on integration
- 🧴 Product recommendations

---

### 13. 📋 CHECKLISTS — Aftercare Instructions (Priority: MEDIUM)
**API**: Bot API 10.0+ (`Checklist`, `InputChecklist`)
**aiogram**: 3.29+ typed support

```python
# Send aftercare checklist after service
from aiogram.types import Checklist, InputChecklist, InputChecklistTask

await bot.send_checklist(
    chat_id=client_id,
    checklist=InputChecklist(
        title="После окрашивания 💇‍♀️",
        tasks=[
            InputChecklistTask(text="Не мыть голову 48 часов"),
            InputChecklistTask(text="Использовать специальный шампунь"),
            InputChecklistTask(text="Наносить кондиционер после каждого мытья"),
            InputChecklistTask(text="Избегать прямых солнечных лучей"),
        ]
    ),
    caption="📋 Ваш план ухода после окрашивания"
)
```

**Salon use cases**:
- 💇 Aftercare instructions (hair, nails, skin)
- 📅 Pre-visit preparation checklist
- 🏠 Home care routine checklist
- ✅ Booking preparation checklist

---

### 14. 🎭 EMOJI STATUS FROM MINI APP (Priority: LOW — Fun Branding)
**API**: Mini Apps — Emoji Status API (Bot API 9.0+)
**Frontend**: JavaScript

```javascript
// In Mini App — let user set salon-themed emoji status
Telegram.WebApp.requestEmojiStatusAccess((granted) => {
    if (granted) {
        // User granted permission
        // Bot can later set: 💇‍♀️ after booking
    }
});
```

**Salon use cases**:
- 💇‍♀️ Set "hairdresser" emoji after booking
- 💅 "Nail salon" emoji after manicure
- 🎉 Birthday: Set party emoji on client's birthday
- ⭐ VIP: Crown emoji for top clients

---

### 15. 📱 SILENT SCHEDULED MESSAGES — Smart Reminders (Priority: HIGH)
**API**: Bot API 10.0 (Silent scheduled messages)
**aiogram**: 3.24+ via `disable_notification`

```python
# Schedule silent reminder (no sound, appears in chat history)
from datetime import datetime, timedelta

reminder_time = booking_date - timedelta(hours=2)

await bot.send_message(
    chat_id=client_id,
    text="⏰ Напоминание:您的 запись через 2 часа!\n💇 Стрижка с Анной в 15:00",
    disable_notification=True,  # Silent!
    # Or use scheduled delivery:
    # schedule_date=reminder_time,
)
```

**Salon use cases**:
- ⏰ Silent pre-appointment reminders (2h before)
- 📅 Weekly schedule summary (every Monday 9:00)
- 🎂 Birthday greetings (silent, not intrusive)
- 📊 Monthly statistics for admin (silent)

---

## 📦 Implementation Priority Matrix

### Phase 1 — Quick Wins (1-2 days)
| Feature | Difficulty | Impact | Files to Touch |
|---------|-----------|--------|----------------|
| Colored buttons | ⭐ Easy | 🔥 High | `keyboards.py` |
| Custom emoji in buttons | ⭐ Easy | 🔥 High | `keyboards.py` + DB |
| Silent reminders | ⭐ Easy | 🔥 High | `cron/reminders.py` |
| Upgrade aiogram 3.24→3.29 | ⭐ Easy | 🔥 High | `requirements.txt` |

### Phase 2 — Medium (3-5 days)
| Feature | Difficulty | Impact | Files to Touch |
|---------|-----------|--------|----------------|
| Rich Messages (service catalog) | ⭐⭐ Medium | 🔥 High | New `handlers/catalog.py` |
| Enhanced Polls (voting) | ⭐⭐ Medium | ⭐ Medium | `handlers/admin.py` |
| Checklist aftercare | ⭐⭐ Medium | ⭐ Medium | New `handlers/aftercare.py` |
| Live Photos portfolio | ⭐⭐ Medium | ⭐ Medium | `handlers/master.py` + DB |

### Phase 3 — Advanced (1-2 weeks)
| Feature | Difficulty | Impact | Files to Touch |
|---------|-----------|--------|----------------|
| Mini App Geolocation | ⭐⭐⭐ Hard | 🔥 High | `webapp/index.html` + backend |
| DeviceStorage for drafts | ⭐⭐⭐ Hard | ⭐ Medium | `webapp/index.html` |
| Guest Bot mode | ⭐⭐⭐ Hard | ⭐ Medium | New handler + API |
| AI Style Advisor (bot-to-bot) | ⭐⭐⭐ Hard | ⭐ Medium | New integration |

### Phase 4 — Monetization (Ongoing)
| Feature | Difficulty | Impact | Files to Touch |
|---------|-----------|--------|----------------|
| Paid Media content | ⭐⭐ Medium | 💰 Revenue | New `handlers/premium.py` |
| Gift Crafting/VIP | ⭐⭐⭐ Hard | 💰 Revenue | DB + cron + payments |
| Emoji Status rewards | ⭐ Easy | ⭐ Low | Mini App + cron |

---

## 🔧 Dependencies to Add/Upgrade

```txt
# requirements.txt updates
aiogram>=3.29.0          # Bot API 10.1 support (currently 3.24)
aiohttp>=3.10.0          # Latest for proxy support
```

---

## 📊 Key API Methods Reference

| Method | API Version | Purpose |
|--------|-------------|---------|
| `sendRichMessage` | 10.1 | Rich formatted messages |
| `sendRichMessageDraft` | 10.1 | Streaming rich messages |
| `answerGuestQuery` | 10.0 | Guest bot responses |
| `sendLivePhoto` | 10.0 | Live photos (before/after) |
| `sendGift` | 9.0 | Send gifts to users |
| `sendPaidMedia` | 8.0 | Premium paid content |
| `sendPoll` (enhanced) | 10.0 | Polls with limits/stats |
| `InlineKeyboardButton.style` | 9.5 | Colored buttons |
| `InlineKeyboardButton.icon_custom_emoji_id` | 9.5 | Custom emoji icons |
| `sendMessageDraft` | 10.0 | Draft/streaming messages |
| `setMyProfilePhoto` | 9.5 | Bot avatar management |

---

## 🎯 Recommended First Steps

1. **Upgrade aiogram** to 3.29.0 (`pip install aiogram>=3.29.0`)
2. **Add colored buttons** to all confirmation/cancel keyboards
3. **Add silent reminders** to existing cron jobs
4. **Build rich service catalog** with tables and media
5. **Add checklist aftercare** for completed bookings
6. **Enable Mini App geolocation** for salon finder

---

*Generated by Hermes Agent — Research based on Telegram Bot API 10.1 changelog*
