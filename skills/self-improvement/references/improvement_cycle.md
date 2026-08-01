# Improvement Cycle — Generation → Application → Verification → Learning

## Полный цикл (внедрён 2026-07-30)

### 1. Generation — self_improvement_loop
- Запускается ежедневно 05:00 (крон)
- Читает: verified_fixes.db, KC experiences, session logs
- Анализирует: recurring patterns, log error clusters, domain failure rates, white spots
- Генерирует: `cache/improvement_suggestions.json` (2000+ suggestions)
- Event: `event_beat("new_suggestions_ready")`

### 2. Application — suggestion_applier
- Запускается по событию `new_suggestions_ready` ИЛИ крон каждые 6ч
- Читает: `improvement_suggestions.json`
- Фильтрует: severity in (critical, high), не применённые ранее
- Применяет топ-5 через fix dispatch:
  - `command` → `command_guard.py` (pre-flight validation)
  - `log_tool_error` → `tool_guard.py` (@with_recovery)
  - `log_unknown` → `unknown_classifier.py` (auto-classification)
  - `domain_failure_pattern` → `domain_failure_guard.py` (HIGH_RISK_DOMAINS)
  - `log_network_*` → `network_guard.py` (circuit breaker)
- Безопасность: `.bak` перед изменением, `MAX_PER_CYCLE=5`, timeout 10 мин

### 3. Verification — verify_changes
- `python -m py_compile <file>` — синтаксис
- Специфичные тесты для каждого guard:
  - `command_guard` → `validate_command()` tests
  - `network_guard` → circuit breaker open/half-open tests
  - `tool_guard` → @with_recovery retry/fallback tests
  - `unknown_classifier` → `classify_unknown()` tests
  - `domain_failure_guard` → `is_high_risk_domain()` tests
- Интеграция: `autonomy_cycle.py --dry` + heartbeat check

### 4. Learning — фиксация результатов
- Успех: запись в `verified_fixes.db` + `applied_suggestions.json` (applied[]) + `event_beat("suggestion_applied")`
- Неудача: откат из `.bak` + `applied_suggestions.json` (failed[]) + `event_beat("suggestion_failed")` + failure counter
- Self-improvement loop читает обновлённые данные на следующем цикле

## Результат первого цикла (2026-07-30)

| Stage | Result |
|-------|--------|
| Generation | 2272 suggestions (14 critical, 7 high) |
| Application | 3/5 critical applied successfully |
| Verification | py_compile + guard-specific tests passed |
| Learning | 3 entries in applied_suggestions.json, verified_fixes.db updated |

## Ключевые файлы

| File | Role |
|------|------|
| `scripts/self_improvement_loop.py` | Generation |
| `scripts/suggestion_applier.py` | Application |
| `scripts/suggestion_consumer.py` | Event consumer (triggers applier) |
| `scripts/ripple_consumer.py` | Event consumer (on_suggestions_ready) |
| `scripts/chain_heartbeat.py` | Event bus (event_beat, system_status) |
| `cache/improvement_suggestions.json` | Generation output |
| `cache/applied_suggestions.json` | Application log |
| `cache/verified_fixes.db` | Learning store |