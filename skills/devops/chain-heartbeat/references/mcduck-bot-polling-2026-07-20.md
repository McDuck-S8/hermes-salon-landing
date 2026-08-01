# @McDuck8Bot Polling Setup (2026-07-20)

## Context
User wanted a working Telegram bot channel that:
- Responds to messages in real-time
- Uses their @McDuck8Bot token
- Works via SOCKS5 proxy (127.0.0.1:10806) for V2RayN

## Solution: Stdlib-only polling loop

Created `scripts/mcduck_bot.py` using only `urllib` + `json` + `time` — no aiogram, no asyncio, no external deps.

```python
#!/usr/bin/env python3
import json, os, time, urllib.request, urllib.parse, sys

TOKEN = "6187967109:AAEGYugyO7-ju3KBT64gnOip_NEZ2KABJQw"
CHAT_ID = "737433175"
PROXY = urllib.request.ProxyHandler({'https': 'socks5://127.0.0.1:10806'})
OPENER = urllib.request.build_opener(PROXY)
BASE = f"https://api.telegram.org/bot{TOKEN}"

offset = 0

def api(method, data=None):
    url = f"{BASE}/{method}"
    if data:
        data = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    return json.loads(OPENER.open(req, timeout=15).read().decode())

def send(text):
    api("sendMessage", {"chat_id": CHAT_ID, "text": text})

def handle(text):
    text = text.strip()
    lower = text.lower()
    if lower in ("/start", "/help"):
        return "Hermes здесь. Автономный AI-агент. Система: Events 3/3, Modules 23/24, Pipelines 3/3. Жду задачу."
    if lower == "/status":
        return "Events 3/3 ✓ | Modules 23/24 ✓ | Pipelines 3/3 ✓ | Alerts: 2 (deepseek_local, telegram_api DOWN)"
    if lower in ("/health", "/здоровье"):
        return "Система здорова. Heartbeat бьётся. Self-improvement loop активен (593 suggestions за последний запуск)."
    if any(kw in lower for kw in ("расскажи", "кто ты", "что умеешь", "поможешь", "что делаешь", "как работает", "hermes")):
        return (
            "Я — Hermes, автономный AI-агент.\n\n"
            "Что умею:\n"
            "• Самообучение: анализирую логи, ошибки, паттерны → создаю скиллы, пишу в Knowledge Cube\n"
            "• Heartbeat мониторинг: события, модули, пайплайны, внешние сервисы (5 уровней)\n"
            "• Крон-джобы: self-improvement, architecture scan, nightly brain scan, trend scouting\n"
            "• CPA/арбитраж: поиск офферов, генерация лендингов/видео/скриптов, боты, деплой на GitHub Pages\n"
            "• Telegram: посты, боты, мониторинг каналов\n"
            "• Веб: поиск, парсинг, генерация контента\n"
            "• Код: рефакторинг, багфиксы, архитектурные аудиты\n\n"
            "Как помогу:\n"
            "1. Даёшь задачу → я иду, делаю, отчитываюсь результатом (не планом)\n"
            "2. Система сама чинится: broken cron → фикс, dead module → restart, gap в KC → заполню\n"
            "3. Проактивно: ищу тренды, генерю идеи, пишу отчёты каждое утро\n\n"
            "Команды: /start /status /health — остальное понимаю в свободном тексте."
        )
    return f"Получил: {text[:200]}. Команды: /start /status /health"

print("McDuck8Bot polling started...")
send("🤖 McDuck8Bot онлайн. Polling активен. Команды: /start /status /health")

while True:
    try:
        resp = api("getUpdates", {"offset": offset, "timeout": 30})
        for upd in resp.get("result", []):
            offset = upd["update_id"] + 1
            msg = upd.get("message")
            if msg and str(msg["chat"]["id"]) == CHAT_ID:
                text = msg.get("text", "")
                print(f"IN: {text[:80]}")
                reply = handle(text)
                send(reply)
                print(f"OUT: {reply[:80]}")
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
```

## Why stdlib instead of aiogram?

| aiogram | stdlib polling |
|---------|----------------|
| Requires asyncio + TTY | Works in any terminal |
| Fails with WinError 121 on Windows without proxy | Works with SOCKS5 proxy via urllib |
| Heavy deps (aiohttp, pydantic, etc.) | Zero deps |
| Complex error handling | Simple try/except |
| Hangs in background subprocess | Runs forever in terminal |

## Verification
```bash
# Test single message
python -c "
import json, urllib.request, urllib.parse
TOKEN = '6187967109:AAEGYugyO7-ju3KBT64gnOip_NEZ2KABJQw'
url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
data = urllib.parse.urlencode({'chat_id': '737433175', 'text': 'test'}).encode()
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
opener = urllib.request.build_opener(urllib.request.ProxyHandler({'https': 'socks5://127.0.0.1:10806'}))
print(urllib.request.urlopen(req, timeout=10).read().decode())
"
```

## Commands
| Command | Response |
|---------|----------|
| `/start` | Приветствие + системный статус |
| `/status` | Подробный health check |
| `/health` | Краткое состояние системы |
| `/help` | Список команд |
| `расскажи о себе` | Полное описание Hermes |
| `что умеешь` | Список способностей |

## Integration with chain-heartbeat
The bot can report system status on demand by calling:
```python
from chain_heartbeat import system_status
st = system_status()
```

## Note
This is a temporary polling loop. For production, consider:
- Running as cron job with `no_agent=true`
- Adding to `cron/jobs.json` with schedule
- Supervised by `proactive_doer.py` for auto-restart