"""
Salon Bot — Configuration (2026)
Architecture: Backend Architect 🏗️
"""
# === SALON BOT CONFIG ===
import os
from pathlib import Path

# Auto-load .env from Hermes root, then project-level override
for _env_rel in ["../../.env", "../../../.env", ".env"]:
    _env_path = Path(__file__).resolve().parent / _env_rel
    if _env_path.exists():
        with open(_env_path) as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    _k, _v = _k.strip(), _v.strip().strip('"').strip("'")
                    if _k not in os.environ:
                        os.environ[_k] = _v
from dataclasses import dataclass, field

@dataclass
class Config:
    # Telegram — читаем из BOT_TOKEN или TELEGRAM_BOT_TOKEN
    BOT_TOKEN: str = (
        os.environ.get("BOT_TOKEN") or
        os.environ.get("TELEGRAM_BOT_TOKEN") or
        ""
    )
    # SOCKS5 proxy для Telegram (если API заблокирован)
    PROXY: str = (
        os.environ.get("PROXY") or
        os.environ.get("BOT_PROXY") or
        ""
    )
    SUPERADMIN_ID: int = int(os.environ.get("SUPERADMIN_ID", "0"))

    # Salon default
    SALON_NAME: str = os.environ.get("SALON_NAME", "Салон Красоты")
    SALON_PHONE: str = os.environ.get("SALON_PHONE", "+7 (978) 000-00-00")
    SALON_ADDRESS: str = os.environ.get("SALON_ADDRESS", "г. Симферополь")
    SALON_TG: str = os.environ.get("SALON_TG", "")
    SALON_INSTAGRAM: str = os.environ.get("SALON_INSTAGRAM", "")

    # Business hours
    WORK_START_HOUR: int = 9
    WORK_END_HOUR: int = 20
    SLOT_DURATION: int = 30  # minutes

    # Booking
    BOOKING_DAYS_AHEAD: int = 14
    MIN_HOURS_BEFORE: int = 2  # minimum hours before booking

    # Mini App
    WEBAPP_URL: str = os.environ.get("WEBAPP_URL", "")

    # Paths
    DB_PATH: str = os.path.join(os.path.dirname(__file__), "data", "salon.db")
    LOG_PATH: str = os.path.join(os.path.dirname(__file__), "data", "bot.log")

    # Monitoring
    METRICS_PREFIX: str = "salon_bot"

    # Payment (ЮKassa placeholder)
    YOOKASSA_SHOP_ID: str = os.environ.get("YOOKASSA_SHOP_ID", "")
    YOOKASSA_SECRET_KEY: str = os.environ.get("YOOKASSA_SECRET_KEY", "")

config = Config()
