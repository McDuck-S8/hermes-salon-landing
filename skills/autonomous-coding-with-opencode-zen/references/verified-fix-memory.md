# Verified Fix Memory — Local Knowledge Capture (No Docker)

## Problem
Supermemory requires Docker, which isn't always available. Need a **local, lightweight** way to store and retrieve verified fixes for the proactive executor loop.

## Solution: `scripts/verified_fix_memory.py`

### Features
- **Local SQLite** database (`cache/verified_fixes.db`)
- **Optional embeddings** via `sentence-transformers` (all-MiniLM-L6-v2) for semantic search
- **Fallback to keyword search** if embeddings unavailable
- **Deduplication** via SHA256 hash of issue_type + description
- **Verified-only storage** — only fixes with `verified=true` and `evidence` are stored

### Schema
```sql
CREATE TABLE verified_fixes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_hash TEXT UNIQUE NOT NULL,      -- SHA256(issue_type:description)[:16]
    issue_type TEXT NOT NULL,             -- "indentation_error", "timeout", etc.
    issue_description TEXT NOT NULL,      -- Original issue text
    fix_type TEXT NOT NULL,               -- "patch", "command", "investigation"
    fix_description TEXT NOT NULL,        -- What the fix does
    fix_content TEXT,                     -- Unified diff or command
    target_file TEXT,                     -- File that was fixed
    evidence TEXT,                        -- "py_compile PASSED + pytest PASSED"
    tags TEXT,                            -- JSON array
    embedding BLOB,                       -- Serialized numpy array (float32)
    created_at TEXT NOT NULL,
    verified_at TEXT NOT NULL
)
```

### API
```python
from scripts.verified_fix_memory import (
    store_verified_fix,
    query_similar_fixes,
    get_stats,
    on_verified_fix  # Convenience for hermes_hooks integration
)

# Store a verified fix
stored = store_verified_fix(
    issue_type="indentation_error",
    issue_description="IndentationError in proactive_executor.py line 1024",
    fix_type="patch",
    fix_description="Fixed missing indentation after if statement",
    fix_content="--- a/scripts/proactive_executor.py\n+++ b/scripts/proactive_executor.py\n@@ -1021,7 +1021,7 @@\n                 )\n \n-    if not errors:\n+    if not errors:\n         report(\"  No cron jobs with errors detected — all green\")",
    target_file="scripts/proactive_executor.py",
    evidence="python -m py_compile scripts/proactive_executor.py PASSED",
    tags=["indentation", "proactive", "auto-fix"]
)

# Query for similar fixes (semantic search if embeddings available)
results = query_similar_fixes("IndentationError proactive_executor", limit=5)

# Statistics
stats = get_stats()  # {"total_fixes": 2, "issue_types": 1}

# Convenience for hooks integration
on_verified_fix(issue_id, issue_type, issue_description, fix_result)
```

### Integration with `hermes_hooks.py`
```python
# In HermesEventHooks.on_task_complete()
def on_task_complete(self, task_description, result, tags, verified=False, evidence="", fix_result=None):
    # ... existing code ...
    if verified and evidence and HAS_VERIFIED_MEMORY and fix_result:
        issue_id = tags[0] if tags else "unknown"
        issue_type = tags[1] if len(tags) > 1 else "proactive_fix"
        on_verified_fix(issue_id, issue_type, task_description, fix_result)
```

### In `proactive_executor.py` after verification:
```python
fix_results = apply_llm_suggested_fixes(suggested_fixes)
for applied_fix in fix_results["applied"]:
    if verify_fix_result(applied_fix, target_file):
        hooks.on_task_complete(
            task_description=f"Applied fix: {applied_fix['fix']['description']}",
            result="Patch applied and verified",
            tags=["proactive", "verified", applied_fix['fix'].get('fix_type')],
            verified=True,
            evidence="py_compile passed + pytest passed",
            fix_result=applied_fix['fix']
        )
```

### Embedding Model
- **Default**: `sentence-transformers/all-MiniLM-L6-v2` (384 dim, fast, good quality)
- **Fallback**: Pure keyword search (no dependencies)
- **Install**: `pip install sentence-transformers`

### Why Not Supermemory?
| Supermemory | Verified Fix Memory |
|-------------|---------------------|
| Requires Docker | Pure Python, no Docker |
| External service | Local SQLite file |
| Heavy | Lightweight (~50KB) |
| Network call | In-process |

### Files Created
- `scripts/verified_fix_memory.py` — Main module
- `cache/verified_fixes.db` — SQLite database (auto-created)

### Usage in Autonomous Loop
```
proactive_executor (Phase 2.5)
    → apply_llm_suggested_fixes()
    → verify_fix_result()  # syntax + pytest
    → hooks.on_task_complete(verified=True, evidence="...")
    → verified_fix_memory.store_verified_fix()
    → NEXT RUN: query_similar_fixes() finds existing solution
```

This closes the **Information → Knowledge** loop locally without any external dependencies.