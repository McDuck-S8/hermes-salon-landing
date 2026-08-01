# Cole Medin Research — OKF Bundle

## Обзор

Исследование видео Cole Medin, инструментов OpenSpec, Stripe Minions и Claude Code Workflows.
Дополнительно изучено видео по ссылке https://www.youtube.com/watch?v=jgsDu9MubJM (оказалось другим каналом).

---

## 1. Видео по ссылке jgsDu9MubJM

**Ожидание:** Видео Cole Medin "This AI Agent is Actually Building SaaS Apps"
**Реальность:** Видео "GitHub Repos That Feel Illegal to Know" от канала **Cloud Codes** (14.1k подписчиков)

- Ссылка: https://www.youtube.com/watch?v=jgsDu9MubJM
- Дата: 15 июля 2026
- Длительность: 8:52
- Описание: 10 лучших open-source GitHub репозиториев (бесплатное образование, замена платных приложений, инструменты для разработчиков)

### Все GitHub ссылки из видео Cloud Codes

**Shelf 1: Free Education (Бесплатное образование)**
1. https://github.com/freeCodeCamp/freeCodeCamp — полноценный курс веб-разработки
2. https://github.com/codecrafters-io/build-your-own-x — туториалы по созданию собственных технологий
3. https://github.com/kamranahmedse/developer-roadmap — дорожные карты разработчика
4. https://github.com/ossu/computer-science — бесплатная CS степень
5. https://github.com/EbookFoundation/free-programming-books — коллекция бесплатных книг
6. https://github.com/TheAlgorithms/Python — алгоритмы на Python
7. https://github.com/trekhleb/javascript-algorithms — алгоритмы на JS
8. https://github.com/jwasham/coding-interview-university — подготовка к собеседованиям
9. https://github.com/donnemartin/system-design-primer — системный дизайн

**Shelf 2: Paid-App Killers (Самостоятельный хостинг)**
10. https://github.com/immich-app/immich — self-hosted Google Photos
11. https://github.com/Stirling-Tools/stirling-pdf — PDF редактор
12. https://github.com/localsend/localsend — локальная передача файлов
13. https://github.com/excalidraw/excalidraw — виртуальная белая доска
14. https://github.com/AppFlowy-IO/AppFlowy — Notion-подобное приложение
15. https://github.com/coollabsio/coolify — self-hosted Heroku/Netlify

**Shelf 3: Developer Cheat Codes**
16. https://github.com/public-apis/public-apis — коллекция бесплатных API
17. https://github.com/ripienaar/free-for-dev — бесплатные сервисы для разработчиков
18. https://github.com/ollama/ollama — локальный запуск LLM
19. https://github.com/sindresorhus/awesome — список всего awesome

**Применимость в Hermes:** Репо общего назначения, не связаны с Cole Medin. Ollama уже используется в Hermes.

---

## 2. Cole Medin — Обзор

**YouTube:** https://www.youtube.com/@ColeMedin (217k+ подписчиков)
**GitHub:** https://github.com/coleam00 (7.2k+ followers)
**Сайт:** https://dynamous.ai
**Специализация:** Generative AI, AI Agents, RAG, Claude Code, Context Engineering

### Основные репозитории Cole Medin

### 2.1. Archon
- **Ссылка:** https://github.com/coleam00/Archon
- **Звёзды:** 22.9k
- **Что делает:** Первый open-source конструктор harness для AI-кодинга. Позволяет делать AI-кодинг детерминированным и повторяемым. Создаёт структурированные окружения для Claude Code.
- **Технологии:** TypeScript
- **Применимость в Hermes:** Можно использовать как шаблон для построения harness-системы в Hermes. Archon позволяет создавать "фабрики" агентов кодинга — то, что может быть адаптировано для генерации спецификаций.

### 2.2. Context Engineering Intro
- **Ссылка:** https://github.com/coleam00/context-engineering-intro
- **Звёзды:** 13.7k
- **Что делает:** Введение в Context Engineering — дисциплину проектирования контекста для AI-ассистентов. Включает шаблон .claude/commands, PRP (Product Requirements Prompt) workflow.
- **Структура:**
  - `.claude/commands/generate-prp.md` — генерация PRP
  - `.claude/commands/execute-prp.md` — исполнение PRP
  - `PRPs/templates/prp_base.md` — базовый шаблон PRP
  - `INITIAL.md` — шаблон для feature request
- **Ключевые принципы:**
  - Context Engineering > Prompt Engineering (10x)
  - Большинство ошибок агентов — это ошибки контекста, не модели
  - PRP — это не PRD, а инструкция для AI-кодинг ассистента
- **Применимость в Hermes:** Высокая. Методология PRP и Context Engineering напрямую применимы для улучшения качества генерации кода в Hermes. Можно внедрить `.claude/commands/` в Hermes.

### 2.3. AI Transformation Workshop
- **Ссылка:** https://github.com/coleam00/ai-transformation-workshop
- **Звёзды:** 122
- **Что делает:** Материалы workshop "Principles of Agentic Engineering". Включает:
  - **AI Layer** — второй кодбейз из контекста для AI
  - **PIV Loop** — Plan → Implement → Validate
  - **15 reusable Claude Code commands** (prime, plan, implement, validate, review, create-prd, create-stories и др.)
  - **2 skills** (agent-browser для E2E, pptx-generator)
- **5 Golden Rules:**
  1. Commandify everything
  2. Reduce assumptions — вопросы перед PRD
  3. Context is king — сброс между планированием и реализацией
  4. Git log is memory — частые коммиты
  5. System evolution — каждый баг → улучшение AI layer
- **Применимость в Hermes:** Критически высокая. PIV Loop — готовая методология для Hermes. 15 команд можно адаптировать как skills в Hermes.

### 2.4. Ottomator Agents
- **Ссылка:** https://github.com/coleam00/ottomator-agents
- **Звёзды:** 5.7k
- **Что делает:** Коллекция open-source AI агентов для платформы oTTomator Live Agent Studio. Включает: Pydantic AI agents, AG-UI integration, Langfuse observability, RAG agents.
- **Применимость в Hermes:** Шаблоны агентов (Pydantic AI) можно адаптировать.

### 2.5. Excalidraw Diagram Skill
- **Ссылка:** https://github.com/coleam00/excalidraw-diagram-skill
- **Звёзды:** 4.1k
- **Что делает:** Skill для Claude Code (и любых coding agents) для генерации Excalidraw-диаграмм.
- **Применимость в Hermes:** Можно использовать как образец создания skills для Hermes.

### 2.6. Local AI Packaged
- **Ссылка:** https://github.com/coleam00/local-ai-packaged
- **Звёзды:** 3.7k
- **Что делает:** Пакет для запуска локального AI: Ollama, Supabase, n8n, Open WebUI и др.
- **Применимость в Hermes:** Альтернатива для локального развёртывания. В Hermes уже есть Ollama, но n8n интеграция может быть полезна.

### 2.7. AI Agents Masterclass
- **Ссылка:** https://github.com/coleam00/ai-agents-masterclass
- **Звёзды:** 3.4k
- **Что делает:** Код для серии видео AI Agents Masterclass (LangChain, n8n, RAG и др.)
- **Применимость в Hermes:** Обучающий материал, шаблоны для агентов.

---

## 3. OpenSpec (генератор спецификаций)

### Общая информация
- **GitHub:** https://github.com/Fission-AI/OpenSpec
- **Звёзды:** 60.8k
- **Вилок:** 4.2k
- **Лицензия:** MIT
- **Технологии:** TypeScript (98.7%), Node.js (npm пакет)
- **Сайт:** https://openspec.dev
- **Discord:** https://discord.gg/YctCnvvshC
- **npm:** `@fission-ai/openspec`

### Что делает
OpenSpec — это Spec-Driven Development (SDD) фреймворк для AI-кодинг ассистентов. Позволяет заменить "vibe coding" на структурированный процесс:

1. **Создание proposal** — описание изменений
2. **Генерация spec-файлов** — структурированные требования
3. **Разбивка на tasks** — пошаговый план реализации
4. **Применение** — автоматическая реализация по spec
5. **Архивация** — сохранение истории изменений

### Философия
```
→ fluid not rigid → iterative not waterfall
→ easy not complex → built for brownfield not just greenfield
→ scalable from personal projects to enterprises
```

### CLI команды (OPSX workflow)
| Команда | Описание |
|---------|----------|
| `/opsx:explore` | Исследование проблемы, генерация идей |
| `/opsx:propose` | Создание change proposal со specs, design, tasks |
| `/opsx:apply` | Реализация задач из proposal |
| `/opsx:archive` | Архивация завершённых изменений |

### Структура OpenSpec проекта
```
openspec/
  changes/
    add-dark-mode/
      proposal.md    — почему и что меняем
      specs/         — требования и сценарии
      design.md      — технический подход
      tasks.md       — чеклист реализации
    archive/         — история изменений
```

### Интеграция с AI ассистентами
- Claude Code (через .claude/rules/)
- Cursor (через .cursor/rules/)
- GitHub Copilot (через .github/copilot-instructions.md)
- Codex, Windsurf и любые другие (generic format)

### Рекомендуемые модели
OpenSpec лучше всего работает с высокорезонящими моделями: Codex 5.5, Opus 4.7

### Применимость в Hermes
**Очень высокая.** OpenSpec может быть использован как:
- **Генератор спецификаций** для Hermes skills и workflows
- **Планировщик задач** для сложных фич
- **Система контекстной инженерии** для улучшения качества кода
- **Альтернатива** ручному документированию

Возможные способы интеграции:
1. Установить через `npm install -g @fission-ai/openspec` и использовать CLI
2. Создать Hermes skill, оборачивающий OpenSpec команды
3. Использовать OpenSpec для codebase-wide spec management

### Сравнение с аналогами
| Инструмент | OpenSpec | GitHub Spec Kit | Superpowers |
|------------|----------|-----------------|-------------|
| Философия | Spec-Driven Dev | 4-phase workflow | End-to-end AI coding |
| Для brownfield | ✅ | ❌ (greenfield) | ✅ |
| Команды | CLI | GitHub UI | Claude Code |
| Звёзды GitHub | 60.8k | Н/Д | 45k+ |
| Интеграция | Claude, Cursor, Copilot | GitHub Copilot | Claude Code |

---

## 4. Stripe Minions

### Общая информация
- **Блог:** https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents
- **Аналитика:** https://rywalker.com/research/stripe-minions
- **Видео Cole Medin:** https://www.youtube.com/watch?v=NMWgXvm--to ("Stripe's Coding Agents Ship 1,300 PRs EVERY Week")

### Ключевые показатели
| Метрика | Значение |
|---------|----------|
| PR/неделя | 1,300+ (смержено, ноль человеческого кода) |
| Базовый агент | Fork Goose (Block/open-source) |
| MCP инструментов | ~500 (через "Toolshed") |
| Время развёртывания devbox | 10 секунд |
| CI раундов | максимум 2 |
| Годовая платежная нагрузка | $1+ триллион (код Minions) |

### Как работает
1. **Invocation** — через Slack (основной), CLI, Web
2. **Devbox** — изолированный AWS EC2 sandbox (10s spin-up)
3. **Toolshed MCP** — ~500 внутренних инструментов (доки, тикеты, Sourcegraph)
4. **Agent Loop** — Goose fork
5. **CI** — локальный lint (<5s) → CI (max 2 rounds) → auto-fix
6. **Pull Request** — code review человеком, но код пишет агент

### Blueprints (оркестрация)
Ключевое нововведение Stripe — "Blueprints": гибрид детерминированных workflow-нодов и agentic loops.

```
Slack → Devbox → MCP Server (500 tools) → Agent Loop → Lint → CI → Auto-fix → PR
```

### Применимость в Hermes
- **Прямая:** Ограничена (требует масштаба Stripe)
- **Косвенная:** Высокая — архитектурный паттерн (MCP сервер с инструментами, изолированные sandbox, CI loop) применим для построения agentic системы Hermes
- **Ключевой урок:** Агентам нужны те же инструменты и контекст, что и людям-разработчикам

---

## 5. Claude Code Workflows (по Cole Medin)

### PIV Loop (Plan → Implement → Validate)

#### Plan (Планирование)
- `/prime` — загрузка контекста (Jira ticket, codebase tree, git log)
- `/plan` — структурированный план с validation strategy
- Sub-agents для параллельного исследования (но не реализации)

#### Implement (Реализация)
- Сброс контекста между Plan и Implement
- `/implement` — исполнение плана в свежем окне
- TodoWrite для отслеживания прогресса

#### Validate (Валидация) — 5-уровневая пирамида
```
Layer 5: Manual testing ← Человек (golden path + edge cases)
Layer 4: Code review ← Человек (с AI assist)
Layer 3: Integration / E2E ← Агент + browser automation
Layer 2: Unit tests ← Агент
Layer 1: Type checking + linting ← Агент
```

### 15 Claude Code команд (из ai-transformation-workshop)
| Команда | Назначение |
|---------|-----------|
| `/prime` | Загрузка контекста |
| `/prime-server` | Контекст для серверной части |
| `/prime-client` | Контекст для клиентской части |
| `/prime-endpoint` | Контекст для эндпоинта |
| `/prime-components` | Контекст для компонентов |
| `/create-prd` | Создание PRD |
| `/prd-interactive` | Интерактивное создание PRD |
| `/create-rules` | Генерация CLAUDE.md для проекта |
| `/create-stories` | PRD → Jira issues (через Atlassian MCP) |
| `/plan` | Планирование реализации |
| `/implement` | Реализация плана |
| `/validate` | Валидация и тестирование |
| `/review` | Code review |
| `/security-review` | Аудит безопасности |
| `/install` | Установка AI layer в проект |

### Context Engineering vs Prompt Engineering
| Prompt Engineering | Context Engineering |
|-------------------|-------------------|
| Фокус на формулировку | Фокус на полную систему контекста |
| Ограничен одним промптом | Включает доки, примеры, правила, паттерны |
| Как дать стикер | Как написать сценарий |

---

## 6. Связанные инструменты

### 6.1. Goose (Block)
- **Ссылка:** https://github.com/block/goose
- **Роль:** Open-source база для Stripe Minions
- **Описание:** Coding agent от Block, на котором построены Stripe Minions

### 6.2. Claude Agent SDK / Harness
- **Ссылка:** https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding
- **Cole Medin's harness:** https://github.com/coleam00/Linear-Coding-Agent-Harness
- **Описание:** Anthropic's harness для долгоживущих агентов с Linear для task management

### 6.3. AG-UI Protocol
- **Ссылка:** https://github.com/ag-ui-protocol/ag-ui
- **Описание:** Протокол для встраивания AI агентов в приложения (Cole Medin video)

### 6.4. Superpowers
- **Ссылка:** https://github.com/obra/superpowers
- **Звёзды:** 45k+
- **Описание:** Spec-driven toolkit для AI-кодинг агентов (альтернатива OpenSpec)

---

## 7. Рекомендации для Hermes

### Немедленное внедрение
1. **OpenSpec** — установить CLI, создать skill-обёртку для генерации спецификаций
2. **PIV Loop** — внедрить методологию Plan-Implement-Validate в workflows
3. **.claude/commands/** — создать набор команд для Hermes (адаптировать 15 команд Cole Medin)

### Среднесрочное внедрение
1. **Context Engineering** — улучшить систему контекстов для агентов Hermes
2. **Stripe Blueprints pattern** — добавить гибридные deterministic/agentic workflows
3. **MCP Toolshed** — создать централизованный MCP сервер с инструментами Hermes

### Долгосрочное
1. **Собственные coding agents** — по аналогии с Archon/Goose
2. **Spec-driven development** как стандарт для всех проектов Hermes

---

## 8. Все найденные ссылки (сводка)

### Репозитории Cole Medin
| Репозиторий | Звёзды | Ссылка |
|------------|--------|--------|
| Archon | 22.9k | https://github.com/coleam00/Archon |
| context-engineering-intro | 13.7k | https://github.com/coleam00/context-engineering-intro |
| ottomator-agents | 5.7k | https://github.com/coleam00/ottomator-agents |
| excalidraw-diagram-skill | 4.1k | https://github.com/coleam00/excalidraw-diagram-skill |
| local-ai-packaged | 3.7k | https://github.com/coleam00/local-ai-packaged |
| ai-agents-masterclass | 3.4k | https://github.com/coleam00/ai-agents-masterclass |
| ai-transformation-workshop | 122 | https://github.com/coleam00/ai-transformation-workshop |
| Linear-Coding-Agent-Harness | — | https://github.com/coleam00/Linear-Coding-Agent-Harness |

### Инструменты
| Инструмент | Ссылка |
|-----------|--------|
| OpenSpec | https://github.com/Fission-AI/OpenSpec |
| OpenSpec Website | https://openspec.dev |
| Stripe Minions Blog | https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents |
| Stripe Minions Analysis | https://rywalker.com/research/stripe-minions |
| Goose (Block) | https://github.com/block/goose |
| Superpowers | https://github.com/obra/superpowers |
| AG-UI Protocol | https://github.com/ag-ui-protocol/ag-ui |
| Shopify Roast | https://github.com/Shopify/roast |

### Видео
| Видео | Ссылка |
|------|--------|
| Cloud Codes — GitHub Repos That Feel Illegal to Know | https://www.youtube.com/watch?v=jgsDu9MubJM |
| Cole Medin — Stripe's Coding Agents Ship 1,300 PRs | https://www.youtube.com/watch?v=NMWgXvm--to |
| Cole Medin — AI Transformation Workshop | https://www.youtube.com/watch?v=OcTMwjqje5Q |
| Cole Medin — Future of AI and SaaS is Agentic Experiences | https://www.youtube.com/watch?v=BcvjGTxzK40 |

---

*Дата создания: 15 июля 2026*
*Автор: Hermes Agent (автоматическое исследование)*
