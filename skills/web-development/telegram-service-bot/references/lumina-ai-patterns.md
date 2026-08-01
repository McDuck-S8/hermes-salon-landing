# Lumina AI — Personal Beauty Concierge Patterns

AI-like features for service booking bots. From salon-bot implementation (2026-06-22).

## Module Structure

`bot/lumina.py` — self-contained AI-like module, no external LLM dependencies.

### Smart Greetings (time-of-day aware)
```python
AI_GREETINGS = {
    "morning": ["☀️ Доброе утро, {name}! ..."],
    "afternoon": ["🌸 Добрый день, {name}! ..."],
    "evening": ["🌙 Добрый вечер, {name}! ..."],
}
```
Pattern: random choice from category, format with client name. Feels personalized without LLM.

### Smart Booking Reasons
```python
SMART_BOOKING_REASONS = [
    "Я подобрала именно этот слот, потому что {master} обычно делает {service} в это время",
    "{time} — идеальное время: салон не будет переполнен",
]
```
Pattern: After user picks time slot, show a personalized "why this slot" message before confirmation. Increases perceived intelligence.

### Aftercare Reminders (Day 1/3/7/14)
```python
AFTERCARE = {
    "hair_color": {
        1: "🎨 День 1: моем только прохладной водой...",
        7: "🎨 Неделя: скинь фото — оценю как смывается цвет",
    },
    "hair_cut": { 1: "...", 7: "..." },
    "manicure": { 1: "...", 7: "..." },
}
```
Pattern: Cron job checks completed bookings, sends aftercare tips on specific days post-visit. Maps `service.category` → aftercare messages. Silent (`disable_notification=True`).

Integration in cron:
```python
async def send_aftercare():
    # Find completed bookings
    # Calculate days_since = (today - booking_date).days
    # Get aftercare = get_aftercare(category, days_since)
    # Send if aftercare exists for that day
```

### Photo Analysis → Service Suggestions
```python
PHOTO_SERVICES = [
    ("Стрижка каскадом", "Уход кератиновый"),
    ("Окрашивание мелирование", "Маска восстанавливающая"),
]
def suggest_from_photo():
    service, treatment = random.choice(PHOTO_SERVICES)
    return template.format(service=service, treatment=treatment)
```
Pattern: User sends photo → bot "analyzes" → suggests 2 services. For real implementation, integrate vision API (GPT-4V, Claude Vision).

Handler:
```python
@router.message(F.photo)
async def analyze_photo(msg: Message):
    suggestion = suggest_from_photo()
    await msg.answer(f"✨ Lumina AI проанализировала фото:\n\n{suggestion}")
```

### Gift Certificates
```python
def gift_certificate(amount, sender, recipient):
    code = f"GIFT-{random.randint(1000, 9999)}-{amount}"
    return template.format(amount=amount, sender=sender, recipient=recipient, code=code)
```
Pattern: Generate unique code, format as card with borders, store in DB for redemption.

### Predictive Recommendations
```python
def predict_next_visit(service_history):
    last = service_history[0]
    days_since = (today - last_date).days
    if "стрижк" in service.lower() and days_since >= 28:
        return "💇 Прошло {days_since} дней — пора стричься!"
```
Pattern: Based on visit history, predict when client should return. Show on /start if prediction applies. Requires `service_name` and `booking_date` in DB.

## Integration Points

1. **`/start` handler**: Add greeting + predictive recommendation
2. **Booking confirm**: Add smart reason before confirmation button
3. **`F.photo` handler**: Photo analysis → suggestions
4. **Cron job**: Aftercare reminders (Day 1/3/7/14)
5. **Gift certificate command**: Generate + send card

## Database Additions

```sql
-- For aftercare tracking
ALTER TABLE bookings ADD COLUMN aftercare_sent INTEGER DEFAULT 0;

-- For gift certificates
CREATE TABLE gift_certificates (
    code TEXT PRIMARY KEY,
    amount INTEGER,
    sender_id INTEGER,
    recipient_id INTEGER,
    used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- For photo analysis history
CREATE TABLE photo_analysis (
    id INTEGER PRIMARY KEY,
    client_id INTEGER,
    photo_file_id TEXT,
    suggested_services TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Production Pitfalls (from salon-bot session 2026-06-22)

1. **`date.today().hour`** — `date` has no `.hour`. Use `datetime.now().hour`.
2. **Scoped import breaks at runtime** — `from datetime import datetime` inside `if` block → `UnboundLocalError` outside. Always import at function top.
3. **edit_text on photo** — `TelegramBadRequest: there is no text in the message to edit`. Use `delete()` + `answer_photo()` with try/except + text fallback.
4. **Gender-neutral copy** — "Приведи подругу" → "Приведи друга" / "Вам обоим скидка". All UI text must not assume gender.
5. **Global error handler for photo edit_text** — Instead of per-handler try/except, add `@dp.error()` in main.py that catches `TelegramBadRequest("there is no text in the message to edit")` and sends main menu as new message. See `references/telegram-bot-api-10-features.md`.
