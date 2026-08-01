# Procedural Skills Format

## Формат записи

```markdown
## TRIGGER: описание условия
ACTION:
1. Шаг 1
2. Шаг 2
3. Шаг N
RECORD: feedback_store + ALERTS.md (опционально)
```

## Примеры

### TRIGGER: Порт мёртв
ACTION:
1. Проверить процесс
2. Если мёртв — перезапустить
3. Проверить健康
RECORD: feedback_store

### TRIGGER: Disk usage > 80%
ACTION:
1. Найти файлы > 100MB
2. Удалить кэш если есть
3. Логировать что удалено
RECORD: feedback_store

### TRIGGER: Cron job error 3 раза подряд
ACTION:
1. Перезаписать next_run на +1 час
2. Логировать ошибку
3. Уведомить пользователя
RECORD: feedback_store + ALERTS.md

## Правила

1. **Только детерминированные действия.** Если нужно решать — это event-driven.
2. **Максимум 5 шагов.** Если больше — разбить на под-триггеры.
3. **Всегда логировать.** Даже если успех.
4. **RECORD обязателен.** Без лога — нет обратной связи.
5. **ALERTS.md для критических.** Timeout, мёртвый процесс, потеря данных.

## Движок

`scripts/procedural_executor.py` — проверяет триггеры, выполняет, логирует.

Запуск:
```bash
python scripts/procedural_executor.py          # Check all triggers
python scripts/procedural_executor.py --status # Show status
```

## Интеграция с daemon

Добавить в daemon.py перед основным циклом:
```python
# Procedural reflexes — без LLM
from procedural_executor import check_all_triggers
check_all_triggers()
```
