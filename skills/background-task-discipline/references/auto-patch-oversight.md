# Auto-Patch Oversight

The Hermes agent has multiple mechanisms that auto-patch SKILL.md files:

1. **background_review.py** (gateway agent) — after EVERY user response, forks a subagent with `[memory, skills]` tools, reviews the conversation, and patches skills based on learnings.
2. **proactive_executor.py** (cron every 15m) — scans sessions for patterns, creates/evolves skills.
3. **skill_evolution_v2.py** (cron daily 4:00) — full skill evolution cycle.

## The Problem

All three processes patch skills silently with NO human review:
- No before/after diff
- No rollback capability  
- No change log
- User only sees "💾 Patched SKILL.md in skill 'chain-heartbeat'"

## Oversight Solution (2026-07-23)

Three-layer oversight that catches ANY SKILL.md change from ANY source:

### Layer 1: Change Detection
`scripts/skill_watchdog.py` — runs every 10m via cron `cd51817b212e`:
- Scans ALL `skills/*/SKILL.md` files
- Compares sha256 hashes against previous snapshot (`cache/skill_hashes.json`)
- Logs any new/modified files to `cache/patch_journal.jsonl`
- Output: `[SILENT]` if no changes, or list of changes with old/new hashes

### Layer 2: Audit Trail
`cache/patch_journal.jsonl` — append-only JSONL log:
```json
{"ts":"2026-07-23T18:04:00","skill":"devops/chain-heartbeat","action":"updated","old_hash":"a1b2c3d4","new_hash":"e5f6g7h8","trigger":"watchdog","file":"skills/devops/chain-heartbeat/SKILL.md"}
```

### Layer 3: Daily Report
`scripts/daily_patch_review.py` — runs daily at 8:00 via cron:
- Reads patch journal for last 24h
- Groups by skill, counts changes
- Flags repeated patches on same skill (potential oscillation)
- Saves report to `reports/patch_review_*.md`
- Reports to user in their preferred channel

## Auto-Rollback (2026-07-23 update)

The watchdog now includes **built-in auto-rollback** — it validates every changed SKILL.md and reverts bad patches automatically WITHIN 10 MINUTES. No human needed.

### Validation Checks (skill_watchdog.py)

On detecting a SKILL.md change, the watchdog checks:

1. **Min lines** — must be ≥10 lines (corruption guard)
2. **Max lines** — must be ≤5000 (sanity cap)
3. **YAML frontmatter** — if starts with `---`, must have closing `---`
4. **name field** — YAML must contain `name:` field
5. **Null bytes** — no `\x00` in content (binary corruption)
6. **Frontmatter content** — must be ≥5 chars

### Rollback Flow

```
background_review patches SKILL.md  (anytime)
        ↓
  skill_watchdog runs (every 10m)
        ↓
  detects hash change, VALIDATES new content
        ↓
   ✓ VALID → accept, log to patch_journal.jsonl
   ❌ INVALID → restore from cache/skill_backups/<skill>/<old_hash>.bak
                log to patch_journal.jsonl as "ROLLED_BACK" with reason
```

### Backup System

- Every SKILL.md is backed up to `cache/skill_backups/<skill_name>/<sha256>.bak` on each scan
- Max 50 backups per skill (oldest auto-evicted)
- On rollback: find backup matching old_hash, restore, re-hash

### Key Design Decision: Reports Are For The SYSTEM, Not The User

User correction (2026-07-23): "отчёты это для тебя!!! мне они нахуй не нужны!!!"

When a bad patch is detected: **rollback silently**. The journal logs it for the system to audit. The user should NOT receive a daily report of patches — the system self-corrects. Only surface issues that the system CANNOT fix (e.g., no backup available for rollback).

### Journal Format (cache/patch_journal.jsonl)

```json
{"ts":"2026-07-23T18:04:00","skill":"devops/chain-heartbeat","action":"updated","old_hash":"a1b2c3d4","new_hash":"e5f6g7h8","trigger":"watchdog","file":"..."}
{"ts":"...","skill":"devops/chain-heartbeat","action":"ROLLED_BACK","old_hash":"...","new_hash":"REVERTED","reason":"too short (2 lines, min 10)","rolled_back":true,"file":"..."}
```
