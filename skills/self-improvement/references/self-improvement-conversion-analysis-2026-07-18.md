# Self-Improvement Loop Conversion Analysis — 2026-07-18

## The Problem
**17,704 suggestions → 19 skills = 0.11% conversion** (target: 1%)

## Root Cause Analysis

### 1. Verified Fixes DB is Empty
- **File:** `/d/Portable_Soft/hermes/cache/verified_fixes.db`
- **Tables:** 0 (no `verified_fixes` table)
- **Impact:** `load_verified_fixes()` returns `[]` — the primary signal source is dead

### 2. Knowledge Cube is Empty
- **File:** `/d/Portable_Soft/hermes/cache/knowledge_cube.db` (11MB but 0 tables)
- **Tables:** 0 — schema never initialized because `knowledge_cube.get_db()` never called
- **Impact:** `load_cube_experiences()` returns `[]` — no domain/failure pattern analysis possible

### 3. Log Analysis = Noise, Not Signal
| Error Type | Count | Reality |
|------------|-------|---------|
| `log_artifact` | 141 | **SUCCESS logging** ("-> Documented pattern: ..."), not errors |
| `telegram_error` | 116 | Network timeouts (infrastructure), not code bugs |
| `tool_error` | 37 | Terminal timeouts (resource limits), not patterns |
| **Total clusters** | 275 | **>90% false positives** |

### 4. Suggestions = Duplicates & Templates
- 32 suggestions in current output
- 17 "critical" = all `log_artifact` / `telegram_error` / `tool_error` — infrastructure noise
- Duplicate IDs for same pattern (e.g., `log-error-log_artifact-3886` AND `log-error-log_artifact-2675` both count=141)
- Generic template actions: "Add guard", "Add pre-commit validation" — not specific fixes

### 5. Auto-Skills = Checklists, Not Code
```markdown
## Prevention Checklist
- [ ] Add guard/check for this pattern
- [ ] Add pre-commit validation
- [ ] Create regression test
- [ ] Document in knowledge base
```
These are **TODOs**, not working solutions. No executable code, no tests, no integration.

### 6. Knowledge Write-Back = 0
- `total_knowledge_entries_written`: 0 across all 32 runs
- Tables don't exist in KC DB
- Loop writes to KC but DB schema never created

### 7. No Feedback Loop Exists
```
Suggestions JSON → (nothing reads it) 
    → Auto-skills → (nothing uses them) 
    → Loop repeats
```
The cron job runs, writes JSON, creates template skills, exits. Nothing consumes output.

---

## Fix Plan (3 Days → 1%)

| Day | Action | Target |
|-----|--------|--------|
| **1** | Wire `hermes_hooks.on_error()` + `on_task_complete()` to write to `verified_fixes.db` | Populate verified fixes |
| **1** | Call `knowledge_cube.get_db()` at startup to initialize schema | Enable KC experience mining |
| **2** | Filter log noise: exclude `log_artifact`, `telegram_timeout`, `terminal_timeout` | Reduce false positives 80% |
| **2** | Change auto-skill from template → **executable fix** (patch file + test) | Skills become usable |
| **3** | Add suggestion consumer: cron job that reads `improvement_suggestions.json` and **applies top fix** | Close the loop |

---

## Immediate Commands to Run

```bash
# 1. Initialize KC schema
/d/Program\ Files/Python311/python -c "from scripts.knowledge_cube import get_db; get_db(); print('KC initialized')"

# 2. Initialize verified_fixes schema
/d/Program\ Files/Python311/python -c "
import sqlite3
conn = sqlite3.connect('/d/Portable_Soft/hermes/cache/verified_fixes.db')
conn.execute('''CREATE TABLE IF NOT EXISTS verified_fixes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_type TEXT, fix_description TEXT, tags TEXT, source TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP, verified_at TEXT
)''')
conn.commit(); print('Verified fixes DB initialized')
"

# 3. Verify both work
/d/Program\ Files/Python311/python -c "
import sqlite3
for db, table in [('cache/knowledge_cube.db', 'experiences'), ('cache/verified_fixes.db', 'verified_fixes')]:
    conn = sqlite3.connect(f'/d/Portable_Soft/hermes/{db}')
    c = conn.cursor()
    c.execute(f'SELECT COUNT(*) FROM {table}')
    print(f'{db}.{table}: {c.fetchone()[0]} rows')
    conn.close()
"
```

---

## Key Lesson

**Self-improvement loop was "reporting without doing"** — it analyzed noise, generated template suggestions, created checklist skills, and called it done. The loop is broken at every stage:

1. **No data in** → verified_fixes empty, KC empty
2. **Noise analysis** → log patterns are infrastructure, not bugs
3. **No specificity** → suggestions are generic templates
4. **No execution** → auto-skills are TODO lists
5. **No feedback** → nothing reads suggestions, loop repeats

**Fix the pipeline first, then the conversion will follow.**