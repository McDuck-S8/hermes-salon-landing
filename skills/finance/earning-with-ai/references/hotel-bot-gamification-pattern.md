# Hotel Bot v2 — Gamification Design Pattern

## Why Standard Hotel Bots Fail

Standard hotel bot flow: rooms → book → contacts. It's a conveyor belt — users visit once, book, never return. No reason to come back.

## Engagement Features That Work

### 1. Personality
Give the bot a name and character. "Крымчанка" (Crimean woman) — warm, local, uses sea/sun emojis. Not a corporate machine.

### 2. Loyalty System
- Points for actions: +5 booking, +10 quiz correct, +5 daily check-in
- Levels: Новичок (0-50) → Постоялец (51-200) → VIP (201-500) → Легенда (500+)
- Progress bar to next level
- Visual level badges (🌱 → 🌟 → 💎 → 👑)

### 3. Daily Check-in (/checkin)
- +5 base points per day
- Streak bonus: +1 extra per consecutive day (up to +7)
- Reset streak if miss a day
- Users come back DAILY, not just when booking

### 4. Wheel of Fortune
- 1 spin per day
- Random prizes: 5%, 10%, 15%, 20%, 25% discounts, free breakfast, sunset champagne
- Generates promo codes
- Creates urgency: "come back tomorrow to spin again!"

### 5. Quiz About Region
- 15+ questions about Crimea (history, geography, fun facts)
- 4 answer buttons (inline keyboard)
- Shows fun fact after each answer
- +10 points per correct answer
- Leaderboard (/top command)
- Users learn about Crimea = more desire to visit

### 6. Inline Everything
- Date picker with buttons (not text input)
- Guest count with buttons
- Back button at every step
- No text parsing needed for most flows

### 7. Gallery Carousel
- Room showcase with prev/next buttons
- Each room: name, price, description, emoji
- Link to booking from gallery

## Database Schema Additions

```sql
-- Users table (gamification)
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    loyalty_points INTEGER DEFAULT 0,
    daily_streak INTEGER DEFAULT 0,
    last_checkin TEXT,
    wheel_spins INTEGER DEFAULT 0,
    last_spin TEXT,
    quiz_score INTEGER DEFAULT 0,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quiz tracking
CREATE TABLE quiz_progress (
    user_id INTEGER,
    question_idx INTEGER,
    answered_correctly INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, question_idx)
);

-- Discount codes from wheel
CREATE TABLE discount_codes (
    code TEXT PRIMARY KEY,
    percent INTEGER,
    user_id INTEGER,
    used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Key Metrics to Track

- DAU (daily active users via check-ins)
- Quiz completion rate
- Wheel spin rate
- Loyalty level distribution
- Booking conversion from quiz/wheel users

## Implementation Stack

- aiogram 3.x + aiosqlite
- All gamification in same bot (no separate services)
- Inline keyboards for everything (no ReplyKeyboard where possible)
- FSM states for booking flow with back buttons
