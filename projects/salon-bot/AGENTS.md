# Salon Bot — Robot для салона красоты

## Purpose
Telegram-бот для записи клиентов в салон красоты. Тренд 2026: Mini App, дизайн-система, напоминания.

## Ownership
- **Backend Architect 🏗️** — полный контроль архитектуры
- Стек: Python 3.11+, aiogram 3, SQLite, HTML/JS Mini App

## Structure
```
salon-bot/
├── main.py              # Entry point
├── config.py            # Config via dataclass + env vars
├── requirements.txt
├── Dockerfile
├── .env.example
├── bot/
│   ├── db.py            # Database layer (schema v2, pooled)
│   ├── keyboards.py     # Inline keyboards + design tokens
│   ├── handlers/
│   │   ├── client.py    # Client booking flow (FSM)
│   │   ├── admin.py     # Admin panel (CRUD)
│   │   ├── master.py    # Master panel
│   │   └── webapp.py    # Mini App data handler
│   └── webapp/
│       └── index.html   # Mini App (calendar/time picker)
├── cron/
│   └── reminders.py     # 24h reminders + cleanup
├── data/                # SQLite DB (gitignored)
└── AGENTS.md
```

## Commands
- `/start` — главное меню
- `/admin` — панель администратора
- `/master` — панель мастера (по коду)
- `/webapp` — Mini App запись

## Environment
```
BOT_TOKEN=...
SUPERADMIN_ID=...
WEBAPP_URL=https://...  # optional, for Mini App
YOOKASSA_SHOP_ID=...    # optional
YOOKASSA_SECRET_KEY=... # optional
```

## Deployment
- **Status**: Running (background process via Hermes)
- **Bot**: @HotelCrimeaBot (test token)
- **Proxy**: SOCKS5 (127.0.0.1:10806)
- **Log**: `data/bot.log`
- **DB**: `bot/data/salon.db`

## Monitoring
- **watchdog.py** — проверяет бота через Telegram API каждые 5 минут (Hermes cron job `salon-bot-watchdog`). Перезапускает если не отвечает.

## Crons
Ежедневно в 9:00:
```bash
python -m cron.reminders
```
