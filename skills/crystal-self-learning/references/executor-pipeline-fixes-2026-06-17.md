# Executor Pipeline Fixes — 2026-06-17

## Assessment.__post_init__ Bug

**File:** `scripts/crystal/models.py` line 247
**Bug:** `self.success = self.delta > 0` in `Assessment.__post_init__` OVERWROTE the `success` parameter passed by the caller.
**Effect:** All proposals evaluated as failed (success=False) even when executor returned success=True. Delta=0 in dry-run meant success always False.
**Fix:** Removed the override line. `self.success` now preserves the value passed by `_assess()`.
**Lesson:** When using dataclasses with `__post_init__`, check for side effects that silently overwrite constructor arguments.

## Executor Action Mapping

**File:** `scripts/crystal/executor.py` `_execute_one()` method
**Bug:** ConversationAnalyzer generates actions (`implement_idea`, `fix_problem`, `create_feature`, `optimize`, `try_experiment`, `fix_gap`) that ProposalExecutor didn't recognize.
**Effect:** All proposals silently failed with "unknown action" error.
**Fix:** Added explicit mapping:
```python
elif proposal.action in ("implement_idea", "create_feature", "fix_gap", "optimize"):
    return self._create_skill(proposal)
elif proposal.action in ("fix_problem", "try_experiment"):
    return self._patch_skill(proposal)
```
**Lesson:** When a new module generates data consumed by an existing module, verify the interface contract — names, types, allowed values — or failures are silent.

## Duplicate Skill Names

**File:** `scripts/crystal/executor.py` `_create_skill()` method
**Bug:** All proposals from the same department tried to create `crystal-{dept}-auto` — first succeeds, rest fail with "already exists".
**Effect:** 1 success + (N-1) silent failures per department.
**Fix:** Use `crystal-{dept}-{hash(description) % 10000}` for unique names.
**Lesson:** When generating N items that create N artifacts, every artifact name must be unique.

## patch_skill → create_skill Fallback

**File:** `scripts/crystal/executor.py` `_execute_one()` method
**Bug:** When executor received a `patch_skill` proposal but the target skill didn't exist, it returned failure instead of creating a new skill.
**Effect:** All proposals for new departments silently failed.
**Fix:** Check `_patch_skill` result; if `success=False` and error contains "не найден" → route to `_create_skill`.
**Lesson:** Proposal actions that assume pre-existing artifacts need graceful degradation when the artifact doesn't exist yet.

## Skills Must Contain Real Data

**File:** `scripts/crystal/executor.py` `_create_skill()` method
**Bug:** Originally generated placeholder SKILL.md with just a name and "Purpose: created for dept X".
**Effect:** Useless files — a skill with no actionable content wastes space.
**Fix:** `_create_skill` now calls `_generate_error_content()` which pulls actual errors from `ErrorAnalyzer` and actual fixes.
**Lesson:** If you're going to create an artifact, it must contain real value. A template is not a result.

## Conversation Analyzer Integration

**File:** `scripts/crystal/core.py` `propose()` method
**Bug:** ConversationAnalyzer results weren't fed into needs pipeline. The `propose()` method only read `self.needs` (from pattern detection), not conversation analysis.
**Effect:** Crystal generated needs from log errors instead of user goals.
**Fix:** `analyze_conversation()` integrated into `propose()` — but STILL only adds error-based proposals, not user-goal-based proposals.
**Status:** PARTIAL FIX — the two pipelines are still disconnected. See `references/crystal-orientation-problem.md`.
