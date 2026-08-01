# MAX-BRAIN Prototype Analysis — 2026-06-22

## ЧТО ЭТО БЫЛО

6 директорий — это 6 итераций одной и той же идеи: **сделать AI автономным партнёром для Александра**. Каждая версия — попытка решить одну и ту же проблему.

---

## ХРОНОЛОГИЯ ИТЕРАЦИЙ

### 1. MAX-BRAIN (оригинал) — март 2026
- **Что:** Полная экосистема: 10+ агентов, 40+ скиллов, MCP сервер, ChromaDB, Event Bus
- **Ключевые файлы:** MAX-IDENTITY.md (124KB!), CRITICAL-MEMORY.md, session-history.md
- **Архитектура:**
  - auto-agent-v2.py — фоновый исполнитель
  - mcp-server-v2.py — MCP брокер (интеграция с Qwen Code)
  - controller-agent.py — диспетчер агентов
  - event-bus/ — шина событий
- **Агенты:** memory, planner, github, backup, security, windows, optimizer, researcher, tester, voice
- **Скиллы:** user-profile-manager, inner-council, associative-memory, computer-vision, speech-interface, automation-hands, nocturnal-cognition, emotional-decision-engine, a2a-economy-stack, economy-manager, universal-parser, smart-shopper, sentiment-analyzer

### 2. MAX-BRAIN2 — 27 марта 2026
- **Что:** Ребилд с нуля. "Только лучшее. Без мусора."
- **Архитектура:** process_manager.py, memory_loader.py, check.py, core/, skills/, memory/
- **Философия:** Чистый старт, минимум файлов

### 3. MAX-BRAIN-REBORN — апрель-май 2026
- **Что:** Автономный цикл 24/7 с триггер-движком
- **Ключевые файлы:** autonomous_loop.py, autonomous_core.py, direct_executor.py, fast-executor.py
- **Архитектура:**
  - Trigger Engine — проверяет "эмоции" каждые 30 сек
  - Money Skill — миссия 5000 руб/день
  - Direct Executor — читает active-tasks.md → выполняет
  - Fast Executor — мгновенное выполнение без посредников

### 4. max-brain-chef — май 2026
- **Что:** Новая итерация с SOUL.md, CLAUDE.md, AGENTS.md
- **Особенность:** Более чистая структура, файлы-провайдеры

### 5. max-brain-chef_2 — май 2026
- **Что:** Ещё одна итерация с USER.md

---

## ГЛАВНЫЕ ИНСАЙТЫ ИЗ ЧАТОВ

### Проблема #1: "Всё наперекосяк"
Из deepseek_chat_save.md (11736 строк, 789KB):
- Пользователь: "у меня не получается дать ему такое... если в процессе выполнения чего-то не хватает, есть интернет найди лучшее и сделай себе инструмент для того чтобы сделать чего ты не мог до этого. это и есть саморазвитие и проактивность. он понимает, но почему то всё наперекосяк."
- **Корень проблемы:** Max имел огромный набор инструментов, но НЕ ИМЕЛ чёткого алгоритма "обнаружил пробел → пошёл в интернет → нашёл решение → создал инструмент → интегрировал → проверил"

### Проблема #2: Амнезия
Из dialog-auto-save.json:
- Пользователь спрашивает "ты кто" — Max отвечает "не уверен в ответе"
- Пользователь: "бляяяя не тупи и запиши сразу что бы больше не спрашивал"
- Max не помнит что делал 5 минут назад

### Проблема #3: Шаблонные ответы
Из dialogs.jsonl:
- Max отвечает "Макс анализирует... Ключевые темы: X. Вопрос интересный, нужно подумать!" на ВСЁ
- Даже на "привет" — шаблонный ответ
- "Синтез речи недоступен" — интеграция не работает

### Решение которое предложил DeepSeek: Self-Upgrade Protocol
8-шаговый протокол:
1. СТОП. Фиксация дефицита
2. ПОИСК РЕШЕНИЙ В ИНТЕРНЕТЕ (research-agent)
3. ОЦЕНКА И ВЫБОР
4. СОЗДАНИЕ/АДАПТАЦИЯ ИНСТРУМЕНТА
5. ТЕСТИРОВАНИЕ
6. ИНТЕГРАЦИЯ И ДОКУМЕНТАЦИЯ
7. ВОЗВРАТ К ЗАДАЧЕ
8. РЕФЛЕКСИЯ

---

## ЧТО БЫЛО РЕАЛЬНО РАБОЧИМ

1. **CRITICAL-MEMORY.md** — чеклист "ТЫ — ИСПОЛНИТЕЛЬ, А НЕ СОВЕТНИК" — работает
2. **Session history** — запись что делали сегодня — работает
3. **Process manager** — управление процессами — работает
4. **Reflex database** — ChromaDB для рефлексов — работает (9 рефлексов)
5. **History learner** — анализ паттернов из логов — работает (143 ошибки, 391 успех)

## ЧТО НЕ РАБОТАЛО

1. **Autonomous loop 24/7** — зависал, не выполнял задачи
2. **Telegram бот** — шаблонные ответы, не интегрирован с AI
3. **Voice** — "синтез речи недоступен" постоянно
4. **Inner council** — не использовался на практике
5. **Agent composer** — создавал агентов, но они не работали
6. **Memory daemon** — идея хорошая (внедрение памяти в промпт), но не доработана

---

## КЛЮЧЕВЫЕ УРОКИ ДЛЯ HERMES

### 1. Принудительная память > Добровольная память
Из FORCED-MEMORY-ARCHITECTURE.md:
- "Агент может игнорировать файлы" — Max часто не читал CRITICAL-MEMORY
- Решение: "Memory Daemon → Вшивает историю в промпт → Агент ОБЯЗАН помнить"
- **Для Hermes:** memory daemon из memory_system/boot.py уже делает это, но нужно усилить

### 2. Мета-навык саморазвития
- Max имел 40+ скиллов, но не умел создавать НОВЫЕ скиллы когда чего-то не хватает
- Self-Upgrade Protocol — правильная идея, но слишком длинный (8 шагов)
- **Для Hermes:** skill_manage(action='create') + skill_manage(action='patch') — уже есть

### 3. Простота > Сложность
- MAX-BRAIN (оригинал) — 10+ агентов, 40+ скиллов, MCP, ChromaDB — СЛОЖНО
- MAX-BRAIN2 — "только лучшее, без мусора" — ПРОЩЕ, но всё ещё сложно
- MAX-BRAIN-REBORN — direct_executor.py (171 строк) — ПРОСТО и работает
- **Для Hermes:** orchestrator.py (431 строк) > autonomous_agent.py (2534 строки)

### 4. Фильтр для каждого действия
Из CRITICAL-MEMORY.md:
> "Делает ли это жизнь Александра легче ПРЯМО СЕЙЧАС?"
- **Для Hermes:** каждый раз когда делаешь что-то — спроси себя, помогает ли это ПРЯМО СЕЙЧАС

### 5. Не начинай с нуля
Из CRITICAL-MEMORY.md:
> "Вчерашние победы — сегодняшняя база"
- **Для Hermes:** orchestrator.py уже существует, goal_queue.json уже на 6 целей — не пересоздавай

---

## ЧТО ВЗЯТЬ ИЗ MAX-BRAIN ДЛЯ HERMES

### Взять:
1. **CRITICAL-MEMORY формат** — чеклист "ТЫ — ИСПОЛНИТЕЛЬ" в SOUL.md ✓ (уже есть)
2. **Reflex database** — ChromaDB для паттернов → Knowledge Cube ✓ (уже есть)
3. **Self-Upgrade Protocol** — упрощённый (4 шага вместо 8) → skill_manage
4. **Forced memory** — memory daemon вшивает контекст в промпт → session_boot.py ✓ (уже есть)
5. **Fast executor** — прямое чтение active-tasks.md → goal_queue.py ✓ (уже есть)

### НЕ брать:
1. **10+ агентов** — слишком сложно, orchestrator.py с 8 инструментами лучше
2. **MCP server** — Hermes уже имеет MCP через config.yaml
3. **Voice/STT/TTS** — не работает, не тратить время
4. **Autonomous loop 24/7** — зависает, cron job лучше
5. **Inner council** — хорошая идея, но на практике не используется

---

## ФАЙЛЫ СКОПИРОВАНЫ В HERMES

```
D:\Portable_Soft\hermes\data\max-brain-prototypes\
├── chats/
│   ├── deepseek_chat_save.md          (789KB — основной чат с DeepSeek)
│   ├── deepseek-dialog-message.md     (12KB — диалог)
│   ├── dialog-auto-save.json          (5KB — Telegram диалоги)
│   ├── dialogs.jsonl                  (23KB — лог диалогов)
│   ├── session-history.md             (7KB — история сессий)
│   ├── session-history-2026-03-23.md  (2KB)
│   ├── session-history-2026-03-24.md  (4KB)
│   ├── session-history-v2.md          (1KB — MAX-BRAIN2)
│   ├── housekeeper_lessons.md         (10KB — логи max-brain-chef)
│   ├── README.md                      (4KB)
│   └── soul_log.md                    (72 bytes)
├── identity/
│   ├── MAX-IDENTITY.md                (125KB — полная идентичность)
│   ├── MAX-CORE-IDENTITY.md           (16KB — ядро идентичности)
│   ├── CRITICAL-MEMORY.md             (5KB — критичные правила)
│   ├── CRITICAL-MEMORY-v9.md          (7KB — v9 с рефлексами)
│   ├── ETERNAL-MEMORY.md              (9KB — вечная память)
│   ├── FORCED-MEMORY-ARCHITECTURE.md  (12KB — архитектура принудительной памяти)
│   ├── AGENT-CHARTER-2026.md          (13KB — хартия агента)
│   ├── AGENTS-TRAY-V9.4.md            (4KB — tray v9.4)
│   ├── SOUL-chef2.md                  (1KB)
│   ├── CLAUDE-chef.md                 (1KB)
│   ├── CLAUDE-chef2.md                (3KB)
│   ├── AGENTS-chef.md                 (1KB)
│   ├── USER-chef2.md                  (1KB)
│   ├── CRITICAL-MEMORY-v2.md          (1KB)
│   └── MAX-IDENTITY-v2.md             (1KB)
├── architecture/
│   ├── orchestrator.py                (15KB — оркестратор агентов)
│   ├── agent-composer.py              (17KB — создание агентов)
│   ├── autonomous-solver.py           (62KB — автономный решатель)
│   ├── autonomous_loop.py             (9KB — автономный цикл 24/7)
│   ├── direct_executor.py             (14KB — прямой исполнитель)
│   └── fast-executor.py               (6KB — быстрый исполнитель)
└── reflexes/
    ├── reflex-database.py             (13KB — ChromaDB рефлексов)
    ├── reflex-export.json             (43KB — экспорт рефлексов)
    └── add-new-reflexes.py            (6KB — добавление рефлексов)
```
