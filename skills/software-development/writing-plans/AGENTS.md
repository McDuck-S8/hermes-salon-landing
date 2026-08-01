# writing-plans (software-development) — Skill

## Purpose
Write implementation plans: bite-sized tasks, paths, code.

## Ownership
Managed by Hermes Agent. Located in `software-development/writing-plans/`. Note: There's also a `superpowers/writing-plans/` skill with different focus.

## Local Contracts
- **Triggers**: Multi-step features, complex requirements, before delegating to subagents via subagent-driven-development
- **Required tools**: `search_files`, `read_file`, `write_file`, `terminal` (for git, exploration)
- **Config**: No config.yaml required
- **Related skills**: `subagent-driven-development`, `test-driven-development`, `requesting-code-review`

## Work Guidance
**When to use**: ALWAYS before multi-step features, complex breakdowns, or delegating to subagents. Don't skip even for "simple" features or solo work.

**Plan structure (mandatory header + bite-sized tasks)**:
```
# [Feature Name] Implementation Plan
> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** [One sentence]
**Architecture:** [2-3 sentences]
**Tech Stack:** [Key technologies]

---
### Task N: [Descriptive Name]
**Objective:** [One sentence]
**Files:**
- Create: `exact/path/to/new_file.py`
- Modify: `exact/path/to/existing.py:45-67`
- Test: `tests/path/to/test_file.py`

**Step 1: Write failing test**
```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify failure**
Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: FAIL — "function not defined"

**Step 3: Write minimal implementation**
```python
def function(input):
    return expected
```

**Step 4: Run test to verify pass**
Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: PASS

**Step 5: Commit**
```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```

**Task granularity**: Each task = 2-5 minutes (one TDD cycle). NOT "build auth system" (50 lines, 5 files). YES: "create User model with email", "add password hash field", "create password hash utility".

**Principles**: User-first (who benefits? user, not system learning); no stubs (real working code with real data); DRY (extract shared logic); YAGNI (only what's needed now); TDD (every task includes test cycle); frequent commits.

**Execution handoff**: "Plan complete and saved. Ready to execute using subagent-driven-development — I'll dispatch a fresh subagent per task with two-stage review. Shall I proceed?"

## Verification
- No test scripts in skill directory
- No evals/ directory
- Verify by loading skill and checking SKILL.md loads correctly

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| (none) | No references/, templates/, or scripts/ directories in this skill |