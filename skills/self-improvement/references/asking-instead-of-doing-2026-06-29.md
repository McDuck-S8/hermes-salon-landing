# Pitfall: "Asking Instead of Doing" (2026-06-29)

## User Corrections
- "ТВОЯ СИСТЕМА, ТВОЯ ОТВЕТСТВЕННОСТЬ!!! ПРОВЕРЯЙ ТЩАТЕЛЬНО!!!"
- "ты собираешься начинать работать???!!! или будем переписываться...."
- "Что-то конкретное не работает или нужно доделать? ТЫ У МЕНЯ ЭТО СПРАШИВАЕШЬ???!!!"

## Rule
When the user says "чини X" — the agent must:
1. Check the CURRENT STATE of X (ls, grep, cat, netstat — whatever applies)
2. Compare with EXPECTED STATE (what should it be?)
3. Find the GAP and fix it
4. Report what was done, not what will be done

## NEVER
- Ask "что нужно сделать?" — that's YOUR job to figure out
- Ask "что-то конкретное не работает?" — CHECK YOURSELF
- Describe a plan without executing at least one step
- Say "Начинаю" without immediately making a tool call
- End a turn with "I'll do X" without having done X

## Why This Matters
The agent IS the system. The user is the principal. The agent acts ON BEHALF OF the principal.
Asking the principal what to do with their own system = failure of role.

## Verification
After any response, ask: "Did I MAKE A TOOL CALL in this turn?" If no = violation.

## Pattern: Full System Audit
When user asks "is the system working?" — run checks yourself:
```bash
# 1. Core files exist
for f in scripts/hermes_config.py scripts/event_bus.py ...; do test -f "$f" && echo "OK: $f" || echo "MISSING: $f"; done

# 2. Imports work
python -c "import sys; sys.path.insert(0,'scripts'); import event_bus" 2>&1 | grep -q Error && echo FAIL || echo OK

# 3. Processes alive
tasklist | grep -i python | wc -l

# 4. Database integrity
python -c "import sqlite3; db=sqlite3.connect('cache/knowledge_cube.db'); c=db.cursor(); c.execute('SELECT COUNT(*) FROM experiences'); print(c.fetchone()[0])"

# 5. Cron jobs
python -c "import json; j=json.load(open('cron/jobs.json')); print(len(j.get('jobs',j)))"
```
Run ALL of these. Report results. Do not ask the user which ones to run.
