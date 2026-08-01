# Three Sources of Proactivity Framework

**Date:** 2026-07-23  
**Source:** User (Alexander) — session on activating proactivity  
**Umbrella skill:** closed-loop-autonomy

## Overview

User identified 3 systems already built in Hermes that should drive autonomous
behavior without being commanded. They already exist — they just need to be
**used** without waiting for a command.

## Source 1: User Voice (Principal)

**What it is:** Every user message is recorded to Knowledge Cube via
`record_user_to_kc.py`. The `proactive_voice.py` scanner detects corrections,
preferences, demands, and frustrations in real-time.

**How it activates proactivity:**
- Crystal reads user_voice entries from KC at every session start
- Detects sentiment patterns: positive, frustration, correction, demand
- Adapts behavior without being told: "user is correcting → check approach",
  "user is frustrated → stop asking, do faster"
- The system doesn't wait for "сделай выводы" — it derives conclusions from
  every message automatically

**Implementation:**
- `scripts/proactive_voice.py` — message scanner (correction/preference/demand/frustration)
- `scripts/record_user_to_kc.py` — records messages with `[user:Александр:source]` tag
- `scripts/morning_report.py` — `analyze_user_voice()` reads last 24h of KC
- `scripts/auto_boot_scan.py` — runs morning_report at every session start

## Source 2: Chain Heartbeat (System as Organism)

**What it is:** `syscheck.py` and `auto_boot_scan.py` as mandatory reflexes.
The system CANNOT work while unhealthy.

**How it activates proactivity:**
- Every session start: auto_boot_scan checks principal identity, EE sync,
  heartbeat health, stale files
- Every morning report: system health is verified before anything else
- If unhealthy → fix immediately, do not proceed to user work
- Not a check "I should do" — but "I CANNOT NOT do"

**Implementation:**
- `scripts/syscheck.py` — `--quiet` returns exit code, verbose prints table
- `scripts/auto_boot_scan.py` — 4 checks + morning report, MUST pass to continue
- `scripts/chain_heartbeat.py` — `system_status()`, `self_check()`, `event_beat()`

## Source 3: Ripple Engine (Stones in Water)

**What it is:** Every morning, throw stones in the water and build circles.
See new knowledge → synthesize mature keys → unblock them → propose action.

**How it activates proactivity:**
- Daily at 9:00 (cron job `516f7f57d47e`): morning_report.py runs
- Finds mature domain clusters and entity growth from KC/EE
- Top-3 mature keys → proposes strongest one for today
- Persists proposal to session bridge for next session

**Expected behavior:** Start the day with:
> "Принципал, за ночь я нашёл 3 новых зрелых ключа. Самый сильный — X.
> Предлагаю разблокировать его сегодня."

NOT:
> "Что будем делать?"

**Implementation:**
- `scripts/morning_report.py` — `find_mature_keys()` queries KC domains + EE entities
- `cache/session_bridge.json` — stores morning_proposal between sessions
- Cron: daily at 9:00 AM

## The Activation Moment (2026-07-23)

The 3 sources were ALREADY BUILT before this session (except proactive_voice.py
and morning_report.py). What was missing: **autonomous usage without command.**

| Before | After |
|--------|-------|
| User voice recorded to KC, never analyzed | Crystal scans every session, deduces sentiment |
| syscheck existed but was optional | Boot scan MUST pass before any work |
| KC patterns existed but unread | Morning report finds mature keys daily |

**Key insight from user:** "Проактивность проявится из трёх источников, которые
ты уже построил. Они уже есть в системе — нужно только чтобы он начал их
использовать без твоей команды."

## Files

- `scripts/proactive_voice.py` — Source 1 implementation
- `scripts/morning_report.py` — Sources 1+2+3 combined
- `scripts/auto_boot_scan.py` — Sources 2+3 at session start
- `scripts/session_bridge.py` — Persistence layer for all 3 sources
- `cache/session_bridge.json` — Key commitments, last_ee_sync, morning_proposal
