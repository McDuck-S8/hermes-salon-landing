---
name: alerts
description: "Auto-generated from ALERTS.md"
trigger: "When user asks about ALERTS concepts"
usage: alerts
Revisit: 2026-07-31
---

# ALERTS.md — Текущие проблемы системы

**Обновлено:** 2026-06-22 14:50 (meditation cycle)

---

## RESOLVED

### [RESOLVED] Cron jobs: 22 PAST DUE → 0
- **Время решения:** 2026-06-22
- **Причина:** Scheduler не выполнял time-based jobs с 11 июня
- **Действие:** Вручную запущены все 22 джоба, исправлены баги путей:
  - `event_daemon.py beat` → `event_daemon.py` (двойной путь)
  - `hermes_health.py --watch` → `hermes_health.py` (--watch часть имени)
  - `event_trigger.py` — создан мёртвый скрипт
  - `jarvis_security_wrapper.py` — создан обёртка для --warnings-only
- **Статус:** ALL_GREEN по reality_gate

### [RESOLVED] OpenCode title_generation provider error
- **Время решения:** 2026-06-22
- **Причина:** auxiliary.title_generation использовал provider "opencode" вместо "opencode-zen"
- **Действие:** config.yaml patched

---

## ACTIVE

### [MEDIUM] Trend Scout и Market Research timeout (120s)
- **Модуль:** cron
- **Проблема:** trend_scout.py и market_research.py слишком долгие для 120s лимита
- **Действие:** Увеличить timeout или оптимизировать скрипты

### [LOW] Knowledge Cube "stale" по reality_gate
- **Модуль:** reality_gate
- **Проблема:** reality_gate проверяет mtime файла, а не БД
- **Реальность:** KC здоров — 5794 записей, 185 скиллов
- **Действие:** Исправить reality_gate проверку

---

## KNOWN ISSUES (not blocking)

### Curiosity Engine: SSL errors
- HN и GitHub недоступны из-за SSL
- 0 реальных discoveries за все запуски
- Решение: переключиться на локальные источники

### Salon bot: running but not earning
- Бот запущен (14 процессов), но нет реальных клиентов
- Решение: деплой к первому клиенту
