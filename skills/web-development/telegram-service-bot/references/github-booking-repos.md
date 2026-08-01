# GitHub Telegram Booking Bot Repos

Last updated: 2026-05-28

## Tier 1: Production-Ready (clone & adapt)

### WingorOsnova/TGB-Booking
- URL: https://github.com/WingorOsnova/TGB-Booking
- Stars: 2 | Language: Python | Updated: 2026-05-14
- Stack: aiogram v3, async SQLAlchemy, SQLite, Alembic
- Features:
  - Client flow: service → date → time → confirm (inline keyboards)
  - Admin panel in Telegram: orders, services (add/toggle/delete), admin management
  - Roles: admin / super admin (SUPER_ADMIN_ID from .env)
  - Booking conflict protection (is_slot_taken check)
  - Max active bookings limit per user
  - My Bookings with cancel (filtered by status)
  - Service toggling (is_active) — no code changes needed
  - Alembic migrations (3 versions: initial, is_super_admin, is_active)
- Config (.env): BOT_TOKEN, DATABASE_URL, ADMIN_IDS, SUPER_ADMIN_ID, TIMEZONE, WORKING_HOURS, SLOT_STEP_MIN, SLOT_DAYS_AHEAD, MAX_ACTIVE_BOOKINGS, SALON_NAME, CURRENCY
- File structure: main.py, config.py, constants.py, db/(models, queries, engine), handlers/(start, booking, my_bookings, admin, admin_services, admin_users, cancel_booking, info), keyboards/(main_menu, booking, admin, admin_bookings, admin_services, admin_users, my_bookings), services/slots.py, states/(booking, admin_services, admin_users)
- Local clone: data/projects/TGB-Booking/

### dlysenko-dev/telegram-booking-bot
- URL: https://github.com/dlysenko-dev/telegram-booking-bot
- Stars: 0 | Language: Python | Updated: 2026-03-26
- Stack: aiogram3 + SQLite
- Features: service catalog with prices, inline calendar, free slots display, booking confirmation, reminder 1hr before visit, admin notifications, admin panel with stats, cancel by client/admin
- Config: BOT_TOKEN, ADMIN_IDS, WORK_START_HOUR, WORK_END_HOUR, SLOT_DURATION_MIN, REMINDER_BEFORE_MIN

## Tier 2: Useful References

### kurkurzz/TelegramBot-BookingWithTimeslot
- URL: https://github.com/kurkurzz/TelegramBot-BookingWithTimeslot
- Stars: 8 | Language: Python | Updated: 2026-05-08

### andryplekhanov/hotels-aiogram-bot
- URL: https://github.com/andryplekhanov/hotels-aiogram-bot
- Stars: 2 | Stack: aiogram + PostgreSQL + SQLAlchemy + Docker
- Features: Hotels.com API integration, hotel search
- Demo video: https://youtu.be/KhSCAg0uD4U

### qXstay/telegram-beauty-booking-bot
- URL: https://github.com/qXstay/telegram-beauty-booking-bot
- Stars: 0 | Updated: 2026-03-15
- Focus: beauty salon booking, reminders, admin notifications

### IldarS2000/GrandHotelBot
- URL: https://github.com/IldarS2000/GrandHotelBot
- Stars: 2 | Focus: hotel room booking

### kinfe-pythoner/Hotel-Booking-Telegram-Bot
- URL: https://github.com/kinfe-pythoner/Hotel-Booking-Telegram-Bot
- Stack: aiogram 3.1.4 | Focus: hotel reservation

## GitHub API Search

```python
import urllib.request, json
url = "https://api.github.com/search/repositories?q=aiogram3+booking&sort=stars&order=desc&per_page=5"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/vnd.github.v3+json"})
resp = urllib.request.urlopen(req, timeout=15)
data = json.loads(resp.read())
for item in data["items"]:
    print(f"⭐{item['stargazers_count']} | {item['full_name']} | {item['html_url']}")
```
