# Cron Script Restoration — 2026-07-12 (Session 2)

## Problem
6 cron scripts were dead or missing, referencing `~/.hermes/memory_tree/` (non-existent path).

| Script | Issue | Fix |
|---|---|---|
| `subconscious_loop_cron.py` | imported `memory_tree` (DNE) | Rewritten — reads events.db directly, spreads activation in KC |
| `dream_memory_cron.py` | script not found | Created — consolidates KC entries, finds cross-domain patterns |
| `self_analysis_cron.py` | script not found | Restored from blank — KC health + anomaly detection |
| `skill_evolution_v2.py` | script not found | Restored — skill usage pattern analysis |
| `memory_consolidate.py` | script not found | Restored — compress/prune old memories |
| `auto_fetch_cron.py` | referenced `memory_tree` (fallback) | Already delegated to session_dump_ingester |

## Root Cause
The original cron scripts were written for an external tool (`memory_tree` on `~/.hermes/`) that was removed. Scripts were never migrated to be standalone inside Hermes.

## Key Pattern: Self-Contained Cron Script

Every restored/recreated script follows:

```python
#!/usr/bin/env python3
"""DESCRIPTION — what it does. Self-contained inside Hermes."""
import sqlite3, json, sys
from datetime import datetime
from pathlib import Path

HERMES = Path(__file__).resolve().parent.parent  # NOT ~/.hermes/
KC_DB = HERMES / "cache" / "knowledge_cube.db"
EVENTS_DB = HERMES / "cache" / "events.db"

def main():
    # Operates on KC and events only — no external tools
    pass

main()
```

**Anti-patterns:**
- ❌ `subprocess.run(["python", "~/.hermes/memory_tree/scripts/..."])`
- ❌ Any reference to `memory_tree` or paths outside `HERMES_HOME`
- ❌ Wrappers that delegate to non-existent external tools

## Watchdog Created
`test_cron_scripts_exist.py` — permanent integrity checker. See `cron-maintenance` skill.

## Verification
All 6 scripts: `py_compile.compile()` + `python scripts/<name>.py` → exit 0. No external deps.
