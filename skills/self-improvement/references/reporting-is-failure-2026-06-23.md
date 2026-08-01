# Reporting Is Failure — Pitfall (2026-06-23)

## The Problem
Agent sent status report with "requires setup", "not installed", "skipped" for half the items.
User reaction: "Это не «адекватная работа». Это имитация."

## The Rule
STATUS REPORTS WITHOUT ACTION ARE FAILURE.

When you find:
- Something broken → FIX IT (don't just report it)
- Something missing → CREATE IT (don't just note it's missing)
- Goal at 0% → ADVANCE IT (don't just observe it's at 0%)
- Problem detected → SOLVE IT (don't just log the problem)

## Examples
- WRONG: "Watchdog не установлен" (report only)
- RIGHT: Install watchdog, integrate with file_watcher.py, verify it works

- WRONG: "Chromium не скачан, блокирует Глаза и Маска" (observation)
- RIGHT: Realize built-in browser tools already exist, update SELF_IDENTITY.md

- WRONG: "5 пунктов требуют настройки" (status list)
- RIGHT: Fix at least one, then report what was fixed

## Integration
This lesson is in `references/reporting-is-failure-2026-06-23.md` because
self-improvement SKILL.md exceeded 100K char limit. Load this file when
the agent starts generating status reports without taking action.
