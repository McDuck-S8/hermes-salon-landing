# Crystal v3 Architecture Design Session — 2026-06-16

## Context
User was frustrated that crystal context was lost across sessions ("ты каждый раз это делаешь").
Old crystal (v2.0, 3576 lines) was deleted and called "мусор" — user corrected: "мусора не существует, есть непонимание того что читаешь".

## Key User Quotes
- "такой важный проект для нас, а у тебя нет понимания и записей что это такое!!!"
- "мусора не существует!!!! есть не понимание того что читаешь, а значит не знаешь что с этим делать!!!"
- "задачча на основе моих запросов, сессий изучать меня, мои потребности и понимать куда развиваться как мне так самой системе"
- "если есть что ещё добавить-говори что"
- "нужны ветки отделов или агенств-работа с ютуб, соц сетями, создание сайтов и тгб, монетизация и т д"

## Architecture Decision: 12 Modules

Evolution from 6 to 12 modules based on user feedback:

| # | Module | Why Added |
|---|--------|-----------|
| 4 | Priority Engine | "у тебя limited time" — need to prioritize |
| 5 | User Energy Model | adapt proposals to user state |
| 6 | Dependency Map | "Telegram bot needs hosting" — blockers matter |
| 7 | Risk Assessment | safe vs risky actions need different handling |
| 10 | Proactive Alerts | "сам ищи что устарело" — don't wait for user |
| 11 | Memory Integration | read/write user memory for continuity |

## Departments (8)
User requested: youtube, social-media, websites, telegram-bots, monetization
Added: ai-core, devops, data (infrastructure domains)

## Files Created/Modified
- `skills/crystal-self-learning/AGENTS.md` — full v3 architecture spec (9.6KB)
- `skills/crystal-self-learning/SKILL.md` — updated description + pitfalls + principles
- `scripts/AGENTS.md` — added Crystal to Local Contracts + Child DOX Index

## What Old Crystal Did Right
- will() — 800 lines of decision-making (removed due to bugs, not bad concept)
- conscience — self-learning loop (removed due to EE dependency)
- self_model.json — persistent self-knowledge (removed due to path issues)
- These concepts are restored in v3 as: Priority Engine, Feedback Loop, Memory Integration

## What Old Crystal Did Wrong
- Hardcoded entity_engine.db path (8 times) → crash
- SELF_MODEL_PATH never defined → NameError
- Self-modification via crude string replace
- 19 patches accumulated without architecture review
- No tests, no validation, no DOX
