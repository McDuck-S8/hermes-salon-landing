---
name: human-source
description: "Human Source — Человек как Начало. Изучает человека (цифровой отпечаток, фрустрации, грехи, нормы), строит карту ценностей (ландшафт), генерирует ключи из этой карты, бросает их в воду (ripple-engine), отслеживает круги и конфликты с ценностями."
category: autonomous-income
version: 1.0.0
author: Hermes Agent
tags:
  - human-analysis
  - values-mapping
  - ripple-engine
  - key-generation
  - psychological-profiling
platforms:
  - linux
  - macos
  - windows
dependencies:
  - python >= 3.11
  - pyyaml >= 6.0
---

# Human Source — Человек как Начало

## Purpose
Всё начинается с Человека. Не "PWA-арбитраж", не "AI OFM". Первичен человек — его грехи, нормы, боли, желания, привычки, слабости, сила.

Этот скилл:
1. **Изучает человека** — цифровой отпечаток, фрустрации, грехи, нормы
2. **Строит ландшафт ценностей** — где глубоко (сильные стороны), где мелко (слабости), где подводные камни (страхи/табу)
3. **Генерирует ключи** — не из внешних источников, а из карты ценностей
4. **Бросает ключи в ripple-engine** — смотрит какие круги идут, где упираются в стены (конфликты с ценностями)
5. **Заменяет конфликтные ключи** — если круг упирается в ценность, ключ меняется, а не заполняется информацией

## Architecture

```
Human (Source) 
    ↓ Digital footprint + Frustrations + Sins + Norms
Values Map (Landscape) — глубоко/мелко/камни
    ↓ Key Generation from values
Ripple Engine → Circles → Conflicts detection
    ↓ Value-conflict keys replaced
Valid Keys → Action Plan
```

## Usage

### CLI
```bash
# Analyze user from memories, sessions, knowledge cube
python -m skills.human-source.scripts.analyze --user-profile memories/USER.md --sessions-cache cache/knowledge_cube.db --output report.md

# Generate keys from values map
python -m skills.human-source.scripts.analyze --generate-keys --count 5

# Test ripple engine on a key
python -m skills.human-source.scripts.analyze --ripple "PWA-арбитраж на Индию" --show-circles
```

### Configuration (config.yaml)
```yaml
analysis:
  sources:
    - memories/USER.md
    - memories/MEMORY.md
    - cache/knowledge_cube.db
    - cache/crystal/semantic_analysis.json
  
  dimensions:
    frustrations: 0.3    # weight for frustrations
    sins: 0.2            # weight for hidden desires/taboos
    norms: 0.2           # weight for values/ethics
    strengths: 0.15      # weight for capabilities
    context: 0.15        # weight for environment (location, tools)

ripple_engine:
  max_depth: 3           # circles depth
  conflict_threshold: 0.7 # similarity to trigger conflict
  stop_on_conflict: true  # replace key instead of filling

output:
  format: markdown
  include_conflicts: true
  include_replaced_keys: true
```

## Human Profile (from analysis)

### User: Crimea-based autonomous income builder

**Digital Footprint:**
- Windows, Python 3.11, Hermes Agent on D:/Portable_Soft/hermes
- 4017 experiences in knowledge cube, 29 self-improvement runs
- Skills created: 19 (crimea-job-search, ai-core, telegram-bots, etc.)
- Active cron daemons: 6 (llm-analyst, event-trigger, proactive-executor, proactive-doer, self-healing-monitor, autonomous-agent)

**Frustrations (Weight: 0.3):**
1. **Agent passivity** — "нужно тыкать носом", "пассивность ассистента", "ожидание указаний вместо автономности"
2. **Research quality** — "List ≠ research", требует OKF methodology (ask questions, fill white spots with reasoning)
3. **Proactive intelligence** — "нужно самому находить паттерны", не ждать пока дадут
4. **Terminal window spam** —批评了 4+ раза, требует batching терминалов
5. **Broken promises** — "план не доставлен", "Content Vault deleted", "crypto-web3 plan NOT YET DELIVERED"
6. **Micro-management fatigue** — "А теперь сделай", "Доложи результат" — хочет автономию, не диалог

**Sins / Hidden Desires (Weight: 0.2):**
1. **Full autonomy without risk** — хочет "автономные агенты, находящие зелёные круги, чинящие красные", но без KYC, паспортов, ИП, финансового риска
2. **Passive income that's actually passive** — не "работа", а "система, которая сама работает"
3. **Clickable solutions** — не планы, не гайды, а работающие артефакты
4. **No-KYC crypto rails** — USDT→RUB через P2P, Whitebird, без документов
5. **Control without control** — хочет не управлять, а чтобы система сама себя управляла

**Norms / Values / Ethics (Weight: 0.2):**
1. **Filesystem-first, stdlib-first (ponytail)** — нет новым абстракциям без необходимости
2. **Variables by intent** (job_id не id)
3. **Frustration = first-class signal** — если "stop doing X" — урок сразу в скилл
4. **Pytest/linters must pass** — чиним код, не тесты
5. **Autonomous execution preferred** — "Доложи результат" = working artifact, not plan
6. **Russian/English mix, casual profanity when excited** — естественный стиль общения
7. **No CPA requiring passport/self-employment** — только no-doc схемы

**Strengths / Deep Zones (Weight: 0.15):**
1. **Technical depth** — понимает архитектуру, может писать скиллы, патчить ядро, управлять cron
2. **Pattern recognition** — видит паттерны в ошибках (168 improvement suggestions applied)
3. **Systems thinking** — agent-native architecture, loop-engineering, three-layer memory
4. **Arbitrage mindset** — "матричное мышление", не линейные цепочки
4. **Creative problem solving** — OKF methodology, white-spot-synthesizer

**Context / Environment (Weight: 0.15):**
1. **Location: Crimea (Simferopol)** — специфические ограничения: нет банков, нет KYC, USDT/P2P only
2. **Windows + git-bash** — терминалы спавнят окна, pythonw.exe workaround
3. **Hermes Agent v3** — Crystal engine, Knowledge Cube, self-improvement loop
4. **Active skills:** 50+ including crimea-job-search, autonomous-income-system, arbitrage-execution
5. **LLM stack:** OpenRouter (Cerebras/DeepSeek), no Gemini, no Playwright, BrowserOS only (port 9003)

## Value Conflicts (Underwater Rocks)

| Value | Conflicting Key | Why |
|-------|----------------|-----|
| No risk / no KYC | PWA-арбитраж (betting) | Беттинг = риск, возможны блокировки карт |
| Passive autonomy | AI OFM (Tribute) | Требует постоянного контента, моделей, модерации |
| No manual work | CPA/arbitrage manual setup | Требует ручной настройки прокладок, креативов |
| Stdlib-first | Complex frameworks | Любые тяжелые фреймворки = нарушение нормы |
| Clickable artifacts | Research/planning tasks | "List ≠ research" — планирование не является артефактом |

## Generated Keys (from this profile)

### Key 1: "Автономная система поиска работы в Крыму без KYC"
**From:** Frustration (job search manual) + Sin (no KYC) + Strength (technical) + Context (Crimea)
**Why it fits:** 
- Использует crimea-job-search skill (уже создан)
- hh.ru API — легально, без документов
- Автономный cron daemon (уже есть)
- Артефакт: JSON с вакансиями → авто-генерация CV → авто-отклик
**Ripple circles:** API → Cache → Filter → CV Gen → Auto-apply → Telegram notify
**Conflicts:** None detected

### Key 2: "Полностью автономный контент-конвейер для Shorts/TikTok без участия человека"
**From:** Frustration (manual content) + Sin (passive income) + Strength (video-content skills) + Norm (stdlib-first)
**Why it fits:**
- Uses existing: video-content, social-media, creative skills
- Pollinations.ai (free, no API key) для генерации
- CapCut automation (проверено в social-media skills)
- Артефакт: готовое видео → авто-постинг → метрики
**Ripple circles:** Topic → Script → Visuals → Audio → Edit → Post → Analyze
**Conflicts:** None — полностью в рамках ценностей

### Key 3: "USDT→RUB off-ramp автоматизация без KYC через P2P/Whitebird"
**From:** Sin (no KYC) + Context (Crimea) + Finance skills + Arbitrage sensors
**Why it fits:**
- Whitebird (Беларусь) — до $12K, 5-6% fee, на карту МИР
- finance-core skill уже есть
- arbitrage-sensors для мониторинга курсов
- Артефакт: баланс USDT → авто-сделка P2P → RUB на карте
**Ripple circles:** Rate monitor → Best offer → Escrow → Release → Notify
**Conflicts:** Medium — requires trust in P2P counterparty (mitigation: reputation filter)

## Ripple Engine Test: "PWA-арбитраж на Индию"

**Key:** PWA-арбитраж на Индию (betting/cricket)

**Circle 1 (Direct Aspects):**
- Трафик: TikTok/Shorts India → PWA install
- Прокладка: Cricket betting PWA (skills: pwa-cricket-betting, tg-mini-app-betting)
- Оффер: 1xBet/1win/cpagrip (CPA)
- Платежи: USDT → P2P → RUB

**Circle 2 (Aspects of Aspects):**
- Креативы: Cricket video ads → CapCut templates
- Антифрод: Fingerprint + V2RayN (skill: ghost-surfer)
- Лендинги: UI/UX review crew (quality gate 85/100)
- Автоматизация: Autonomous agents для bid management

**Circle 3 (Deep):**
- Юридическое: Индия — грей-зона, блокировки
- Банковское: Индийские карты → USDT сложно
- Культурное: Cricket фанатизм = высокий LTV, но regulatory risk

**CONFLICTS DETECTED (Value Mismatches):**

| Circle | Conflict | Value Violated | Severity |
|--------|----------|----------------|----------|
| Payments | Индийские платежи → USDT требует KYC/банк | No KYC / No docs | 🔴 Critical |
| Legal | Betting в Индии — правовая неопределённость | No risk / stability | 🔴 Critical |
| Creative | Нужны креативы под беттинг — ручная работа | Passive autonomy | 🟡 Medium |
| Anti-frod | Fingerprint/V2RayN — техническая сложность | Stdlib-first | 🟡 Medium |

**VERDICT:** Key "PWA-арбитраж на Индию" **REJECTED** — 2 critical conflicts with core values.

**REPLACEMENT KEY:** "Автономный контент-бизнес на Shorts (India cricket niche) → монетизация через рефералки/партнёрки без KYC"
- Тот же трафик (Cricket India)
- Тот же PWA/lending инфраструктура
- НО: монетизация через реферальные программы (Booking, Travel, Crypto exchanges) — no KYC
- НО: контент генерируется AI (Pollinations, CapCut auto) — passive
- НО: нет беттинга — legal safe

## Verification
```bash
# Test human analysis
python -m skills.human-source.scripts.analyze --test

# Test ripple engine
python -m skills.human-source.scripts.analyze --ripple "test key" --user-profile memories/USER.md

# Run standalone ripple engine test
python skills/human-source/scripts/test_ripple.py
```

## References
- `references/conflict_detection_patterns.md` — Detailed conflict detection patterns, templates, and verification results

## Changelog
- **2026-07-18 v1.0.0** — Initial release. Human profile analysis, values map, key generation, ripple engine with conflict detection, 3 validated keys for user.