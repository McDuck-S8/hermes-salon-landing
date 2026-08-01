---
name: recovery-test
description: "Auto-generated from RECOVERY_TEST.md"
trigger: "When user asks about RECOVERY_TEST concepts"
usage: recovery-test
Revisit: 2026-07-31
---

# RECOVERY_TEST.md — Тест на самовосстановление

**Дата:** 2026-06-19

---

## 1. Ты узнаешь что feedback_store повреждён?

**ДА** — но не автоматически.

**Механизм:** При следующем run autonomous_agent, compute_score() вызовет feedback_store.compute_weight(). Если файл повреждён — будет exception. Agent поймает его в try/except и продолжит с дефолтными весами (1.0). В логе будет "ImportError" или "JSONDecodeError".

**Проблема:** Нет dedicated monitor'а который проверяет целостность feedback_store. Агент узнает только когда попытается его прочитать. Если файл удалён — узнает при следующем run (через 5 минут). Если повреждён частично — может работать с кривыми данными.

**Конкретный путь:** `D:/Portable_Soft/hermes/cache/feedback_store.json`

## 2. Можешь ли восстановить веса?

- **Есть ли резервная копия:** НЕТ. Нет backup'а feedback_store.json.
- **Можно ли пересчитать из другого источника:** ДА. action_log.jsonl содержит все действия с статусами (success/error). Можно пересчитать веса из лога.
- **Продолжу как ни в чём не бывало:** ДА. С дефолтными весами (1.0). Агент забудет что какие-то действия были успешнее других.

**Конкретный путь:** `D:/Portable_Soft/hermes/cache/action_log.jsonl` (189 записей) → можно пересчитать.

## 3. Если завтра откажет один из модулей

**event_watcher:**
- **Узнаю ли:** НЕТ. event_watcher не существует как отдельный модуль. Есть event_reactor.py (one-shot check) и file_watcher.py (не используется).
- **Перезапущу ли:** НЕТ. Нет mechanism для self-restart.
- **Сообщу ли:** НЕТ. Нет alerting system.
- **Продолжу ли работать:** ДА. Agent работает через daemon timer, не зависит от event_watcher.

**curiosity_engine:**
- **Узнаю ли:** ДА. В logs будет "Curiosity scan failed".
- **Перезапущу ли:** НЕТ. Cron job запустит снова через 24 часа.
- **Сообщу ли:** НЕТ. Нет alerting.
- **Продолжу ли работать:** ДА. Не критичный модуль.

**feedback_store:**
- **Узнаю ли:** ДА. В autonomous_agent.log будет "ImportError".
- **Перезапущу ли:** НЕТ. Продолжу с дефолтными весами.
- **Сообщу ли:** НЕТ. Нет alerting.
- **Продолжу ли работать:** ДА. С потерей learning history.

## 4. Что произойдёт если отключить интернет на 2 часа

1. **curiosity_engine** — 0 discoveries (HN/Reddit/GitHub заблокированы). Уже 0.
2. **auto_recall** — не сможет искать в Lavra knowledge (если требует сеть).
3. **mcp_memory_bridge** — не сможет sync.
4. **session_dump_ingester** — будет работать (локальные файлы).
5. **autonomous_agent** — будет работать (все данные локальные).
6. **goal_queue** — будет работать (локальный JSON).
7. **feedback_store** — будет работать (локальный JSON).

**Итог:** 80% системы работает без интернета. 20% (curiosity, mcp sync, Lavra search) не работают.

## 5. Зависимости

| Зависимость | Тип | Что сломается без неё |
|-------------|-----|----------------------|
| Python 3.11 | Runtime | Всё |
| SQLite | DB | Knowledge Cube, feedback_store, sessions |
| Telegram Bot API | External | Salon bot, auto-poster, delivery |
| OpenRouter/DeepSeek | LLM | Классификация, анализ |
| Docker | Infra | money4band (если запущен) |
| Internet | Network | Curiosity, MCP sync, Lavra search |
| `cache/feedback_store.json` | Data | Learning loop (веса сбросятся) |
| `cache/agent_decisions.json` | Data | Decision history (cooldown) |
| `cache/goal_queue.json` | Data | Goal management |
| `cron/jobs.json` | Config | Все cron jobs |
| `config.yaml` | Config | Delegation, providers, MCP |
| `.env` | Config | Telegram token, API keys |
