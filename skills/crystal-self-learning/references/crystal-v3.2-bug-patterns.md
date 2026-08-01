# Bug Patterns Found in Crystal v3.2 (June 2026)

## Assessment.__post_init__ Override Bug

**File:** `scripts/crystal/models.py`, Assessment class, line 247
**Bug:** `self.success = self.delta > 0` in `__post_init__` silently overwrote the `success` parameter passed to the constructor.
**Effect:** ALL proposals evaluated as failed (success=False) even when executor returned success=True. 0/85 success rate in --cycle.
**Root cause:** In dry-run mode, before == after (no state change), so delta=0, so `delta > 0` = False.
**Fix:** Removed the override line. Now `success` is whatever the caller passes.
**Lesson:** dataclasses with `__post_init__` can silently overwrite constructor arguments. Always inspect `__post_init__` before trusting passed values.

## Duplicate Skill Names

**File:** `scripts/crystal/executor.py`, `_create_skill()`
**Bug:** All proposals from same department generated `crystal-{dept}-auto`. First creates, rest fail "already exists".
**Effect:** 1 success + (N-1) silent failures per department.
**Fix:** Use `crystal-{dept}-{abs(hash(description)) % 10000}` for unique names.
**Lesson:** When generating N artifacts, every name must be unique.

## Missing Action Mapping

**File:** `scripts/crystal/executor.py`, `_execute_one()`
**Bug:** ConversationAnalyzer generates actions not in executor's known list.
**Effect:** All proposals fail silently with "unknown action".
**Fix:** Map new actions to closest known handler.
**Lesson:** When a new module produces data consumed by an existing module, verify the interface contract.

## Chinese Characters in Python Code

**File:** `scripts/crystal/feedback_loop.py`
**Bug:** Docstrings contained Chinese (提案, 提议).
**Effect:** UnicodeEncodeError on Windows console.
**Fix:** Replaced with Russian equivalents.
**Lesson:** Windows console encoding — no non-ASCII in Python output.
