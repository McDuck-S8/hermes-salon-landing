# Hermes Boot Flow — Known Issues and Fixes

## hermes_start.py Import Chain

The boot script (`hermes_start.py`) imports and runs these modules in order:
1. `session_boot` → `boot()` — full session bootstrap (dumps, KC, goals, context)
2. `session_context` → `build_context()` — returns **str**, not dict
3. `goal_queue` → `get_active_goals()` — returns list of active goals
4. `goal_executor` → `execute_goal()` — executes highest-priority goal

## Known Bugs (fixed 2026-06-30)

### Bug 1: build_context() return type mismatch
- `session_context.py:build_context()` returns a formatted **string**
- `hermes_start.py` calls `ctx.keys()` assuming it's a **dict**
- **Fix:** Added `isinstance(ctx, dict)` check in hermes_start.py
- **Fix location:** hermes_start.py line ~24

### Bug 2: session_manifest.py missing
- `session_boot.py` Step 14 tries to import `session_manifest.py` via `importlib.util.spec_from_file_location()`
- File didn't exist → `FileNotFoundError`
- **Fix (temporary):** Added `manifest_path.exists()` guard in session_boot.py
- **Fix (permanent):** Created `scripts/session_manifest.py` with `verify_manifest()` and `record_changes()`

### Bug 3: Event chain 0/0 steps
- `Chain: 0/0 steps succeeded` — event chain doesn't find steps
- Root cause: event classifier classifies boot as `action_completed` (low confidence) → chain finds no matching steps
- **Status:** Cosmetic — doesn't affect functionality

## session_manifest.py API

```python
from session_manifest import verify_manifest, record_changes

# Record current file hashes
record_changes(["scripts/event_bus.py", "scripts/goal_executor.py", ...])

# Verify against recorded hashes
result = verify_manifest()
# Returns: {"verified": [...], "broken": [{"file": ..., "reason": ...}]}
```

## Boot Output Format

```
=== HERMES BOOT ===
  session_boot: OK (N dumps, N errors)
  session_context: OK (N chars)
  goals: N active
  tool_catalog: EXISTS
  autonomous_action: EXECUTED goal {id} — {status}
=== BOOT DONE ===
```
