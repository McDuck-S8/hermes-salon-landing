# Actionable Breakdown: 11 YouTube Videos → Hermes Agent & Лендинг Косметолога

**Дата:** 2026-07-29  
**Цель:** Извлечь конкретные применимые идеи из описаний 11 видео

---

## 1. lsj9T5y5OP0 — 10 GitHub Repos That Kill Subscriptions (Part 9)

**Суть:** 10 open-source self-hosted альтернатив платным сервисам.

**Что применимо к Hermes:**

- **Invoice Ninja** — можно интегрировать для выставления счетов клиентам CPA-бота. `delegate_task` на создание инвойса через API.
- **Pi-hole** — уже косвенно: Hermes gateway использует DNS для прокси. Если на сервере стоит Pi-hole — убрать рекламу в Telegram/каналах.
- **Сам паттерн:** для каждого платного сервиса в Hermes (API-прокси, VPS) надо держать open-source fallback.

**Что применимо к лендингу косметолога:**

- **draw.io** — схемы процедур на лендинге (бесплатно vs Visio/Lucidchart)
- **ONLYOFFICE** — прайс-листы в .docx на сайте
- **darktable** — обработка фото "до/после" бесплатно

---

## 2. bYaw3Nwqzn0 — Matt Pocock Skills → Никита Велс (КЛЮЧЕВОЕ ДЛЯ HERMES)

**Суть:** Пайплайн из 4 Claude Code скиллов (Grill Me → To Spec → To Tickets → Implement) + Wayfinder + Автопилот. Прямое пересечение с Hermes skills: brainstorming, writing-plans, subagent-driven-development.

**Подробный разбор скиллов Покока:**

| Скилл | Что делает | Аналог в Hermes | Что надо сделать |
|-------|-----------|----------------|------------------|
| Grill Me | Агент допрашивает пользователя, пока не поймёт задачу | `brainstorming` skill — но у нас нет формального "допроса" | **Создать skill `grill-me`** — сценарий из 5-10 итеративных вопросов для уточнения задачи |
| To Spec | Превращает ответы в спецификацию | `writing-plans` — но без промежуточного шага "spec" | **Дополнить `writing-plans`** шагом генерации spec из Q&A |
| To Tickets | Нарезает spec на тикеты методом Tracer Bullet (1 тикет = 1 контекстное окно) | `subagent-driven-development` разбивает на таски | **Дополнить `subagent-driven-development`** указанием Tracer Bullet: каждый тикет ≤ одно контекстное окно |
| Implement | TDD + код-ревью после каждой задачи | `subagent-driven-development` уже делает 2-stage review | Уже есть. OK. |
| Wayfinder | Для больших проектов — навигация по коду | Аналога нет | **Создать skill `wayfinder`** — интеграция с tree-sitter/ctags для обзора кодовой базы |
| **Автопилот (скилл Велса)** | Весь пайплайн одной командой: опрос → spec → тикеты → субагенты в чистых контекстах | Нет аналога | **СОЗДАТЬ СКИЛЛ `autopilot`** — ключевой! |

### Конкретные действия для Hermes:

#### 2.1 Создать skill `autopilot`

**Файл:** `skills/autopilot/SKILL.md`

Логика:
1. Принимает одно предложение задачи от пользователя
2. Запускает Grill Me (5 вопросов: цель, критерии успеха, ограничения, tech stack, окружение)
3. Генерирует spec в `docs/superpowers/specs/<date>-<topic>.md`
4. Нарезает на тикеты (1 тикет = 1 задача ≤ 1 контекстное окно)
5. Каждый тикет запускает `delegate_task(goal=..., context=spec+тикет, toolsets=...)` в чистом контексте
6. После каждого тикета — spec review + quality review

```python
# Пример логики autopilot (execute_code):
steps = [
    "grill_me() → запись ответов",
    "to_spec(answers) → сохранение в docs/superpowers/specs/",
    "to_tickets(spec) → список из N тикетов",
    "for ticket in tickets: delegate_task(goal=ticket, context=spec)"
]
```

#### 2.2 Создать skill `grill-me`

**Файл:** `skills/grill-me/SKILL.md`

Сценарий вопросов:
1. "Что именно нужно сделать? Опиши задачу в 1-2 предложениях"
2. "Кто будет использовать результат? Какие у них потребности?"
3. "Какие критерии успеха? Как поймём, что задача сделана правильно?"
4. "Есть ли ограничения по tech stack, времени, бюджету?"
5. "Что уже есть? Какие файлы/сервисы затрагивает задача?"

#### 2.3 Создать skill `wayfinder`

**Файл:** `skills/wayfinder/SKILL.md`

Интеграция c `ripgrep` / `tree-sitter`:
```bash
# Анализ структуры проекта
find . -name "*.py" -type f | head -50
rg -l "def " --type py | head -30

# Поиск интерфейсов
rg "class .*:" --type py
rg "def .*\(.*\) ->" --type py
```

#### 2.4 Дополнить `writing-plans`

Добавить шаг "Generate Spec from Requirements":
```markdown
### Шаг 0: Generate Spec
- Read user requirements
- Generate structured spec: goal, architecture, tech stack, files, interfaces
- Save to `docs/superpowers/specs/<date>-<topic>.md`
```

---

## 3. bYCNNJGCnl8 — OpenSEO (Semrush Alternative)

**Суть:** Self-hosted SEO-инструмент с Docker + MCP integration.

**Что применимо к Hermes:**

- **MCP integration у OpenSEO** — можно подключить как MCP-сервер в `hermes mcp add openseo --url http://localhost:3000`. Тогда Hermes сможет:
  - Искать ключевые слова для SEO-текстов
  - Анализировать конкурентов
  - Проверять site health

- **DataForSEO API** — $0.01/запрос. Можно использовать для SEO-аудита сайтов, которые Hermes генерирует (лендинги, микро-сайты)

**Что применимо к лендингу косметолога:**

- Запустить OpenSEO на сервере → keyword research по "косметолог", "инъекции", "уход за лицом"
- Rank tracking для позиций лендинга
- Competitor analysis — у кого какие ключевые слова в топе

### Конкретные действия:

```bash
# 1. Поднять OpenSEO
docker run -d -p 3000:3000 --name openseo every-app/open-seo

# 2. Подключить к Hermes как MCP-сервер
hermes mcp add openseo --url http://localhost:3000/mcp

# 3. Запросить у Hermes SEO-аудит лендинга
# Через MCP: OpenSEO предоставляет search volume, keyword gap, backlinks
```

---

## 4. hCmOqPO3e9M — Что использую для заработка (UBT, нейросети, дейтинг)

**Суть:** anti-detect browser + proxy + accounts + virtual cards + ZennoPoster + Grok.

**Что применимо к Hermes:**

- **Anti-detect browser (Vision)** — можно подключить через `browser` toolset с прокси. Hermes и так поддерживает Browserbase/Camofox.
- **Grok** — уже есть как provider (xAI). `hermes model` → xAI/Grok.
- **Виртуальные карты (Multicards)** — полезно для оплаты API-ключей без российской карты.

**Что применимо к лендингу косметолога:**

- Тестировать лендинг в разных браузерных профилях (через Vision anti-detect)
- Смотреть, как лендинг выглядит на разных устройствах

---

## 5. vZTxDqOTCmk — Dewey Agent: $5K/mo Managed AI Agents (ВАЖНО)

**Суть:** Dewey — личный агент Ника Василеску с cloud computer, phone, email, payment card, password vault. Развёртывание агентов за 48 часов. Модель $5K/mo через B2B2B reseller.

**Подробный разбор:**

| Компонент Dewey | Что делает | Аналог в Hermes | Что сделать |
|----------------|-----------|-----------------|-------------|
| Cloud computer | ВМ для агента | `terminal(backend=ssh/modal)` | **Настроить Modal backend** для автономных агентов |
| Cloud phone | Номер для звонков | Нет | **Исследовать Vapi MCP** (уже есть skill!) |
| Cloud email | Почтовый ящик | Gateway Email | **Настроить email gateway** |
| Payment card | Карта для оплат | Нет | Пока не нужно |
| Password vault | Хранение паролей | Нет | **Создать skill `agent-vault`** — шифрованное хранение через `cryptography` |
| Orgo платформа | UI для агентов | Gateway Telegram/Discord | Уже есть, но можно расширить |

### Конкретные действия для Hermes:

#### 5.1 Создать skill `dewey-agent-pattern`

**Файл:** `skills/dewey-agent-pattern/SKILL.md`

Паттерн развёртывания managed agent за 48 часов:
1. Discovery-транскрипт (аналог Grill Me) — 2 часа
2. Определение стека — 4 часа
3. Сборка агента — 24 часа
4. Тестирование — 12 часов
5. Подключение клиента — 6 часов

#### 5.2 B2B2B Reseller Model

Модель $5K/mo:
- Hermes агент → клиент → клиенты клиента
- Клиент платит $5K/mo за агента
- Клиент перепродаёт агента своим клиентам
- Hermes получает recurring revenue

**Пример для косметолога:**
- Создать агента-запись для косметолога (бот в Telegram)
- Косметолог платит $200-500/mo
- Косметолог предлагает бота своим клиентам для записи
- Hepdes получает комиссию

#### 5.3 Настроить Vapi MCP для голосовых звонков

```bash
# Уже есть skill vapi-voice-calls
skill_view(name='vapi-voice-calls')
# Использовать для звонков клиентам косметолога
```

---

## 6. RfoMhAWbibU — Local AI Hardware Guide

**Суть:** Memory bandwidth > FLOPS, KV cache, quantization, MoE.

**Что применимо к Hermes:**

- **Ollama** для локального запуска моделей — `hermes model` можно настроить на local LLM через Ollama
- **llama.cpp** — для inference на CPU/GPU
- **KV cache quantization (8-bit key / 4-bit value)** — экономит 60% VRAM на длинных контекстах

**Конкретные действия:**

```bash
# 1. Установить Ollama
ollama pull qwen3:14b

# 2. Настроить Hermes на локальную модель
hermes config set model.default "ollama/qwen3:14b"
hermes config set model.provider "ollama"

# 3. Для стека косметолога: локальный AI для обработки фото до/после
# segment-anything-model (SAM) — уже есть skill!
```

**Когда локальный AI выигрывает:**
- Конфиденциальные данные (фото клиентов)
- Лаг/отсутствие интернета
- Долгие batch-обработки
- Специфические модели (SAM для сегментации фото)

---

## 7. QOBXFCYYMvk — Litestream + SQLite: Scale to 1M Users

**Суть:** SQLite + Litestream вместо Postgres. 20μs vs 1ms latency. Expensify: 4M QPS на SQLite.

**Что применимо к Hermes:**

- **Hermes уже использует SQLite** (state.db, knowledge_cube.db). Litestream даёт:
  - Бекап в реальном времени
  - Streaming replication
  - S3/Cloudflare R2 как storage

- **Конкретно:**
  ```bash
  # Установить Litestream
  # Настроить replication state.db → S3
  # Автоматический бекап knowledge_cube.db
  ```

**Что применимо к лендингу косметолога:**

- SQLite для хранения заявок с лендинга (если сайт статический → Formspree/Web3Forms лучше)
- Если свой бэкенд — SQLite + Litestream дешевле и быстрее Postgres

### Конкретные действия:

```bash
# 1. Установка Litestream
go install github.com/benbjohnson/litestream@latest

# 2. Конфиг ~/.litestream.yml
dbs:
  - path: /d/Portable_Soft/hermes/state.db
    replicas:
      - url: s3://my-bucket/hermes-state.db
  - path: /d/Portable_Soft/hermes/knowledge_cube.db
    replicas:
      - url: s3://my-bucket/hermes-kc.db
```

---

## 8. wRowrEeKJzk — Обход Блокировки YouTube, Discord (Без VPN)

**Суть:** GoodbyeDPI / Zapret — обход DPI-блокировок.

**Что применимо к Hermes:**

- **Прямое применение:** Hermes gateway на Windows уже использует SOCKS5/HTTP прокси для Telegram. Zapret/GoodbyeDPI может помочь, если прокси нестабилен.
- **Альтернатива:** если SOCKS5 падает, можно:
  1. Установить Zapret (`service.bat`)
  2. Настроить `telegram.proxy_url: ""` (без прокси) — Zapret сам обходит блокировки
  3. Тестировать: `curl -s --connect-timeout 8 https://api.telegram.org`

**Что применимо к лендингу косметолога:**

- Если лендинг хостится на GitHub Pages, а клиенты из РФ — доступ будет и так
- Для YouTube-виджетов на лендинге — Zapret может не работать (нужен прокси)
- **Рекомендация:** не использовать YouTube-виджеты на лендинге для РФ-аудитории

---

## 9. UsZWycrlVVA — Top 10 AI Repos You Should Know

**Суть:** 10 open-source AI репозиториев для self-hosted AI stack.

**Что применимо к Hermes:**

Без полного текста (617 chars), но типичные кандидаты:
- **Ollama** — уже используем
- **llama.cpp** — уже есть skill
- **vLLM** — для production serving
- **DSPy** — уже есть skill!
- **Hugging Face Hub** — уже есть skill

**Проверить, какие из 10 репозиториев уже интегрированы как skills:**

```bash
skills_list | grep -i "ollama\|llama\|vllm\|dspy\|hf"
```

---

## 10. _bEEdgfiE0w — 3 бизнес модели через ИИ (Atoms.dev)

**Суть:** Atoms.dev — платформа для создания AI-приложений без кода. В видео: AI для барбершопа (selfie → рекомендация), генератор детских сказок, AI-нутрициолог.

**Что применимо к лендингу косметолога:**

**ПРЯМОЕ ПРИМЕНЕНИЕ №1 — AI Skin Analyzer:**

```markdown
### Фича для лендинга косметолога: "AI-анализ кожи"
1. Клиент загружает selfie
2. Модель (SAM + классификатор) анализирует: тип кожи, проблемные зоны
3. Выдаёт рекомендацию: какие процедуры подходят
4. Кнопка "Записаться на консультацию"

Технологии:
- segment-anything-model (SAM) — уже есть skill
- CLIP или ResNet классификатор
- FastAPI бэкенд
```

**Что применимо к Hermes:**

- **Atoms.dev** можно использовать как low-code платформу для прототипирования
- Альтернатива: Dify / Langflow (self-hosted)

### Конкретные действия:

```bash
# 1. Настроить SAM для сегментации кожи на фото
skill_view(name='segment-anything-model')

# 2. Создать pipeline: upload photo → SAM segmentation → classify → recommend
# Использовать delegate_task для асинхронной обработки

# 3. На лендинге: форма загрузки фото + AJAX запрос к FastAPI
```

**Сравнение с atoms.dev для косметолога:**

| Что делает | На atoms.dev | На Hermes |
|-----------|-------------|-----------|
| Selfie → AI рекомендация | Визуальный билдер | RPA: SAM + CLIP + FastAPI |
| Генерация текстов | Claude/GPT встроен | `delegate_task` к LLM |
| Деплой | Встроенный | GitHub Pages + Modal |
| Цена | Платная подписка | Бесплатно (self-hosted) |

---

## 11. LUfe9JvjJws — Полная АВТОМАТИЗАЦИЯ Pinterest Аккаунта

**Суть:** Multi-account Pinterest farm: Android Cloud Phones + anti-detect browser + массовый постинг + bulk scheduling.

**Что применимо к лендингу косметолога:**

**ПРЯМОЕ ПРИМЕНЕНИЕ №2 — Pinterest traffic для лендинга:**

1. Создать Pinterest board "Уход за лицом", "Косметология", "Anti-age"
2. Генерировать AI-пины (before/after, советы, процедуры)
3. Bulk upload через Pinterest API
4. Трафик → лендинг косметолога
5. Монетизация: запись на процедуры

**Конкретные действия:**

```bash
# 1. Получить Pinterest API токен (через developer app)
# 2. Создать skill `pinterest-automation`
#    - Генерация пинов через Stable Diffusion / DALL-E
#    - Bulk upload через Pinterest REST API
#    - Планирование постинга (cron job Hermes)
#    - Трекинг кликов в лендинг

# 3. Настроить cron job:
hermes cron create "every 6h" --skill pinterest-automation \
  --delivery telegram \
  --prompt "Generate and post 5 new Pinterest pins for cosmetology landing page"
```

**Что применимо к Hermes:**

- **Android Cloud Phones** — можно через `mobile-mcp` skill (уже есть!)
- **Multi-login антидетект** — Camofox/Browserbase в `browser` toolset
- **Bulk scheduling** — `cronjob` toolset уже есть
- **Multi-account management** — можно сделать skill `social-farm` для управления аккаунтами

---

# ИТОГ: План первоочередных действий

## Для Hermes Agent

| # | Действие | Файлы | Приоритет |
|---|---------|-------|-----------|
| 1 | **Создать skill `autopilot`** | `skills/autopilot/SKILL.md` | 🔴 High |
| 2 | **Создать skill `grill-me`** | `skills/grill-me/SKILL.md` | 🔴 High |
| 3 | **Создать skill `wayfinder`** | `skills/wayfinder/SKILL.md` | 🟡 Medium |
| 4 | **Дополнить `writing-plans`** → шаг Generate Spec | `skills/writing-plans/SKILL.md` | 🔴 High |
| 5 | **Создать skill `dewey-agent-pattern`** | `skills/dewey-agent-pattern/SKILL.md` | 🟡 Medium |
| 6 | **Настроить Litestream** для бекапа SQLite | `~/.litestream.yml` | 🟢 Nice |
| 7 | **Подключить OpenSEO MCP** | `hermes mcp add openseo` | 🟡 Medium |
| 8 | **Создать skill `pinterest-automation`** | `skills/pinterest-automation/SKILL.md` | 🟡 Medium |
| 9 | **Проверить интеграцию Vapi MCP** для звонков | `skill_view(name='vapi-voice-calls')` | 🟢 Nice |
| 10 | **Настроить Modal backend** для автономных агентов | `hermes config set terminal.backend` | 🟡 Medium |

## Для лендинга косметолога

| # | Действие | Технологии | Приоритет |
|---|---------|-----------|-----------|
| 1 | **AI Skin Analyzer** — selfie → рекомендация | SAM + CLIP + FastAPI | 🔴 High |
| 2 | **SEO-аудит через OpenSEO** | OpenSEO + DataForSEO | 🔴 High |
| 3 | **Pinterest traffic pipeline** | Pinterest API + cron job | 🔴 High |
| 4 | **Telegram booking agent** | Telegram bot + Hermes gateway | 🟡 Medium |
| 5 | **AI генерация before/after** | Stable Diffusion + comfyui | 🟡 Medium |
| 6 | **Voice-консультация через Vapi** | Vapi MCP + Twilio | 🟢 Nice |

## Синергия: что объединяет оба направления

```
Pinterest → лендинг → AI Skin Analyzer → Telegram bot → запись
     ↑                          ↑
(cron + Pinterest API)    (SAM + FastAPI)
     ↑                          ↑
  Hermes agent              Hermes agent
     ↕                          ↕
   skills/                   delegate_task
   pinterest-automation       segment-anything-model
```

**Описание синергии:**
1. Hermes cron job генерирует пины для Pinterest
2. Трафик с Pinterest идёт на лендинг косметолога
3. На лендинге AI Skin Analyzer (SAM + классификатор) анализирует фото
4. Клиент получает рекомендацию + кнопка "Записаться"
5. Telegram bot (Hermes gateway) обрабатывает запись
6. Vapi MCP звонит клиенту для подтверждения
7. Всё это managed agent за $200-500/mo для косметолога (модель Dewey)

---

## Как начать прямо сейчас

```bash
# 1. Скачать OpenSEO
docker run -d -p 3000:3000 --name openseo every-app/open-seo

# 2. Настроить Pinterest app на developers.pinterest.com
# 3. Создать autopilot skill
skill_manage(action='create', name='autopilot', content=...)

# 4. Дополнить subagent-driven-development
patch SKILL.md → добавить Tracer Bullet, добавить шаг Generate Spec

# 5. Настроить Litestream для бекапа
# 6. Создать pinterest-automation skill
# 7. Запустить cron job для Pinterest
```

**Ссылки на существующие skills, которые уже покрывают часть:**
- `segment-anything-model` — SAM для AI Skin Analyzer
- `vapi-voice-calls` — голосовые звонки
- `cpa-landing-generator` — генерация лендинга
- `telegram-bot-integration` — Telegram бот
- `comfyui` — генерация before/after фото
- `opencode-zen` / `claude-code` — основные модели

---

*Сгенерировано на основе 11 описаний YouTube видео из /d/Portable_Soft/hermes/cache/yt_descs/*
