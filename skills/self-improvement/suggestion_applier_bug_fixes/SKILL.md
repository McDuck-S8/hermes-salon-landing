---
name: suggestion_applier_bug_fixes
description: Bug fixes and hardening for Suggestion Applier (2026-08-01 session)
category: self-improvement
---

# Bug Fixes & Hardening (2026-08-01) — This Session

## HERMES_HOME Path Resolution Fix

**Problem**: The `apply_suggestion()` for `fix_file` action was resolving file paths relative to the current working directory (CWD) instead of `HERMES_HOME`. When the applier ran from `scripts/` directory, file paths like `CLAUDE.md` resolved to `scripts/CLAUDE.md` instead of `HERMES_HOME/CLAUDE.md`.

**Root Cause**: In `_fix_file()`, `_register_skill()`, and `_add_revisit()`, target paths were constructed using `Path(file_path)` without prepending `HERMES_HOME`.

**Fix**: Prepend `HERMES_HOME` to all target file paths in `_register_skill()`, `_add_revisit()`, and `_fix_file()`:

```python
# Before (broken):
target_path = Path(target_file)

# After (fixed):
target_path = HERMES_HOME / target_file
```

**Files Modified**: `scripts/suggestion_applier.py` — methods `_register_skill()`, `_add_revisit()`, `_fix_file()`.

**Verification**: Both `impeccable` and `maintenance-scanner` skills now auto-register correctly in `CLAUDE.md` and `.claude/rules/always.md` when applier runs from `scripts/` directory.

---

## ext_guard.py Import & Dispatch Fix

**Problem**: The `apply_ext_guard` function was defined but not imported in the `FIX_DISPATCH` mapping, so `log-ext` and `log-error-ext` issue types had no handler.

**Fix**: Added import and dispatch entry:

```python
# In suggestion_applier.py imports:
from scripts.ext_guard import apply_ext_guard

# In FIX_DISPATCH:
"log-ext": apply_ext_guard,
"log-error-ext": apply_ext_guard,
```

---

## Cron Fallback Job Added

**Problem**: Suggestion Applier only ran on `new_suggestions_ready` event. If the event didn't fire, suggestions would queue indefinitely.

**Solution**: Added fallback cron job in `cron/jobs.json`:

```json
{
  "id": "suggestion-applier",
  "name": "suggestion-applier",
  "script": "suggestion_applier.py",
  "no_agent": true,
  "schedule": {"kind": "cron", "expr": "*/30 * * * *"},
  "enabled": true
}
```

Runs every 30 minutes as fallback to event-driven execution.

---

## Skill Usage Analyzer Integration

**New Integration**: Suggestion Applier now receives suggestions from `skill_usage_analyzer.py`:

| Issue Type | Action | Description |
|------------|--------|-------------|
| `register_skill` | Auto-register skill in CLAUDE.md + .claude/rules/always.md |
| `add_revisit` | Add Revisit frontmatter to files missing it |
| `fix_file` | Fix subagent_verifier findings |

**Verified**: Both `impeccable` and `maintenance-scanner` skills auto-registered in `CLAUDE.md` and `.claude/rules/always.md` when analyzer ran with `--execute`.

---

## Applied Log Corruption Handling

**Problem**: `cache/applied_suggestions.json` was stored as dict `{"failed": [...]}`, not a list. `load_applied()` crashed on `.append()`.

**Fix**: `load_applied()` now handles both formats:

```python
data = json.loads(self.applied_log.read_text(encoding="utf-8"))
if isinstance(data, list):
    return data
elif isinstance(data, dict) and "failed" in data:
    return data["failed"]
return []
```

---

## Nested Payload Extraction Bug Fix

**Problem**: Suggestion queue stores items as `{source, skill, action, payload}` where actual action lives in `payload.payload`. Original code checked `payload.get("action")` which was always `None`.

**Fix** in `apply_suggestion()`:

```python
# Before (broken):
if source == "skill_usage_analyzer" and payload.get("action") == "register_skill":

# After (fixed):
inner = payload.get("payload", {})
action = inner.get("action", "")
if source == "skill_usage_analyzer" and action == "register_skill":
    return self._register_skill(inner)
```

**Affected Actions**: `register_skill`, `add_revisit`, `fix_file`.