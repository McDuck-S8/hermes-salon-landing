# Proactivity Implementations — 2026-06-07 v2

Major overhaul: error-alerter removed, proactive-executor rewritten, cube-categorizer created, telegram-delivery fixed.

## Architecture (Current, 2026-06-07)

```
                                              ┌─────────────────────┐
                                              │  Skill Auto-Evol.   │
                                              │  04:00 daily        │
                                              │  ─ creates/updates  │
                                              │  skills from Cube   │
                                              └────────┬────────────┘
                                                       │ reads
                                                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE CUBE LAYER                          │
│  cache/knowledge_cube.db  (619 entries, 12 domains)              │
│                                                                  │
│  cube-feeder (04:15 daily) → feeds sessions into Cube            │
│  cube-categorizer (every 6h) → labels uncategorized entries      │
│  cube-to-memory (every 6h) → Cube → .lavra/memory/knowledge.jsonl│
│  dimension-discovery (04:45 daily) → finds new Cube dimensions   │
│  knowledge-surfacer (every 6h) → generates reports               │
└──────────────────────────┬───────────────────────────────────────┘
                           │ feeds
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                    PROACTIVE ENGINE LAYER                        │
│                                                                  │
│  proactive-executor (every 15m) → reads Cube gaps, fixes crons   │
│  result-producer (every 30m) → replaces error_alerter            │
│  self-healing-monitor (every 15m) → restarts dead cron jobs      │
│  system-watcher (every 60m) → health checks + backlog detection  │
└──────────────────────────┬───────────────────────────────────────┘
                           │ reports
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                    DELIVERY LAYER                                │
│                                                                  │
│  telegram-delivery (every 60m) → sends reports to TG             │
│  unified-system-cycle (every 120m) → deep analysis               │
└──────────────────────────────────────────────────────────────────┘
```

## Script 1: proactive_executor.py (REWRITTEN 2026-06-07)

**Path:** `D:/Portable_Soft/hermes/scripts/proactive_executor.py`  
**Schedule:** every 15min (no_agent=True)

### Before v2
Only did VACUUM + "search for creative domain" + "suggest skill for DB maintenance".  
Useless noise — ran every 15min with zero observable effect.

### v2 — Knowledge-Driven Fix Engine
3 phases per run:

**Phase 1 — Knowledge Cube Analysis**  
- Queries `cache/knowledge_cube.db`: count per domain, newest entry, gaps  
- Reports domains with 0 entries (architecture, bugfix, learning)  
- Tracks uncategorized entries for trend monitoring

**Phase 2 — Cron Error Scan**  
- Reads `cron/output/<job_id>/*.md` for each registered job  
- Detects errors: exit code 1, traceback, timeout  
- Classifies: auto-fixable vs manual-fix-needed

**Phase 3 — Apply Fixes**  
Known fixers with results from first run:
1. **Telegram CHAT_ID** — scanned config.yaml + channel_directory.json, found `id=737433175`, wrote to `.env`. FIXED.
2. **Knowledge gaps** — probed `knowledge_gaps` table schema for auto-fill. Table lacks textual columns → reported as manual task.
3. **DB maintenance** — `PRAGMA optimize` on databases >10MB instead of wasteful full VACUUM.
4. **Stale action cleanup** — marks old VACUUM actions as 'stale' in proactive_actions table.

### Output Format
```
============================================================
PROACTIVE EXECUTOR v2 — Knowledge-Driven Fixes
Started: 2026-06-07 21:43:49
============================================================

[Phase 1] Knowledge Cube Analysis
  Total experiences: 619
  Domains: browser=27, coding=112, communication=34, creative=1, ...
  [GAP] domain 'architecture' has 0 entries
  [GAP] domain 'bugfix' has 0 entries

[Phase 2] Cron Job Error Scan
  [ERROR] free-api-health-check: Script exited with code 1
    → Qwen API port 3264 not responding

[Phase 3] Applied Fixes
  ✅ Telegram CHAT_ID: found 737433175, written to .env

Summary: 3 issues found, 1 fixed, 2 need manual action (elapsed: 1.2s)
```

## Script 2: result_producer.py (CREATED 2026-06-07, replaces error_alerter)

**Path:** `D:/Portable_Soft/hermes/scripts/result_producer.py`  
**Schedule:** every 30min (no_agent=True)

### Why It Exists
User correction: "а нахрена мне -и пинает в Telegram при ошибках мне нужен результат"  
Old `error-alerter` sent Telegram messages to @max_brain_chef_official every 5min for EVERY cron error.  
**REMOVED 2026-06-07.** Replaced with a fixer.

### Architecture
```python
FIXERS = {
    "telegram-delivery": fix_telegram,      # check + fix chat_id
    "free-api-health-check": fix_qwen,       # try restart Qwen proxy
}

def check_cron_errors():
    """Find cron jobs that errored in last run."""
    for jid_dir in cron_output_dirs:
        latest_run = read_latest_output(jid_dir)
        if has_error(latest_run):
            errors.append(jid_dir.name)

def main():
    errors = check_cron_errors()
    for name in errors:
        fixer = FIXERS.get(name)
        if fixer:
            result = fixer()
            print(f"🔧 [{name}] {result}")      # FIXED result
        else:
            print(f"ℹ️ [{name}] needs manual fix: {diagnosis}")
    print(f"📊 Disk free: {shutil.disk_usage(HERMES).free / 1e9:.1f} GB")
```

### Key Difference from error_alerter
| Aspect | Old (error-alerter) | New (result-producer) |
|--------|-------------------|----------------------|
| Interval | 5min | 30min |
| Action | Report error → ping TG | Try to fix → report outcome |
| User sees | "ERROR: X failed" | "🔧 Fixed X: restarted" |
| Value | Attention waste | Actual fix |

## Script 3: cube_categorizer.py (CREATED 2026-06-07)

**Path:** `D:/Portable_Soft/hermes/scripts/cube_categorizer.py`  
**Schedule:** every 6h (no_agent=True, job `faaa775374fb`)

### Problem It Solves
366/619 entries (59%) tagged `uncategorized`. The Knowledge Cube was a raw session dump — domain-specific queries returned nothing useful because everything was uncategorized.

### How It Works
10 domain rule sets with keyword heuristics. Order matters — first match wins:
```python
DOMAIN_RULES = [
    (["error", "bug", "crash", "traceback", "exception"], "debugging"),
    (["install", "setup", "deploy", "docker", "migrat"], "devops"),
    (["write", "code", "function", "class", "def "], "coding"),
    (["search", "research", "find", "lookup", "найди"], "research"),
    (["terminal", "bash", "command", "run", "запуст"], "terminal"),
    (["browser", "navigate", "click", "page", "url"], "browser"),
    (["telegram", "send", "message", "чат", "отправ"], "communication"),
    (["file", "folder", "copy", "move", "delete"], "file_ops"),
    (["system", "status", "check", "hi", "hello"], "system"),
    (["data", "analyz", "statistic", "report"], "data"),
]
```

### First Run Results (2026-06-07)
- **94 entries categorized** into 10 domains
- **272 remain uncategorized** (short conversational fragments: "ну что там", "привет", "test")
- New domains created: `debugging` (10 entries), `terminal` (19 entries)
- Distribution: terminal=19, coding=10, debugging=10, research=10, communication=13, system=13, browser=6, devops=8, file_ops=3, data=2

### Future Improvements
- Add `--llm` mode for remaining 272 entries (batch classify via LLM)
- Store classification confidence score in new `classification_score` column
- Auto-add new domain patterns when they emerge

## Script 4: telegram_delivery_report.py (REWRITTEN 2026-06-07)

**Path:** `D:/Portable_Soft/hermes/scripts/telegram_delivery_report.py`  
**Schedule:** every 60min (no_agent=True)

### Before Fix
Failed with `CHAT_ID не указан` — cron subprocess didn't pass `--chat-id` arg, no fallback.

### After Fix — 5-Tier CHAT_ID Resolution
```
1. CLI arg --chat-id     → direct override
2. CHAT_ID env var       → from .env or environment
3. config.yaml           → telegram.home_chat / chat_id / allowed_chats[0]
4. channel_directory.json → first telegram chat's id
5. Final fallback        → @max_brain_chef_official
```
Also: sends reports as Telegram messages using `send_telegram_message()` from telegram_bridge.py (direct import, not subprocess).

### Resolved chat_id
Found `737433175` (numeric DM chat of user Александр) from `channel_directory.json`.

## Cleanup: Removed error-alerter (2026-06-07)

Removed job `error-alerter` (every 5min). Was pinging @max_brain_chef_official with every cron error.  
**Replaced by:** `result-producer` (every 30min, fixes before reporting).

## Updates: proactive-executor and telegram-delivery crons

- `proactive-executor` (job `1245c0fb6fa3`) — script updated to v2
- `telegram-delivery` (job `373127b8a1aa`) — script rewritten with CHAT_ID fallback

## New crons created 2026-06-07

| Job | Interval | Script | Purpose |
|-----|----------|--------|---------|
| result-producer | 30min | result_producer.py | Fix errors, don't alert them |
| cube-categorizer | 6h | cube_categorizer.py | Label uncategorized Cube entries |
| skill-evolution | 4h (v2) | skill_evolution_v2.py | Create skills from Cube patterns |

## Skill Auto-Evolution Pipeline (2026-06-07)

```
cube-feeder (04:15 daily)        → feeds sessions into Knowledge Cube
cube-categorizer (every 6h)      → labels uncategorized entries
skill-evolution (04:00 daily)    → creates/updates skills from Cube domains
proactive-executor (every 15m)   → applies Cube insights as fixes
result-producer (every 30m)      → replaces alerters with fixers
```

This pipeline ensures user sessions → structured data → actionable skills → system improvement, with no manual intervention and no Telegram pings about errors.

## Future Work (Not Implemented)
- **Auto-fill knowledge gaps:** `knowledge_gaps` table has 60 gaps. Need `topic` column or LLM fill.
- **Retry mechanism:** Failed proactive actions should retry with backoff (currently skip permanently).
- **Priority queuing:** Error events > informational events in processing order.
- **Feedback loop:** Verify whether proactive actions actually fixed the problem.
- **Live gateway health-check:** Ping gateway endpoint, auto-restart if down.
