---
name: procedural-skills
description: "Auto-generated from PROCEDURAL_SKILLS.md"
trigger: "When user asks about PROCEDURAL_SKILLS concepts"
usage: procedural-skills
Revisit: 2026-07-31
---

# Procedural Skills — Deterministic Action Chains

> Revisit: when new reflex patterns emerge, infrastructure changes, or alert thresholds shift. Last touched: 2026-07-02.

Цепочки действий, которые выполняются БЕЗ LLM. Триггер → Действие → Запись.

**Формат:**
```
### SKILL: <name>
TRIGGER: <condition>    — что проверяем
ACTIONS:                — цепочка шагов (порядок важен)
  1. <action>
  2. <action>
FEEDBACK: <what to log> — результат в feedback_store
ALERT: <level>          — если нужен алерт пользователю
```

**Принцип:**
- Если триггер сработал → ВЫПОЛНЯЕМ, не спрашиваем
- Если действие провалилось → логируем и идём дальше
- Результат → feedback_store (успех/провал + метрики)
- Критические провалы → ALERTS.md + pending_alerts.json

---

### SKILL: network_dead
TRIGGER: proxy port 10806 не отвечает ИЛИ curl через прокси timeout
ACTIONS:
  1. Проверить порт 10806: `netstat -ano | grep 10806 | grep LISTENING`
  2. Если процесс v2ray/xray жив но не отвечает:
     a. `taskkill /PID <pid> /F`
     b. Запустить: `start "" "D:\v2rayN-windows-64\v2rayN.exe"`
     c. Подождать 10 секунд
     d. Проверить: `curl -x socks5://127.0.0.1:10806 -s --connect-timeout 5 https://api.telegram.org`
  3. Если порт мёртв:
     a. Попробовать `wmic process where "commandline like '%v2ray%'" call terminate`
     b. Запустить: `start "" "D:\v2rayN-windows-64\v2rayN.exe"`
     c. Подождать 15 секунд
     d. Проверить
  4. Если proxy не восстановился после 2 попыток → переключить сервер:
     a. Прочитать `D:\v2rayN-windows-64\guiNConfig.json`
     b. Найти текущий activeServer index
     c. Переключить на следующий
     d. Перезапустить v2rayN
     e. Подождать 10 сек
     f. Проверить
  5. Перезапустить gateway: `hermes gateway stop && hermes gateway run`
  6. Подождать 15 сек, проверить connection: `netstat -ano | grep <gateway_pid> | grep 10806`
FEEDBACK: success/fail, прокси uptime%, какой сервер, gateway PID
ALERT: 1 (если proxy не восстановился)

### SKILL: proxy_intermittent
TRIGGER: proxy работает <70% за последние 10 попыток
ACTIONS:
  1. Логировать: proxy success rate в feedback_store
  2. Увеличить timeout до 30 сек в adapter.py (если ещё не)
  3. Убедиться что keepalive_expiry=0 в adapter.py (если ещё не)
  4. Не переключать сервер — интермиттент ≠ мёртв
FEEDBACK: success rate, timeout, keepalive settings

### SKILL: gateway_dead
TRIGGER: gateway PID не найден в process list ИЛИ process exit code != 0
ACTIONS:
  1. Удалить stale lock: `rm -f ~/.hermes/gateway.pid ~/.hermes/gateway.lock ~/.hermes/gateway_state.json`
  2. Убить zombie процессы: `taskkill /F /IM "python.exe" | grep gateway`
  3. Очистить __pycache__ adapter: `rm -rf hermes-agent/plugins/platforms/telegram/__pycache__`
  4. Запустить: `cd D:/Portable_Soft/hermes && HERMES_TELEGRAM_HTTP_CONNECT_TIMEOUT=30 hermes-agent/.venv/Scripts/python.exe -m hermes_cli.main gateway run`
  5. Подождать 10 сек
  6. Проверить: `hermes gateway list` → должен показать PID
  7. Проверить proxy connection: `netstat -ano | grep <pid> | grep 10806`
FEEDBACK: gateway PID, startup time, proxy connected yes/no
ALERT: 2 (если 3 перезапуска за час)

### SKILL: cron_job_stuck
TRIGGER: cron job в error status 3 раза подряд
ACTIONS:
  1. Прочитать job из jobs.json
  2. Найти ошибки: `grep -A5 "last_error" cron/jobs.json`
  3. Перезаписать next_run на +1 час от сейчас
  4. Добавить поле `consecutive_errors: N`
  5. Логировать в feedback_store: job_id, error_type, consecutive_count
  6. Если consecutive_errors >= 5 → ALERT
FEEDBACK: job_id, error, new_next_run
ALERT: 2 (если >= 5 ошибок подряд)

### SKILL: goal_blocked_escalate
TRIGGER: goal в статусе "blocked" дольше 24 часов
ACTIONS:
  1. Прочитать goal из knowledge cube / goals state
  2. Определить причину блокировки
  3. Если причина "proxy/network" → применить network_dead
  4. Если причина "code/build" → попробовать fix
  5. Если причина "waiting_user" → пропустить
  6. Если ничего не помогло за 24ч → ALERT пользователю
FEEDBACK: goal_id, block_duration, cause, action_taken
ALERT: 1 (всегда — пользователь должен знать)

### SKILL: disk_low
TRIGGER: disk usage > 90% на D:
ACTIONS:
  1. `du -sh D:/Portable_Soft/hermes/cache/* | sort -hr | head -5`
  2. Удалить файлы старше 7 дней: `find cache/ -mtime +7 -delete`
  3. Очистить логи > 10MB: `find logs/ -size +10M -delete`
  4. Очистить __pycache__: `find . -name __pycache__ -exec rm -rf {} + 2>/dev/null`
  5. Проверить диск снова
FEEDBACK: freed_space_mb, before%, after%
ALERT: 1 (если > 95% после очистки)

### SKILL: session_recall_index
TRIGGER: >100 новых сообщений с последней индексации
ACTIONS:
  1. `python scripts/session_recall.py --index`
  2. Проверить: `python scripts/session_recall.py --status`
FEEDBACK: indexed_count, total_indexed

### SKILL: signal_new_brick
TRIGGER: signal_pipeline.py добавил новый кирпич в ARBITRAGE_WORKSHOP.md
ACTIONS:
  1. Проверить: `grep -c "требует проверки" ARBITRAGE_WORKSHOP.md`
  2. Если кирпичей > 0 — запустить rd_processor.py для обработки
  3. Если rd_processor создал цель — проверить что цель в goal_queue.json
  4. Логировать:砖数, новые цели
FEEDBACK: bricks_count, goals_created
ALERT: 0 (штатная работа)

### SKILL: no_bricks_today
TRIGGER: R&D не добавил ни одного кирпича за 24 часа
ACTIONS:
  1. Проверить: `grep -c "$(date +%Y-%m-%d)" cache/bricks_log.jsonl`
  2. Если 0 — создать алерт в ALERTS.md
  3. Проверить: curiosity_engine.py работает? (timeout 15 python scripts/curiosity_engine.py --quick)
  4. Если сканер падает — проверить сеть/прокси
FEEDBACK: bricks_today, scanner_status
ALERT: 1 (WARNING — R&D простаивает)

### SKILL: no_lessons_today
TRIGGER: Отдел развития не записал ни одного урока за 24 часа
ACTIONS:
  1. Проверить: `grep -c "$(date +%Y-%m-%d)" LESSONS.md`
  2. Если 0 — проверить feedback_store.json за сегодня
  3. Если есть записи в feedback — извлечь уроки
  4. Если нет записей — логировать что система не работает
FEEDBACK: lessons_today, feedback_entries
ALERT: 1 (WARNING — развитие простаивает)

### SKILL: workshop_stale
TRIGGER: ARBITRAGE_WORKSHOP.md не обновлялся >3 дней
ACTIONS:
  1. Проверить: `stat -c %Y ARBITRAGE_WORKSHOP.md` (last modified)
  2. Если >3 дней — запустить полный pipeline (signal_pipeline.py)
  3. Если pipeline не находит нового — проверить источники
FEEDBACK: last_modified, pipeline_result
ALERT: 1 (WARNING — мастерская простаивает)
