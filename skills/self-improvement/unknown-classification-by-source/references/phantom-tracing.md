# Phantom Tracing — Как проявлять фантомов в Entity Engine

Когда Entity Engine ошибочно классифицирует сущность (например, присваивает тип «Человек» серверу, боту или временному идентификатору), **не удаляй** — проследи происхождение.

## Алгоритм

1. **Найти фантомов**: сущности с неверным типом
   ```sql
   SELECT e.id, e.name, e.mention_count FROM entities e
   JOIN entity_types t ON e.type_id = t.id
   WHERE t.name = 'Человек'
   AND e.name NOT IN ('Александр');
   ```

2. **Выяснить происхождение**: для каждого фантома найти что это на самом деле
   - Если имя похоже на ID/хеш (`0f8o`, `c65`, `065`, `25`, `0`) → искать в KC через `SELECT source, raw_text FROM experiences WHERE raw_text LIKE '%name%' LIMIT 3`
   - Если имя похоже на URL/домен (`dc01.steelproxy.com`) → это сервер/прокси
   - Если имя похоже на TG-юзернейм (`@ai_frontier_you`) → это TG-канал
   - Если имя — обычное слово (`echo`, `google`, `workflow`) → это команда/компания/концепт

3. **Создать реальную сущность** с правильным типом
   ```python
   e.execute("SELECT id FROM entity_types WHERE name=?")
   # Если типа нет — создать с правильным TEXT id
   e.execute("INSERT INTO entity_types (id, name) VALUES (?, ?)",
             ('data-source', 'Источник данных'))
   e.execute("INSERT INTO entities (name, type_id, mention_count, ...) VALUES (?, ?, 1, ...)",
             (real_name, type_id, now))
   ```

4. **Создать `phantom_of` связь**
   ```sql
   INSERT INTO relationships (source_entity_id, target_entity_id, relation_type)
   VALUES (<фантом_id>, <реальная_id>, 'phantom_of');
   ```

## Типичные фантомы

| Категория | Примеры | Реальный прообраз |
|-----------|---------|-------------------|
| ID/хеши | `0f8o`, `c65`, `065` | WSL encoding issue, Timestamps |
| Числовые коды | `25`, `0` | HTTP Status, Null/Zero values |
| Прокси/хосты | `dc01` | steelproxy.com |
| TG-каналы | `@ai_frontier_you`, `@neuro_kitchen_ai` | TG-каналы пользователя |
| Боты | `hotelcrimeabot` | Telegram боты отелей |
| Команды | `echo` | shell command |
| Компании | `google` | search engine |
| Инструменты | `babel` | Babel JS |
| Концепты | `workflow` | рабочий процесс |
| NPM-пакеты | `@swarmclawai/...` | AI skill ecosystem |

## Почему это важно

- Фантом — это **сигнал**, не мусор. Если EE ошибочно классифицировала сущность — значит эта сущность существует и важна.
- Удаление фантома = потеря знаний о том, что система взаимодействует с этим объектом.
- `phantom_of` связь сохраняет историю: мы видим что ранее приняли X за Y, но теперь знаем что это Z.
- Отношение `phantom_of` можно использовать в аналитике: «какие сущности чаще всего ошибочно классифицируются» → улучшение алгоритмов EE.

## Статистика после чистки

После применения метода к 16 фантомным «людям»:
- 17 связей `phantom_of` создано
- 13 новых реальных сущностей добавлено (steelproxy.com, WSL encoding issue, TG-каналы пользователя и др.)
- Тип «Человек» сократился с 17 до 1 (только Александр)
