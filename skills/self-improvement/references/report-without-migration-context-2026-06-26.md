# Pitfall: Report Without Migration Context

**Date:** 2026-06-26
**Signal:** User said "не полностью... я тебя переносил из D:\Portable_Soft\hermes-usb-portable-main" — correcting an incomplete status report.

## What Happened

Agent gave a status report covering today's sessions (FreeQwenApi, v2rayN, reality_gate, session_boot fixes). User pointed out the report missed the most important context: the entire hermes installation was being migrated from `hermes-usb-portable-main` to `hermes`.

## Why It Matters

When user asks "what happened today" or "report status":
1. The migration IS the main event — all other work happened in its shadow
2. There may be useful files left in the old location
3. Some scripts/configs may reference old paths
4. The user expects you to know about the migration because it was discussed in earlier sessions

## Prevention

Before giving a status report:
1. `session_search(query="перенос OR миграция OR migration OR перенес", limit=3)` — check for recent migration activity
2. If a migration happened, check if old location still has useful files
3. Report migration status as the TOP item in any status report

## Key Lesson

Status reports must include ALL major context, not just the most recent 1-2 sessions. Migration/relocation is a first-class topic that overrides granular task details.
