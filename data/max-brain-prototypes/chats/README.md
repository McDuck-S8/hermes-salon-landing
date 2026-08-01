# 🏠 MAX-BRAIN MEMORY — ДОМ

> **Главный принцип: ВСЯ инфа в памяти, ничего не раскидано.**

## 📁 СТРУКТУРА КОРНЯ

```
memory/
├── index.json          ← Главный индекс всего дома (авто)
├── housekeeper.py      ← Чистильщик (python housekeeper.py --dry/--active)
├── housekeeper_lessons.md ← Уроки от чистки
├── soul_log.md         ← Лог души
│
├── state/              ← Состояние системы (16 файлов)
├── tasks/              ← Задачи (активные, выполненные, очереди)
├── logs/               ← Все логи (changes, errors, meta, scam_checks...)
├── lessons/            ← Уроки из ошибок
├── graph/              ← Графы (tool_graph, knowledge_graph...)
├── insights/           ← Инсайты
├── checks/             ← Чекпоинты
├── reflections/         ← Саморефлексии
├── status/             ← Статусы системы
│
├── autonomy/           ← Автономность (goals, improvements, priorities, triggers)
├── backups/            ← Бэкапы (включая backup/trash/)
├── context/            ← Контекст (emotions, patterns, conversations...)
├── insights/           ← Инсайты
├── graph/              ← Графы
│
├── a2a/                ← Agent-to-Agent коммуникация
├── agentic_context/    ← Контекст агентов
├── credentials/        ← Токены, пароли
├── chroma/             ← Векторная БД
├── chromadb/           ← ChromaDB
├── council/            ← Совет агентов
├── diagnostics/        ← Диагностика
├── evolver/            ← Эволюция
├── experts/            ← Эксперты
├── knowledge/          ← База знаний (WIKI, RAW...)
├── metacognition/      ← Метакогниция
├── patterns/           ← Паттерны
├── persistence/       ← Персистентность
├── profiles/           ← Профили
├── reflexes/          ← Рефлексы
├── search_cache/       ← Кэш поиска
├── sessions/           ← Сессии
├── visions/            ← Видения
└── (другие папки)      ← см. index.json
```

## 🎯 БЫСТРЫЙ ДОСТУП

| Что нужно | Где |
|-----------|-----|
| Текущее состояние | `state/system.json` |
| Задачи | `tasks/` |
| Логи | `logs/` |
| Уроки | `lessons/lessons-learned.md` |
| Ошибки | `lessons/errors.md` |
| Графы | `graph/` |
| Инсайты | `insights/` |
| Автономность | `autonomy/` |
| Индекс всего | `index.json` |

## 🧹 HOUSEKEEPER — Чистка дома

```bash
# Проверить что будет
python memory/housekeeper.py --dry

# Применить
python memory/housekeeper.py --active
```

**Правила:**
1. Новый файл → сразу в правильную папку (state/, tasks/, logs/, lessons/)
2. Удалить → только через backup + урок в housekeeper_lessons.md
3. Ничего не раскидывать в корень memory/
4. Автозапуск: autonomous_loop проверяет порядок каждый запуск

## 📝 INDEX.JSON

`index.json` — автоиндекс всего дома. Обновляется после каждой чистки.
Формат: `{path: {size, modified}}`

## ⚠️ НЕ ТРОГАТЬ

- `index.json` — генерируется автоматически
- `housekeeper.py` — не редактировать напрямую
- `soul_log.md` — лог души

---

**Версия дома: v14.11 (2026-05-03)**
**Housekeeper: v1.0**