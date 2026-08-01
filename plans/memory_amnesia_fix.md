# План: Защита от амнезии MEMORY.md

## Проблема
MEMORY.md пустой (5 строк из 52). Агент теряет контекст между сессиями.
Причина: нет автоматического механизма записи в MEMORY.md.

## Корневые причины
1. Нет скрипта который пишет в MEMORY.md
2. memory tool не используется агентом (context compaction)
3. memory_extractor.py не существует
4. dream-memory отключена от MEMORY.md

## Решения

### 1. MEMORY_GUARD (script) — автозапись при изменениях
Файл: scripts/memory_guard.py
- Запуск: перед каждым ответом агента
- Проверяет: если MEMORY.md < 20 строк → алерт
- Автодобавляет: ключевые факты из последних файлов
- Cron: каждые 30 минут

### 2. BOOT_MEMORY_CHECK (session_boot.py)
- Step 0: проверить MEMORY.md размер
- Если < 10 строк: загрузить из backup
- Если < 20 строк: добавить system state из AGENTS.md

### 3. memory_extractor.py (новый скрипт)
- Запуск: после каждого завершения сессии
- Извлекает: ключевые решения, ошибки, предпочтения
- Формат: declarative facts (не imperative)
- Цель: MEMORY.md всегда содержит актуальный контекст

### 4. dream-memory → MEMORY.md bridge
- dream-memory консолидирует сессии
- Результат пишется в MEMORY.md (не в data/dream-memory/)
- Cron: ежедневно в 3:00

### 5. MEMORY.md size watchdog
- Файл: scripts/memory_watchdog.py
- Проверяет: размер MEMORY.md
- Если < 10 строк: emergency alert
- Если > 200 строк: archive old entries
- Cron: каждые 6 часов

## Приоритеты
1. 🔴 memory_guard.py — НЕМЕДЛЕННО (запускать перед каждым ответом)
2. 🔴 BOOT_MEMORY_CHECK — НЕМЕДЛЕННО (при старте сессии)
3. 🟡 memory_extractor.py — сегодня
4. 🟡 dream-memory bridge — сегодня
5. 🟢 memory_watchdog.py — завтра

## Верификация
- После внедрения: MEMORY.md всегда > 20 строк
- При старте сессии: контекст загружается из MEMORY.md
- При завершении сессии: ключевые факты сохраняются
