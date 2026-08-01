# Self-Diagnosis Findings — 2026-07-01

## Quick System Diagnosis Results

**Trigger:** User asked "проведи самодиагностку системы, выяви недостащие знания"
**Method:** Manual checks (self_system.py --status, procedural_executor --status, cronjob list, terminal)
**Output:** `cache/SELF_DIAGNOSIS_2026-07-01.md` (full report), `LESSONS.md` (12 lessons)

## Key Findings

### CRITICAL (3)
1. **Knowledge Cube DB empty (0 tables)** — Crystal v3 writes to JSON (`cache/crystal/`), not SQLite. `knowledge_cube.db` has 0 tables despite Crystal reporting 3333 experiences. Two separate storage systems, not connected.
2. **All API keys expired** — openai, anthropic, together, groq all EXPIRED. No fallback chain. Procedural executor can't refresh. Fix: use free providers (opencode-zen, ollama) as primary.
3. **Memory 84%** — Perplexity/Comet.exe = 6.7GB, chrome = 3.1GB, Code = 2.7GB, Telegram = 2.3GB. System slowdown, OOM risk.

### HIGH (4)
4. **DECISION_LOG stale 10+ days** — last real entries from 2026-06-21. No tracking of recent decisions.
5. **Goal Queue: 66 goals, 0 active** — all skipped/failed. Autonomous agent has no targets.
6. **3 cron jobs ERROR** — self-improvement-loop, self-upgrade-loop, ai-tools-hub-poster.
7. **Bayesian flow degraded** — P(alive)=0.6, daily rate 15.43, today 0 signals.

### MEDIUM (3)
8. **Telegram unreachable 4 days** — network watchdog shows unreachable since 2026-06-27.
9. **40% signal skip rate** — 88/215 signals skipped in pipeline.
10. **Crystal: 0 Knowledge Base entries** — 60K patterns not utilized.

### MISSING (5)
A. LESSONS.md didn't exist → created with 12 lessons
B. No proof-of-payment for any of 50 arbitrage bonds
C. No active revenue testing — all bonds UNVERIFIED
D. KC SQLite integration not working
E. Procedural executor feedback empty

### GOOD (6)
- State DB: 243MB, 44K messages, 384 sessions ✅
- Session Recall: 3000 indexed, BM25 working ✅
- Event System: 0 pending, 100 processed ✅
- Signal Daemon: RUNNING ✅
- Procedural Executor: 12 triggers, working ✅
- 9/15 cron jobs healthy ✅

## Diagnostic Commands Used

```bash
# System status
python scripts/self_system.py --status

# Procedural executor status (shows processes, disk, memory, alerts)
python scripts/procedural_executor.py --status

# Bayesian scorer
python scripts/bayesian_scorer.py --status

# Crystal summary
python scripts/crystal.py --summary

# Signal pipeline
python scripts/signal_pipeline.py --status

# DB sizes
python -c "import sqlite3,os; [print(f'{f}: {os.path.getsize(f)/1024/1024:.1f}MB') for f in ['state.db','knowledge_cube.db'] if os.path.exists(f)]"

# Knowledge Cube tables
python -c "import sqlite3; c=sqlite3.connect('knowledge_cube.db'); print([r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()])"

# Goal queue
python -c "import json; d=json.load(open('cache/goal_queue.json')); g=d if isinstance(d,list) else d.get('goals',[]); print(f'{len(g)} goals'); [print(f'  [{x.get(\"status\",\"?\")}] {x.get(\"title\",x.get(\"description\",\"?\"))[:60]}') for x in g[:5]]"

# Cron jobs (via cronjob tool)
# cronjob(action='list')
```

## New Patterns Discovered

### Memory Diagnosis on Windows
```bash
# Find RAM hogs
tasklist /FI "MEMUSAGE gt 1000000" /FO TABLE 2>/dev/null
# Or PowerShell:
powershell -Command "Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 10 Name,@{N='MB';E={[math]::Round($_.WorkingSet64/1MB)}}"
```

### API Key Health Check
```bash
# Check if keys exist (not expired — that requires API call)
grep -E "^(OPENAI|ANTHROPIC|TOGETHER|GROQ)_API_KEY" .env | sed 's/=.*/=***/'
```

### Quick System Vitals
```bash
# One-liner: DB sizes + process count + disk
python -c "
import sqlite3, os
for f in ['state.db', 'knowledge_cube.db']:
    if os.path.exists(f):
        sz = os.path.getsize(f)/1024/1024
        conn = sqlite3.connect(f)
        tables = [r[0] for r in conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()]
        print(f'{f}: {sz:.1f}MB, {len(tables)} tables: {tables[:5]}')
        conn.close()
"
```
