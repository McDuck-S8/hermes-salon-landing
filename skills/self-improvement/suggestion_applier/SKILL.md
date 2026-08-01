---
name: suggestion_applier
description: "Автоматическое применение критических предложений из self_improvement_loop. Читает improvement_suggestions.json, приоритизирует, применяет фиксы, проверяет, коммитит или откатывает."
trigger: "По событию new_suggestions_ready или по крону (каждые 6 часов)"
usage: suggestion_applier
---

# Suggestion Applier — Автоматическое применение улучшений

Замкнёт цикл самоулучшения: генерация → применение → проверка → обучение.

## Архитектура

```
self_improvement_loop → improvement_suggestions.json
    ↓
suggestion_applier (этот модуль)
    ├── Читает топ-N critical/high предложений
    ├── Для каждого: генерирует/применяет фикс
    ├── Проверяет: syntax + lint + autonomy_cycle
    ├── Успех: фиксирует в verified_fixes.db + applied_suggestions.json
    └── Неудача: откат через .bak, запись в feedback_store
    ↓
chain_heartbeat.event_beat("suggestion_applied" / "suggestion_failed")
```

## Входные данные

- `cache/improvement_suggestions.json` — от self_improvement_loop
- Структура: pattern, count, severity, description, recommended_actions, source

## Алгоритм

### 1. Чтение и приоритизация
- Загрузить suggestions
- Фильтр: severity in (critical, high)
- Сортировка: count DESC
- Взять топ-5 (configurable: MAX_PER_CYCLE=5)

### 2. Применение (execution)
Для каждого suggestion:
- Извлечь recommended_actions или сгенерировать по pattern (шаблоны в `templates/`)
- Типы действий:
  - Создание guard-модуля (command_guard, network_guard, tool_guard)
  - Изменение config.yaml (timeouts, circuit breaker settings)
  - Обёртка существующих вызовов в try/except + retry
  - Обновление скиллов (добавить pre-flight checks)
- Безопасность: копия файла → `.bak` перед изменением

### 3. Проверка (verification)
После каждого изменения:
- `python -m py_compile <file>` — синтаксис
- `pylint/flake8` (если доступны) — стиль
- `python scripts/autonomy_cycle.py --dry` — системная проверка
- Специфичные тесты для guard'ов (если есть)

### 4. Фиксация / Откат
**Успех:**
- Записать в `verified_fixes.db` (pattern, fix_description, tags)
- Записать в `cache/applied_suggestions.json` (applied array)
- Удалить/пометить applied в `improvement_suggestions.json`
- `event_beat("suggestion_applied")`

**Неудача:**
- Восстановить из `.bak`
- Записать в `cache/applied_suggestions.json` (failed array)
- Увеличить failure counter для pattern
- `event_beat("suggestion_failed")`

### 5. Повторение
- Запуск: по событию `new_suggestions_ready` ИЛИ крон каждые 6 часов
- После цикла: полный `autonomy_cycle` для интеграционной проверки

## Интеграция

| Компонент | Взаимодействие |
|-----------|----------------|
| feedback_store | Запись успехов/неудач, веса |
| autonomy_cycle | Проверка после изменений |
| self_improvement_loop | Читает обновлённый suggestions |
| proactive_executor | Дополняет (рестарт кронов если нужно) |
| chain_heartbeat | event_beat для applied/failed |
| tactical_buffer / strategic_db | Новые паттерны → гипотезы |

## Хранилище: cache/applied_suggestions.json

```json
{
  "applied": [
    {"pattern": "command", "timestamp": "...", "files_changed": [...], "status": "success", "verification_result": "..."}
  ],
  "failed": [
    {"pattern": "network_retry", "timestamp": "...", "error": "...", "attempt_count": 1}
  ]
}
```

## Железные правила (безопасность)

1. **Всегда .bak** перед изменением любого файла
2. **Макс 5 предложений за цикл** (MAX_PER_CYCLE)
3. **Таймаут 10 мин** на применение одного предложения
4. **Непонятные действия** (requires_manual) — пропуск, не применение
5. **Откат при любой ошибке верификации**

## Уроки из практики (Pitfalls)

- **Pattern matching на issue_type**: `recurring-*` (verified_fixes) и `log-error-*` (session_logs) — разные источники, но один паттерн. Fix dispatch должен покрывать оба (например, `"command"` и `"log-error-tool_error"`).
- **Target file missing**: `apply_command_guard` ищет `run_command` в `terminal.py`, но функция может называться иначе (`_run` в `action_executor.py`) или отсутствовать. Fallback: создавать standalone guard модуль (`command_guard.py`).
- **Source matters**: `verified_fixes` = структурированные паттерны с `recommended_actions`. `session_logs` = сырой лог, требует NLP классификации (`unknown_classifier.py` с 50+ правилами).
- **Verification**: синтаксис OK (`py_compile`), но semantic проверка нужна для каждого guard типа:
  - `command_guard`: test run проверяет, что опасные команды блокируются
  - `network_guard`: circuit breaker trigger test
  - `tool_guard`: retry + fallback behavior test
  - `unknown_classifier`: classification accuracy на тестовых сообщениях
- **Idempotency**: повторный запуск не должен ломать то, что уже применено (проверка `if not target.exists()` / `if "X" not in content` перед записью).
- **Pre-flight check works**: добавленный `pre_flight_check` в `action_executor.py` успешно блокирует `rm -rf /...` и `dd if=` — semantic тест проходит.
- **Guard modules as templates**: созданные guard-модули (`command_guard.py`, `network_guard.py`, `tool_guard.py`, `unknown_classifier.py`, `config_guard.py`, `domain_failure_guard.py`, `ext_guard.py`) — готовые к переиспользованию шаблоны для будущих паттернов.

## Шаблоны фиксов (scripts/)

- `command_guard.py` — pre-flight валидация команд
- `network_guard.py` — circuit breaker + retry для httpx/telegram/tavily
- `tool_guard.py` — унифицированный error recovery для инструментов
- `config_guard.py` — валидация конфига + HIGH_RISK_DOMAINS
- `unknown_classifier.py` — авто-классификация unknown ошибок
- `domain_failure_guard.py` — domain-level protection

## Ссылки

- `references/pattern_dispatch.md` — логика маппинга issue_type → fixer
- `references/verification_recipes.md` — специфичные тесты для каждого guard

## Запуск

```bash
# Ручной
python scripts/suggestion_applier.py

# По крону (каждые 6 часов) или по событию
# В suggestion_consumer добавить вызов suggestion_applier после on_suggestions_ready
```

## Критерии успеха

- [ ] Модуль применяет ≥1 critical suggestion за цикл
- [ ] Все изменения проходят верификацию (или откат)
- [ ] improvement_suggestions.json сокращается (critical исчезают)
- [ ] verified_fixes.db пополняется успешными кейсами
- [ ] chain_heartbeat показывает suggestion_applied events