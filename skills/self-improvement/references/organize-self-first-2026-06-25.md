# Organize Self First, Projects Later (2026-06-25)

## Core Lesson
User correction: "Salon bot is a PROJECT — a side effect of being well-organized.
Organize yourself to that level FIRST. Projects come like pancakes after."

The agent was chasing salon bot instead of building the foundation.
A well-organized system produces projects effortlessly;
a disorganized system produces broken projects.

## What "Organized" Means
1. **Knowledge Cube clean** — no auto-generated junk, proper categories
2. **Cron jobs working** — no broken jobs, network-dependent disabled when offline
3. **Health checks running** — heartbeat script that actually works
4. **Daily workflow defined** — boot → health → kanban → execute → record → save
5. **Memory clean** — stale entries removed, learnings consolidated
6. **Scripts lean** — dead code in _deprecated, only active scripts in scripts/

## Self-Organization Checklist
```bash
# 1. Knowledge Cube cleanup
sqlite3 cache/knowledge_cube.db "DELETE FROM kc_entries WHERE category='tools'"  # auto-generated junk
sqlite3 cache/knowledge_cube.db "SELECT category, COUNT(*) FROM kc_entries GROUP BY category"

# 2. Cron cleanup (offline environment)
# Disable network-dependent jobs: trend_scout, market_research, curiosity-engine, etc.
# Fix script-not-found jobs: update script path or disable

# 3. Health check
python scripts/hermes_heartbeat.py  # should output network + gateway status

# 4. Memory cleanup
# Remove stale entries, consolidate learnings

# 5. Scripts cleanup
# Move dead scripts to _deprecated/
```

## Fear→Action→System Pattern
The deeper pattern behind "act instead of plan":
1. Fear of failure → analysis paralysis
2. Analysis → no action → no results
3. No results → more fear → more analysis

The escape: build a SYSTEM that makes acting easy:
- Health checks tell you what's broken (so you don't have to guess)
- KC tells you what you know (so you don't have to research)
- Cron tells you what's running (so you don't have to check manually)
- Workflow tells you what to do next (so you don't have to decide)

When the system is organized, acting is trivial. When it's not, every action feels risky.

## Practical Techniques

### KC Cleanup Pattern
```python
import sqlite3
db = sqlite3.connect('cache/knowledge_cube.db')
# Remove auto-generated entries
db.execute("DELETE FROM kc_entries WHERE category='tools'")
# Categorize uncategorized
db.execute("UPDATE kc_entries SET category='research' WHERE category IS NULL OR category=''")
db.commit()
```

### Cron Cleanup for Offline Environments
Disable jobs that need network:
- trend_scout, market_research, curiosity-engine, knowledge-gap-filler, uncertainty-observer
Keep jobs that work offline:
- self-improvement-cycle, heartbeat, cube-to-memory

### load_insights() Merge Pattern
When loading JSON state that may be missing keys:
```python
def load_insights():
    defaults = {"cycles": 0, "insights": [], "errors_seen": {}, "network_checks": 0, "network_fails": 0}
    try:
        data = json.loads(INSIGHTS_FILE.read_text())
        defaults.update(data)  # Merge: existing data overrides defaults
        return defaults
    except:
        return defaults
```
This prevents KeyError when the JSON file exists but is missing newer keys.
