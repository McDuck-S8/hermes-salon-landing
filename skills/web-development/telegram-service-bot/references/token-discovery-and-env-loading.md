# Token Discovery & Environment Loading (Salon Bot)

## Session Context (2026-06-11)

Building a salon-bot sub-project under `D:/Portable_Soft/hermes/projects/salon-bot/`.

## Finding the Token

Hermes stores Telegram tokens in `TELEGRAM_BOT_TOKEN` in the root `.env`:
`D:/Portable_Soft/hermes/.env`

Sub-project bot configs typically expect `BOT_TOKEN`. Must map between them.

## Auto-Loading Hermes Root .env

The `.env` file at Hermes root is not loaded by sub-projects. Add this to the sub-project's `config.py`:

```python
from pathlib import Path

_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_path.exists():
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                _k, _v = _k.strip(), _v.strip().strip('"').strip("'")
                if _k not in os.environ:
                    os.environ[_k] = _v
```

Assumes layout: `project/bot/config.py` → `project/` → `hermes/` → `.env`

## Network Block

Telegram API (149.154.166.110:443) is unreachable on the local network while general internet (google.com) works.

Resolution options:
- Proxy (HTTP/SOCKS5)
- VPS deployment (Docker)
- Local Mini App preview in browser (self-contained HTML with demo data)

## Token Verification Command

```bash
python -c "
import asyncio
from aiogram import Bot
async def v():
    bot = Bot(token='YOUR_TOKEN')
    me = await bot.get_me()
    print(f'OK → @{me.username}')
    await bot.session.close()
asyncio.run(v())
"
```

## File Structure Reference

```
projects/salon-bot/
├── main.py              # Entry point
├── config.py            # Auto-loads Hermes .env + BOT_TOKEN/TELEGRAM_BOT_TOKEN
├── requirements.txt
├── Dockerfile
├── bot/
│   ├── db.py            # Schema v2: pooled aiosqlite, multi-salon, WAL indices
│   ├── keyboards.py     # Design system: gradients, emoji, 2026 UX
│   ├── handlers/
│   │   ├── client.py    # FSM booking flow
│   │   ├── admin.py     # Admin CRUD panel
│   │   ├── master.py    # Master auth + schedule
│   │   └── webapp.py    # Mini App data handler
│   └── webapp/
│       └── index.html   # Self-contained Mini App with demo data
├── cron/
│   └── reminders.py     # 24h reminder + cleanup
└── AGENTS.md
```
