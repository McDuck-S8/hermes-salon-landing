# Proactivity 3 Sources — Activation (2026-07-23)

## Core Principle
Three proactivity sources were already built into the system but were not being used autonomously. The user's instruction: activate them so the system starts every session with a proposal, not a question.

## Source 1: User Voice (Principal)
Every user message is recorded to KC (domain=`user_communication`). At session start, `morning_report.py:analyze_user_voice()` reads the last 24h and computes a **signal**:

| Signal | Keywords | System Response |
|--------|----------|-----------------|
| 🔧 correction | "неправильно","надо не","исправь" | Apply correction immediately |
| 😠 frustration | "говно","не работает","блять" | Check quality. Don't ask. Fix. |
| ⚡ demand | "сделай","запусти","начинай" | Execute without questions |
| 😊 positive | "огонь","круто","отлично" | Continue autonomously |
| 😐 neutral | — | Standard mode |

**Implementation:** `scripts/proactive_voice.py` scans every recorded message. `morning_report.py` aggregates signals. `auto_boot_scan.py` shows the signal at session start.

## Source 2: Chain Heartbeat (System as Organism)
- `scripts/syscheck.py` — mandatory at every session start
- `auto_boot_scan.py` runs 4 checks: principal identity, EE sync freshness, heartbeat health, stale deprecated files
- **Any fail = fix before responding.** System CANNOT work unhealthy.

## Source 3: Ripple Engine (Continuous Pulse)
- Cron job `ad859ec5289b` runs `morning_report.py` every 15 min (no_agent mode)
- Saves `cache/latest_morning_report.json` with: health, user_voice signal, top-5 mature keys, top_proposal
- **At boot: READ cache, don't run analysis**
- Cache <15 min = fresh (show exact age). Cache ≥15 min = stale (show with "данные за N минут назад"). No cache = run one-shot.

## Key User Corrections
1. "Не список проблем. А задачи с сроками." → Each problem → goal_queue task with deadline → implement same session
2. "Не 'утром будет'. Не 'сейчас запущу'. Сейчас." → Cache-first. Report is ALWAYS ready.
3. "Я открыл терминал — я вижу предложение." → First message = top-3 keys + proposal. Never "What shall we do?"

## Files Created/Modified
- `scripts/morning_report.py` — aggregate analysis + JSON cache (+185 lines)
- `scripts/proactive_voice.py` — per-message pattern detection (+130 lines)
- `scripts/auto_boot_scan.py` — cache-first boot (+50 lines replacing analysis)
- `scripts/session_bridge.py` — cross-session persistence (+108 lines)
- `scripts/self_improvement_loop.py` — anti-pattern detector + threshold 3→2 (+48 lines)
