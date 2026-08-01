# mira-agent — реализация task-driven-agent (2026-07-10)

Реализация Telegram AI-агента по образцу MIRA (видео SeTka Project).

## Проект

`D:\Portable_Soft\hermes\mira-agent\` — 14 файлов, ~1200 строк, 7 навыков.

## Ключевые файлы

| Файл | Назначение |
|------|-----------|
| `bot.py` | Telegram-бот (python-telegram-bot v22), /start, /help, handle_message, handle_voice |
| `agent_core.py` | interpret_task() → LLM → plan → execute_plan() → диспетчеризация |
| `config.py` | Загрузка .env, BOT_TOKEN с fallback MIRA_BOT_TOKEN→TELEGRAM_BOT_TOKEN |
| `run.py` | start/stop/restart/status/watchdog, управление процессом через PID-файл |
| `skills/content.py` | generate_text(), generate_image() — встроенные, без внешних API |
| `skills/social.py` | Twitter/X API v2, Instagram/FB — dry-run без ключей |
| `skills/email.py` | Gmail — каркас, dry-run без credentials.json |
| `skills/scheduler.py` | SQLite, cron-формат, create/list/delete |
| `skills/moderation.py` | Спам + токсичность по regex |
| `skills/crypto.py` | CoinGecko API (async httpx), price + trending |
| `skills/search.py` | DuckDuckGo Instant Answer API |

## agent_core.py — системный промпт

Интерпретатор использует единый `SYSTEM_PROMPT` с описанием всех навыков и JSON-схемой ответа. Имеет fallback на `search` если LLM API ключ не задан.

## Telegram-бот (bot.py)

- `python-telegram-bot v22` с `Application.builder()`
- 4 handler: `/start`, `/help`, `TEXT`, `VOICE`
- Все текстовые сообщения идут через `interpret_task()` → `execute_plan()`

## Запуск

```bash
# Требуется MIRA_BOT_TOKEN в .env (отдельный от TELEGRAM_BOT_TOKEN)
cd D:\Portable_Soft\hermes
python mira-agent\bot.py

# Или через run.py:
python mira-agent\run.py start
python mira-agent\run.py status
python mira-agent\run.py stop
python mira-agent\run.py watch   # watchdog с перезапуском каждые 30с
```

## Статус интеграций

| Сервис | Статус | Требует |
|--------|--------|--------|
| Telegram | ✅ работает | MIRA_BOT_TOKEN |
| Текст + картинки | ✅ встроено | ничего |
| Расписания | ✅ SQLite | ничего |
| Модерация | ✅ regex | ничего |
| Поиск | ✅ DuckDuckGo | ничего |
| Крипта | ✅ CoinGecko | ничего |
| Twitter/X | 🟡 dry-run | X_BEARER_TOKEN |
| Instagram | 🟡 dry-run | INSTAGRAM_USERNAME |
| Gmail | 🟡 dry-run | credentials/gmail.json |

## Отличия от оригинала MIRA

- MIRA использует Composo (500+ интеграций) — mira-agent имеет 7 модульных навыков
- MIRA имеет приватный режим (Kakun) — mira-agent без крипто-приватности
- MIRA имеет встроенный кошелёк и DeFi — mira-agent только курс крипты
- MIRA имеет голосовой ввод — mira-agent принимает голос но не обрабатывает
- Общая архитектура (NL → agent core → skills) — идентична
