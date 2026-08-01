# Telegram Helper — Централизованный доступ через прокси

## Проблема
Множество скриптов используют Telegram API напрямую без прокси. Каждый скрипт реализует свою логику подключения.

## Решение
`scripts/telegram_helper.py` — единая точка доступа к Telegram API через HTTP прокси.

## Конфигурация прокси
- **HTTP прокси:** `http://127.0.0.1:10809` (рабочий)
- **SOCKS5:** `socks5://127.0.0.1:10806` (ненадёжный)
- **V2RayN:** GUI-приложение, не запускается из bash

## Использование

```python
from telegram_helper import check_telegram_api, get_updates, send_message

# Проверка API
ok, code = check_telegram_api()
if ok:
    print(f"Telegram API доступен (код {code})")

# Получение обновлений
updates = get_updates(token, limit=50)
if "result" in updates:
    for u in updates["result"]:
        print(u)

# Отправка сообщения
result = send_message(token, chat_id, "Привет!")
```

## Статус-коды
- 200 — OK
- 302 — редирект (нормальный ответ)
- 401 — Unauthorized
- 404 — Not Found

## Интеграция
Скрипты, использующие telegram_helper:
- `scripts/procedural_executor.py` — проверка Telegram API
- `scripts/self_improvement_cycle.py` — проверка сети
- `scripts/network_watchdog.py` — мониторинг сети
- `scripts/hermes_heartbeat.py` — проверка здоровья
- `scripts/posting/read_posts.py` — чтение постов

## Уроки
1. ВСЕ curl/httpx вызовы к Telegram API должны использовать прокси
2. HTTP 302 — нормальный ответ (редирект)
3. SOCKS5 на 10806 — ненадёжный, лучше HTTP на 10809
