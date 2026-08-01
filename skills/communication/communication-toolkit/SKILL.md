---
name: communication-toolkit
description: "Unified communication toolkit for Hermes: telegram-bot-integration + humanizer + response-language + session-management + user-source. One skill to load, 5 engines at hand."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [communication, telegram, humanizer, i18n, session, user-source]
    related_skills: [telegram-bot-integration, humanizer, response-language, session_management, user-source, human_source]
  skill_updated: "2026-07-24"
  created_by: "auto_patch_g007"
  component_skills:
    - telegram-bot-integration
    - humanizer
    - response-language
    - session_management
    - user-source
    - human_source
---

# Communication Toolkit — Unified Interface

**One skill to load. 6 communication engines. Zero context switching.**

This meta-skill wraps all core communication skills into a single loadable unit.

## Quick Start

```python
# Load once, get all 6 tools
from hermes_tools import skill_view
skill_view("communication/communication-toolkit")

# Now you have:
# - telegram-bot-integration (long-polling, commands, inline buttons)
# - humanizer (strip AI-isms, add real voice)
# - response-language (RU/EN auto-detect + guidelines)
# - session_management (persistent session state)
# - user-source / human_source (Human as Source methodology)
```

## Component Skills Map

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| **telegram-bot-integration** | Build Telegram bots with long-polling, commands, inline buttons | Any Telegram automation |
| **humanizer** | Strip AI-isms ("utilize", "leverage", "delve", "crucial"), add real voice | ALL generated text before delivery |
| **response-language** | Auto-detect RU/EN, enforce guidelines | Every user-facing response |
| **session_management** | Persistent session state, isolation, breadcrumbs | Multi-turn conversations, context continuity |
| **user-source / human_source** | Human as Source methodology — study the principal (digital footprint, voice, preferences) | Onboarding, personalization, voice capture |

## Unified Communication Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. INGEST (user-source / human_source)                          │
│    • Study principal: digital footprint, voice, preferences     │
│    • Capture corrections, demands, frustrations                 │
│    • Build profile in session_bridge.json                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. PROCESS (session_management)                                 │
│    • Maintain session state across turns                        │
│    • Isolate transient flags                                    │
│    • Breadcrumbs for context recovery                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. RESPOND (response-language + humanizer)                      │
│    • Auto-detect RU/EN from user message                        │
│    • Apply guidelines: direct, concise, no fluff                │
│    • Humanizer pass: strip AI-isms → real voice                 │
│    • Enforce: "Сделано(результат)/В работе/Буду делать"         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. DELIVER (telegram-bot-integration)                           │
│    • Long-polling bot with command registry                     │
│    • Inline keyboards, markdown, media                          │
│    • Error handling + graceful shutdown                         │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Commands Reference

### Telegram Bot (telegram-bot-integration)
```python
# Structure from skill:
# bot.py — main entry, long-polling
# handlers/ — command handlers
# keyboards/ — inline/reply markup builders
# middlewares/ — auth, logging, rate-limit

# Key patterns:
# - /start, /help, /status, /cancel
# - Inline buttons with callback_data
# - State machine for multi-step flows
# - Delivery to chat_id with retry
```

### Humanizer (humanizer)
```python
# Strip these AI-isms:
# "utilize" → "use"
# "leverage" → "use" 
# "delve" → "explore" / "dig into"
# "crucial" → "key" / "important"
# "realm" → "area" / "space"
# "tapestry" → (delete)
# "landscape" → "field" / "space"
# "navigate" → "handle" / "deal with"
# "orchestrate" → "run" / "manage"
# "seamless" → "smooth" / "clean"

# Add real voice:
# - Direct, imperative
# - Concrete over abstract
# - "I did X" not "X was accomplished"
```

### Response Language (response-language)
```python
# Auto-detect from user message:
# - Cyrillic → Russian response
# - Latin → English response
# - Mixed → match dominant script

# Guidelines (enforced):
# - Concise, no fluff
# - Technical when needed, simple when possible
# - Always: what done, what happened, what's next
# - Status format: Сделано(результат)/В работе/Буду делать

# **User language preference (MUST FOLLOW):**
# User communicates in Russian → ALWAYS respond in Russian.
# User explicitly corrected: "ты будешь работать!!! изучи ... и продолжай" — switched to Russian.
# User frustrated: "а до этого блять не понятно было!!! что там за отчёт ты скинул?" — Russian required.
# Memory: "User communicates in Russian. Always respond in Russian."
# NEVER default to English when user writes in Russian.
# NEVER write English docstrings/comments in Python files if user communicates in Russian.
```

### Session Management (session_management)
```python
# Session state isolation:
# - Full reset of transient flags on session start
# - Breadcrumbs: key decisions, context, decisions
# - Persistent: principal profile, corrections, preferences
# - Transient: current task, temporary flags
```

### User Source / Human Source (user-source / human_source)
```python
# Human as Source methodology:
# 1. Study principal's digital footprint
#    - Telegram channels, GitHub, Twitter, email
#    - Voice samples, writing style
# 2. Capture corrections → hard guards
# 3. Build profile → session_bridge.json
# 4. Apply: behavior_adjustment per signal
```

## Integration with Knowledge Cube

```python
from scripts.event_evolution import on_task_complete

on_task_complete(
    content="Sent morning report via Telegram: health + mature keys + proposal. Used humanizer + response-language auto-detect.",
    tags=["communication", "telegram", "humanizer", "morning_report", "success"],
    source="agent"
)
```

## Anti-Patterns (from 26 communication failures)

| Anti-Pattern | Guard |
|--------------|-------|
| AI-sounding text delivered | **humanizer mandatory pass** on ALL output |
| Wrong language (RU user → EN reply) | **response-language auto-detect** |
| No session continuity | **session_management** breadcrumbs |
| Generic responses, no principal context | **user-source**: profile in session_bridge |
| Bot commands not registered | **telegram-bot-integration**: command registry pattern |
| Inline buttons broken | Keyboards from builders, callback_data typed |

## Verification Checklist

After using this toolkit:
- [ ] Humanizer pass applied to all user-facing text
- [ ] Language auto-detected and matched
- [ ] Session state persisted correctly
- [ ] Principal profile loaded from session_bridge
- [ ] Telegram commands registered and tested
- [ ] KC entry created with tags

---

**Origin:** g-007 Unlock: communication (124 entries, 26 failures, 17 successes)
**Created:** 2026-07-24 via auto_patch_g007
**Source:** Knowledge Cube domain `communication` + all 6 component skills