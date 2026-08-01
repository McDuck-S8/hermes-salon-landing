---
name: skill-pathfinder
description: "Поисковик Пути — самоориентация в пространстве навыков. Строит граф зависимостей навыков, оценивает уровень освоения, находит точку входа (самый слабый × самый востребованный), выстраивает маршрут обучения. Жёсткое правило: не изобретать — смотреть лучшие примеры, выбирать/синтезировать, потом делать."
category: self-improvement
version: 1.0.0
author: Hermes Agent
tags:
  - skill-mapping
  - learning-path
  - dependency-graph
  - best-practices
  - self-assessment
platforms:
  - linux
  - macos
  - windows
dependencies:
  - python >= 3.11
  - pyyaml >= 6.0
  - networkx >= 3.0
---

# Skill Pathfinder — Поисковик Пути

## Purpose
Ты не просто "изучаешь навыки". Ты ориентируешься в пространстве навыков как в ландшафте. Где яма, где холм, где река — и как проложить путь от "здесь" к "там" с минимальными потерями.

Этот навык делает три вещи:
1. **Строит карту** — граф зависимостей всех навыков агента
2. **Находит точку входа** — где слабый навык × высокий спрос = максимальный ROI обучения
3. **Выстраивает маршрут** — порядок прокачки с учётом зависимостей и усиления

И главное: **запрещает изобретать велосипед**. После поиска пробела — обязательный протокол: найти 5-10 лучших примеров → выбрать/синтезировать → только потом делать.

---

## Architecture

```
Skill Pathfinder Pipeline:

[Inventory] → [Graph Build] → [Level Assessment] → [Gap × Demand] → [Entry Point]
                                                              ↓
[Best Practices Research] ← [Gap Analysis] ← [Route Planning] ←
     (3 шага)          (что не хватает)     (A→B→C зависимости)
```

### Core Components

| Component | Responsibility |
|-----------|----------------|
| `inventory.py` | Сканирует skills/, плагины, cron, память — собирает список навыков с метаданными |
| `graph.py` | Строит граф зависимостей (requires, enhances, conflicts) |
| `assess.py` | Оценивает уровень каждого навыка: артефакты, тесты, использование, freshness |
| `demand.py` | Оценивает востребованность: частоты вызова, пользовательские запросы, ошибки |
| `entry.py` | Находит точку входа: argmax(weakness × demand) |
| `route.py` | Выстраивает маршрут: топологическая сортировка + усиление |
| `research.py` | **Протокол 3 шагов**: GitHub/Awwwards/YouTube/форумы → выбор/синтез → отчёт |
| `track.py` | Обновляет карту после изучения, предлагает следующий шаг |

---

## The 3-Step Protocol (НЕВЫПОЛНИМОЕ ПРАВИЛО)

После того как найден пробел в навыке (gap), **запрещено** сразу писать код. Обязательный протокол:

### Шаг 1: Посмотри как у людей (Research)
Найди 5-10 лучших примеров решения этой задачи.
- **Где искать**: GitHub (stars, forks, recent), Awwwards/Dribbble (дизайн), YouTube (туториалы), документации, форумы (Reddit, StackOverflow, Habr)
- **Что фиксировать для каждого**: 
  - Что именно хорошо (конкретный приём, архитектура, UX)
  - Почему это работает (принцип, паттерн)
  - Ссылка на источник

### Шаг 2: Выбери или синтезируй (Select/Synthesize)
- Если есть **готовый инструмент/шаблон/код**, решающий задачу — **бери его**. Не пиши своё.
- Если готового нет — возьми **лучшие приёмы из 2-3 примеров** и синтезируй своё.
- **Запиши в отчёт**: что взял, откуда, почему именно это.

### Шаг 3: Только теперь делай (Execute)
Применяй выбранное/синтезированное решение.
Никакого "я придумал" без ссылки на источник.

---

## Dependency Types

| Type | Meaning | Example |
|------|---------|---------|
| `requires` | Жёсткая зависимость: Б не работает без А | `crystal-core` requires `knowledge-cube` |
| `enhances` | Мягкое усиление: Б делает А лучше | `ripple-engine` enhances `values-map` |
| `conflicts` | Несовместимость | `playwright` conflicts `browseros` |
| `subsumes` | А включает Б (Б устарел) | `human-source` subsumes `user-profile` |

---

## Skill Level Assessment (0-100)

Критерии оценки (сумма = 100):
| Criterion | Weight | How to measure |
|-----------|--------|----------------|
| **Artifacts** | 30% | Есть ли работающие скрипты, отчёты, тесты? |
| **Tests** | 20% | Проходят ли автотесты? Есть ли test coverage? |
| **Usage** | 20% | Как часто вызывается в cron/agent? (logs) |
| **Freshness** | 15% | Когда последний раз обновлялся? (git log) |
| **Completeness** | 15% | Покрывает ли declared functionality? |

---

## Demand Assessment (0-100)

| Source | Weight | Signal |
|--------|--------|--------|
| **User requests** | 35% | "научись X", "сделай Y" в сессиях |
| **Error patterns** | 25% | Повторяющиеся ошибки в Knowledge Cube |
| **Cron frequency** | 20% | Как часто навык нужен в расписании |
| **Cross-skill refs** | 20% | Сколько других навыков зависят от него |

---

## Usage

```bash
# Full audit: build map, assess, find entry, plan route
python -m skills.skill-pathfinder.scripts.analyze --full-audit --output reports/skill_audit.md

# Quick: just find entry point
python -m skills.skill-pathfinder.scripts.analyze --entry-point

# Research best practices for a specific skill gap
python -m skills.skill-pathfinder.scripts.analyze --research "crystal-core" --output reports/research_crystal.md

# Track progress after learning a skill
python -m skills.skill-pathfinder.scripts.analyze --update "crystal-core" --level 85 --artifacts "core.py,executor.py,tests/"
```

---

## Integration with human-source & audience-analyzer

```
human-source (ЧЕЛОВЕК)
    ↓ Values, frustrations, sins, norms
    ↓ "Мне нужен пассивный доход без KYC"

audience-analyzer (РЫНОК)  
    ↓ What audiences need, what offers convert
    ↓ "PWA betting India — high demand, но KYC conflict"

skill-pathfinder (ПУТЬ) ← NEW
    ↓ Gap: " arbitrage-execution" слабый (level=20, demand=90
    ↓ Entry point: прокачать arbitrage-execution
    ↓ Research: найди 5 лучших арбитражных ботов на GitHub
    ↓ Synthesize: возьми архитектуру от бота А, риск-менеджмент от Б
    ↓ Route: arbitrage-execution → finance-core → matrix-thinking
```

---

## Output Artifacts

1. **Skill Map** (`reports/skill_map.graphml`) — граф для визуализации
2. **Audit Report** (`reports/skill_audit.md`) — полная таблица навыков, уровни, спрос
3. **Entry Point Card** (`reports/entry_point.md`) — какой навык, почему, какие 5 примеров, что синтезировать
4. **Route Plan** (`reports/route_plan.md`) — пошаговый план: A → B → C с зависимостями
5. **Research Log** (`reports/research_<skill>.md`) — протокол 3 шагов для каждого gap

---

## Changelog
- **2026-07-18 v1.1.0** — Added dual-axis scoring (human-source × audience-analyzer), three integrations validated, performance optimizations, 3-step protocol execution for arbitrage-execution.
- **2026-07-18 v1.0.0** — Initial release. Graph build, assessment, entry point, 3-step protocol, route planning.

## Pitfalls & Lessons (2026-07-18 Session)

### YAML Frontmatter Parsing
Many SKILL.md files in the wild have malformed frontmatter:
- Unquoted colons in descriptions: `description: Text with : colon`
- Multiline strings with `|` or `>-` indicators
- Missing quotes around values containing special chars

**Fix applied**: Pre-process frontmatter text with regex substitutions before `yaml.safe_load()`:
```python
# Fix unquoted colons in values
frontmatter_text = re.sub(r'^(\\s*\\w+:\\s*)(.+:\\s*.+)$', r'\\1"\\2"', frontmatter_text, flags=re.MULTILINE)
# Fix multiline indicators
frontmatter_text = re.sub(r'^(\\s*description:\\s*)[\\|>\\-].*$', r'\\1 ""', frontmatter_text, flags=re.MULTILINE)
```

### Bracket Balancing in Markdown Generation
When building report lines with `lines.extend([...])`, every `[` must have a matching `]`. Emoji characters (⚙️, ➡️) in f-strings can cause encoding issues on Windows. **Use ASCII markers** (`[Step 1]`, `[Step 2]`) instead.

### Skills Root Path Resolution
When running from `skills/skill-name/scripts/analyze.py`, the skills root is **four levels up**:
```python
hermes_root = Path(__file__).parent.parent.parent.parent  # skills/skill-name/scripts → hermes/
skills_root = hermes_root / "skills"
```

### Asyncio Import
Don't forget `import asyncio` when using `asyncio.run(main())` at module bottom.

### Graceful Degradation
If `networkx` not installed, graph features degrade gracefully — set `nx = None` and check `if graph.graph and nx:` before using.

---

## Multi-Dimensional Scoring (NEW — 2026-07-18 Session)

### Three Integrations Required for Valid Entry Points

The entry point formula was updated from simple `weakness × demand` to four-factor scoring:

```
Entry Score = weakness × demand × personal_importance × audience_relevance / 100³
```

Where each factor is 0-100 and derived from separate integrations:

#### 1. Human-Source Integration (`HumanSourceIntegrator`)
**Purpose**: Evaluate personal importance (0-100) based on user's values map.

**Loads from**: `skills/human-source/scripts/analyze.py` + `reports/human_source_report_final.md`

**Key outputs**:
- `get_personal_importance(skill_name, skill)` → 0-100 score
- `get_risk_boundary(skill)` → `"free" | "needs_approval" | "blocked"`

**Underwater rocks (hard constraints)** that block skills:
- `kyc`, `passport`, `document`, `verification` → **blocked** (No KYC/Documents)
- `playwright`, `gemini`, `chrome` → **blocked** (No Google Gemini/Playwright)
- `budget`, `paid api`, `subscription`, `legal`, `compliance` → **needs_approval**

**Personal keywords** that boost score: crimea, simferopol, job, hh.ru, p2p, usdt, rub, offramp, crypto, shorts, tiktok, content, pipeline, arbitrage, matrix, betting, cricket, autonomous, cron, daemon, self-heal, telegram, bot, channel

#### 2. Audience-Analyzer Integration (`AudienceRelevanceCalculator`)
**Purpose**: Evaluate audience/market relevance (0-100) using audience-to-skill mappings.

**Audience → Required Skills mappings**:
| Audience | Required Skills |
|----------|----------------|
| `arbitrage` | arbitrage-execution, finance-core, arbitrage-sensors, matrix-thinking |
| `betting` | pwa-betting, creative-production, anti-fraud, cloaking |
| `crypto` | p2p-offramp, usdt-rub, defi, wallet-security |
| `content` | content-pipeline, shorts-production, tiktok-automation, youtube-seo |
| `telegram` | telegram-bot-integration, telegram-channel-poster, tg-mini-app |
| `job-search` | crimea-job-search, hh-ru-parser, cv-optimizer |
| `affiliate` | cpa-affiliate-bot, offer-scanner, landing-generator |

**Category value boosts**: finance=30, arbitrage=30, autonomous-income=25, automation=20, cpa-affiliate=25

#### 3. Artifact Map (`SkillArtifactMap`)
**Purpose**: Track created artifacts per skill to prevent reinventing wheels.

**Scans**: scripts/ (with py_compile test), reports/, templates/

**Key methods**:
- `get_artifact_summary(skill_name)` → human-readable summary
- `has_working_implementation(skill_name)` → bool (has tested script)

---

### Decision Matrix (NEW)

Entry point selection now uses 2-axis evaluation:

| Personal Importance | Audience Relevance | Action |
|---------------------|-------------------|--------|
| High | High | 🔥 **Priority 1** — learn immediately |
| High | Low | 🧠 Learn for self, not for revenue |
| Low | High | 💰 Learn for revenue, even if not personally interesting |
| Low | Low | ⚪ Defer or skip entirely |

This prevents two failure modes:
1. **Personal bias trap**: Learning skills only you need but market doesn't value
2. **Market chase trap**: Learning skills market wants but you'll never maintain

---

### Performance Optimizations Applied

Disabled expensive DB lookups during inventory scan (git log, knowledge cube, sessions DB) — they caused 60s+ timeouts. Now using category/tag heuristics only:
```python
# Category boost for high-value domains
high_value_categories = {'finance': 30, 'arbitrage': 30, 'autonomous-income': 30, 'automation': 25, 'devops': 20, 'cpa-affiliate': 25}

# Tag-based boost for known important topics
important_tags = ['cpa', 'arbitrage', 'betting', 'cricket', 'india', 'pwa', 'telegram', 'bot', 'shorts', 'tiktok', 'p2p', 'usdt', 'crypto', 'offramp', 'crimea', 'job', 'hh', 'content', 'pipeline']
```