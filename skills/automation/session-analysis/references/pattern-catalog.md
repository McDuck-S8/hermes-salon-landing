# Known Session Patterns

Catalog of recurring patterns detected across sessions. Use this to speed up pattern recognition in future analyses.

## User Behavior Patterns

### "Продолжай дальше" (Continue)
**Signal:** User sends short imperative like "продолжай", "делай дальше", "работай"
**Meaning:** User wants RESULTS, not plans. They've already approved the direction.
**Action:** Check what was in-progress, verify it's still running/working, report status, continue execution.

### Frustration Signals
**Signal:** "бляять", "опять", "снова", "почему не работает", CAPS LOCK
**Meaning:** Something is broken or repeating. User is losing patience.
**Action:** Stop planning, stop explaining. Fix the immediate blocker. Report what's broken and what you did to fix it.

### "Молодца" / Approval After Innovation
**Signal:** User praises after agent proposes something creative
**Meaning:** User values creative initiative, not just execution. Build on this.
**Action:** Note the winning approach for future sessions.

## Technical Patterns

### Missing Script in Cron Job
**Signal:** `auto_consult.py NOT FOUND`, repeated N times across cron runs
**Meaning:** Cron job was configured before the script existed, or script was deleted/moved.
**Action:** Create the script OR disable the cron job. Never let it fail silently N times.

### Terminal Broken on Windows (MSYS)
**Signal:** `cd: C:\Users\Asus: No such file or directory` in terminal()
**Cause:** MSYS/Git Bash can't resolve Windows home directory path.
**Workaround:** Use `execute_code` with `from hermes_tools import terminal` as wrapper, or specify `workdir` explicitly.

### Knowledge Base Not Growing
**Signal:** Same experience count across multiple analysis runs (e.g., "55 experiences" for 18+ hours)
**Meaning:** after() hook not firing, or sessions not being recorded.
**Action:** Manually seed experiences from recent completed sessions. Check hook registration.

### Recommendation Engine = Static Fallback
**Signal:** Every session gets identical recommendation regardless of domain
**Meaning:** Recommendation logic is a hardcoded string, not context-aware.
**Action:** Implement domain matching (devops vs business vs research), tool health checks, past success/failure filtering.

## Project Patterns

### Hotel CRM Bot Project (Crimea)
**Context:** User building AI chatbot for hotels in Crimea (Telegram, aiogram 3.x)
**Status:** Bot created (@HotelCrimeaBot), CRM database with 10 leads, 20 hotel contacts
**Stack:** Python, aiogram, SQLite, SOCKS5 proxy for Telegram API
**Key files:** `data/projects/crimea-bots/production_hotel_bot.py`, `data/plans/crm.db`
**Recurring need:** Bot restart, lead management, outreach to hotels

### Entity Engine (3 Cubes)
**Context:** User proposed knowledge system with 3 interconnected cubes
- **Knowledge Cube** — experiences and outcomes (55 entries)
- **Flёр Cube** — atmosphere/aura of interactions (4 entries)
- **Pattern Cube** — recurring behaviors and rhythms (4 entries)
**Location:** `~/.hermes/cache/entity_engine.db`
**Status:** Structure created, data sparse. Needs historical session processing.
