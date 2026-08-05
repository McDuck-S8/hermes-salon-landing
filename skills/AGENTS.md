# skills/ — Agent Skills Library

## Purpose
Bundled agent skills — reusable behaviors and domain-specific knowledge that agents can load on demand.

## Ownership
Skills are curated and versioned. Managed via the skill-forge system.

## Local Contracts
- Each skill has a `SKILL.md` file as its entry point
- Skills may include `references/` (markdown docs), `scripts/` (executable helpers), `templates/`
- Skills are organized by category in subdirectories
- `.hub/` contains the skill hub index and cache
- `.usage.json` tracks skill usage statistics

## Work Guidance
- **Loading a skill**: Use the `skill` tool with the skill name
- **Creating a skill**: Follow the SKILL.md format, place in appropriate category
- **Categories**: automation, creative, data-science, devops, finance, github, media, mlops, research, security, self-improvement, software-development, web-development, etc.
- **Auto-generated skills**: `auto-generated/` — patterns learned from sessions
- **Lavra agents**: `lavra-agent-*` — review and analysis agents

## Skill File Hygiene (обязательно для АВТО-СОЗДАННЫХ скиллов)

Правила для автономных писателей (background_review, self_improvement_loop).
Причина: 2026-08-05 пользователь — «научи товарищей правильно оформлять файлы».
Скелеты с TODO-заглушками — антипаттерн «записал-не-сделал».

**ЕДИНЫЙ ИСТОЧНИК ПРАВИЛ: `config/skill_hygiene.yaml`** — правки вносятся
там, код не трогается (принцип «правки в одном файле», 2026-08-05).
Этот файл — человеко-читаемая копия для справки; исполняется YAML.

1. **НЕ создавать скелеты**: никаких TODO/TBD/FIXME/`pass`/пустых `[ ]` чекбоксов.
   Скилл без реального содержания НЕ создаётся вообще.
2. **Валидное имя**: lowercase, только `[a-z0-9_-]`, ≤64 символа, без пробелов.
   Нормализация: `_valid_skill_name()` в self_improvement_loop.
3. **Frontmatter**: обязательные `name`, `description` (≤57 символов в первой
   строке — видно в system prompt), `trigger`; `category: auto-generated`
   для автогенерированных.
4. **Структура**: SKILL.md (класс-левел) + `references/` для деталей сессии,
   `templates/` для заготовок, `scripts/` для исполняемых помощников.
5. **Обновление предпочтительнее создания**: сначала patch существующего
   (loaded/umbrella), потом support file, только потом новый скилл.
6. **Protected skills не трогать**: bundled, hub-installed, pinned,
   user-owned (background_review уже кодирует это в промпте).
7. **Создание через skill_manage** (когда доступен); из чистого Python —
   через `_write_skill_file()` с валидацией, не голым `write_text`.

## Verification
- Each skill should have a valid `SKILL.md`
- Check `.usage.json` for usage stats

## Child DOX Index
| Category | Contents |
|---|---|
| `automation/` | Browser, session analysis, telegram digest, **subagent-orchestration** |
| `creative/` | Design, art, video, music generation, **remotion-video** |
| `context-engineering/` | Context window management: **filesystem-context** (tool-output offloading), **context-optimization** (masking, KV-cache, compaction) |
| `devops/` | Kanban, system ops, webhooks, **chain-heartbeat**, **maintenance-scanner** |
| `finance/` | Earning with AI, Excel, stocks |
| `github/` | PR workflow, issues, code review |
| `lavra-agent-*` | Review and analysis agents (30+) |
| `research/` | ArXiv, patterns, wiki |
| `self-improvement/` | Dream memory, evolution, verification |
| `software-development/` | TDD, debugging, plans, **impeccable** (дизайн/аудит UI), **beads** (трекер задач) |
| `superpowers/` | Process skills: brainstorming, subagent-driven-development, writing-plans, using-superpowers |
