# branches.yaml Template

Copy this structure when creating a new branches.yaml:

```yaml
branches:
  branch-name:
    status: "one-line current state"
    last_action: "what was just done"
    next_step: "what should happen next"
    key_files:
      - "path/to/relevant/file.py"
    context: "important tokens, ports, configs, versions"
```

## Naming Convention
- Lowercase with hyphens: `crm-bot`, `freellmapi`, `self-evolution`
- Max 5-7 active branches
- Mark completed branches with `[CLOSED]` prefix in status

## Example (real session)
```yaml
branches:
  crm-bot:
    status: "бот запущен PID 83856, работает"
    last_action: "проверили что бот отвечает в Telegram"
    next_step: "тестирование бронирования"
    key_files:
      - "data/projects/crimea-bots/production_hotel_bot.py"
    context: "aiogram 3.28.2, SOCKS5 прокси, CRM SQLite"
  freellmapi:
    status: "РАБОТАЕТ! PID 93992, порт 3001"
    last_action: "запустил сервер, все API endpoints отвечают 200"
    next_step: "добавить API ключи провайдеров в /api/keys"
    key_files:
      - "D:/Portable_Soft/freellmapi/"
    context: "Express 5 + better-sqlite3 12.10.0 + drizzle-orm"
```

## breadcrumbs.log Format
```
[HH:MM] branch-name | action taken | next step
[12:05] crm-bot | запустил бота PID 83856 | жду тест в Telegram
[12:08] freellmapi | npm install сломан | нужен better-sqlite3
[12:15] crm-bot | пользователь тестирует бронирование | жду反馈
```
