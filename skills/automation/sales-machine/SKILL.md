---
name: sales-machine
description: >
  Sales Machine — международный конвейер по привлечению клиентов для малого бизнеса.
  Сканирует Google Maps, генерирует демо-лендинги, отправляет предложения через
  Telegram/WhatsApp/VK/OK/Email, передаёт тёплых лидов полевым агентам.
version: 1.0.0
platforms: [windows]
metadata:
  hermes:
    tags: [sales, lead-generation, landing-pages, monetization]
---

# Sales Machine — International Lead Generation & Sales Automation

## Location
`D:\Portable_Soft\hermes\projects\sales-machine\`

## Architecture

```
lead_finder.py ──> demo_builder.py ──> closer.py ──> field_agent.py
    │                   │                  │               │
    ▼                   ▼                  ▼               ▼
Google Maps        HTML Landing        Telegram        Field Agent
Yandex Maps        GitHub Pages        WhatsApp        (человек)
2GIS              (5 мин deploy)       VK / OK         Close Script
Instagram                              Email
Facebook
```

## Modules

### lead_finder.py
- Сканирует Google Maps для бизнесов (салоны, рестораны, отели и т.д.)
- Собирает: название, телефон, адрес, рейтинг, категории, сайт
- Сохраняет в SQLite (db/clients.db)
- Поддерживает пресеты: kiev_salons, budva_restaurants, budva_hotels, etc.
- **⚠️ Если Google Maps недоступен** (консент, Chrome не запущен, cron) — используйте `references/web-search-fallback.md` для компиляции лидов через множественные веб-источники

### demo_builder.py
- Генерирует HTML landing page для 5 ниш: salon, restaurant, hotel, auto_service, clinic
- Поддерживает 3 языка: ru, en, sr
- Адаптивные, современные, с CTA-кнопками
- Deploy на GitHub Pages опционально
- **WCAG 2.1 AA** — для EU-рынка требуется доступность. См. навык `web-accessibility` для полного чеклиста

### closer.py
- Интеграция с Composio (Telegram, WhatsApp, VK, OK, Gmail)
- Sales scripts с обработкой возражений
- Отслеживание ответов

### field_agent.py
- Регистрация полевых агентов
- Назначение тёплых лидов
- Скрипты закрытия сделки (ru/sr)

## Quick Start

```bash
cd /d/Portable_Soft/hermes/projects/sales-machine

# 1. Инициализировать БД
python -c "from lead_finder import init_db; init_db()"

# 2. Сканировать Google Maps (через browser-harness)
# Используйте browser-harness run.py для выполнения lead_finder
```

## Commands

```bash
# Сканировать
python main.py scan budva_restaurants --lang en

# Просмотр лидов
python main.py leads --status new

# Генерация демо
python main.py demo <lead_id> --niche salon --lang ru

# Dashboard
python main.py dashboard

# Агенты
python main.py agent register --name "Milos" --phone "+382..." --location "Budva"
python main.py agent list
```

## OSINT Site Builder (New Methodology)

Коли клієнт дає Telegram-канал бізнесу замість сканування Google Maps:

1. Виконати **Фазу 1: OSINT** — проаналізувати канал (опис, пости, медіа, відгуки)
2. Згенерувати **звіт** у `reports/osint_report_[назва].md`
3. Показати користувачу → чекати рішення
4. **Фаза 2: Сайт** — створити landing page на основі зібраних даних
5. Quality Gate → deploy
6. **Фаза 3: Фінальний звіт**

Повна методологія: `references/osint-site-builder-methodology.md`

## Prequisites

1. browser-harness установлен (`pip install -e` в `browser-harness/`)
2. **Chrome/Chromium должен быть запущен** с включённым remote debugging (см. `install.md` в browser-harness)
3. Telegram Bot Token в `TELEGRAM_BOT_TOKEN` (env)
4. Composio API Key в `COMPOSIO_API_KEY` (env)

## ⚠️ Known Pitfalls

### Google Maps consent page blocks autonomous scanning
Google consistently redirects to a consent cookie page (`consent.google.com`) that **cannot be bypassed** via browser clicks or JavaScript evaluation in autonomous/cron mode. The consent page buttons are in isolated form contexts that don't respond to programmatic clicks.

**Workaround:** Use `references/web-search-fallback.md` — compile leads via `web_search_plus` across multiple sources (TripAdvisor, Booking.com, local directories) instead of browser-scraping Google Maps directly.

### Chrome must be running for lead_finder.py
The `lead_finder.py` module requires `browser-harness` which in turn needs a running Chrome/Chromium instance with remote debugging enabled. Without it, `scan_preset()` raises `ModuleNotFoundError` for `browser_harness` even if the package is installed (Windows pip install path mismatch).

**Detection:**
```bash
browser-harness --doctor  # Check "[FAIL] chrome running"
```
If Chrome isn't running, either launch it with remote debugging (Way 2) or use the web-search fallback.

### Пресеты не существуют в БД — только в коде
Пресеты (`budva_restaurants`, `budva_hotels`, etc.) — это просто строки запросов в `modules/lead_finder.py:QUERIES`. Они не создают таблицы или записи в БД. Если пресет не найден, сначала проверьте `QUERIES` dict.

## ⚠️ Windows Path Handling (critical)

**DO NOT use `/d/` MSYS paths in Python.** On Windows, `os.path.realpath('/d/Portable_Soft/...')` resolves to `D:\d\Portable_Soft\...` (wrong). Use proper OS paths:

```python
# ✅ CORRECT — use relative paths or os.path.join with abspath
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "db", "clients.db")

# ❌ WRONG — /d/ prefix breaks on Windows
DB_PATH = "/d/Portable_Soft/hermes/projects/sales-machine/db/clients.db"
```

**PYTHONPATH in git-bash:** env var is NOT passed to Windows Python. Always use `sys.path.insert(0, 'modules')` inside the script instead.

**`execute_code` sandbox** has a separate filesystem — DB/files written there are NOT visible from terminal. Run disk I/O from `terminal()` tool, not `execute_code()`.

## Database

`db/clients.db` — все данные: leads, demos, conversations, deals, field_agents.

| Таблица | Назначение |
|---|---|
| clients | Лиды (имя, телефон, адрес, рейтинг, статус) |
| demos | Сгенерированные лендинги (URL, template, язык) |
| conversations | История сообщений (канал, направление, текст) |
| deals | Сделки (сумма, статус, агент) |
| field_agents | Полевые агенты (контакты, локация, комиссия) |
| campaigns | Активные кампании (этап, канал) |
