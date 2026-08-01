---
name: subagent-driven-development
description: "Execute plans via delegate_task subagents (2-stage review)."
version: 1.3.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [delegation, subagent, implementation, workflow, parallel]
    related_skills: [writing-plans, requesting-code-review, test-driven-development]
---

# Subagent-Driven Development

## Overview

Execute implementation plans by dispatching fresh subagents per task with systematic two-stage review.

**Core principle:** Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration.

## When to Use

Use this skill when:
- You have an implementation plan (from writing-plans skill or user requirements)
- Tasks are mostly independent
- Quality and spec compliance are important
- You want automated review between tasks

**vs. manual execution:**
- Fresh context per task (no confusion from accumulated state)
- Automated review process catches issues early
- Consistent quality checks across all tasks
- Subagents can ask questions before starting work

## The Process

### 1. Read and Parse Plan

Read the plan file. Extract ALL tasks with their full text and context upfront. Create a todo list:

```python
# Read the plan
read_file("docs/plans/feature-plan.md")

# Create todo list with all tasks
todo([
    {"id": "task-1", "content": "Create User model with email field", "status": "pending"},
    {"id": "task-2", "content": "Add password hashing utility", "status": "pending"},
    {"id": "task-3", "content": "Create login endpoint", "status": "pending"},
])
```

**Key:** Read the plan ONCE. Extract everything. Don't make subagents read the plan file — provide the full task text directly in context.

### 2. Per-Task Workflow

For EACH task in the plan:

#### Step 1: Dispatch Implementer Subagent

Use `delegate_task` with complete context:

```python
delegate_task(
    goal="Implement Task 1: Create User model with email and password_hash fields",
    context="""
    TASK FROM PLAN:
    - Create: src/models/user.py
    - Add User class with email (str) and password_hash (str) fields
    - Use bcrypt for password hashing
    - Include __repr__ for debugging

    FOLLOW TDD:
    1. Write failing test in tests/models/test_user.py
    2. Run: pytest tests/models/test_user.py -v (verify FAIL)
    3. Write minimal implementation
    4. Run: pytest tests/models/test_user.py -v (verify PASS)
    5. Run: pytest tests/ -q (verify no regressions)
    6. Commit: git add -A && git commit -m "feat: add User model with password hashing"

    PROJECT CONTEXT:
    - Python 3.11, Flask app in src/app.py
    - Existing models in src/models/
    - Tests use pytest, run from project root
    - bcrypt already in requirements.txt
    """,
    toolsets=['terminal', 'file']
)
```

#### Step 2: Dispatch Spec Compliance Reviewer

After the implementer completes, verify against the original spec:

```python
delegate_task(
    goal="Review if implementation matches the spec from the plan",
    context="""
    ORIGINAL TASK SPEC:
    - Create src/models/user.py with User class
    - Fields: email (str), password_hash (str)
    - Use bcrypt for password hashing
    - Include __repr__

    CHECK:
    - [ ] All requirements from spec implemented?
    - [ ] File paths match spec?
    - [ ] Function signatures match spec?
    - [ ] Behavior matches expected?
    - [ ] Nothing extra added (no scope creep)?

    OUTPUT: PASS or list of specific spec gaps to fix.
    """,
    toolsets=['file']
)
```

**If spec issues found:** Fix gaps, then re-run spec review. Continue only when spec-compliant.

#### Step 3: Dispatch Code Quality Reviewer

After spec compliance passes:

```python
delegate_task(
    goal="Review code quality for Task 1 implementation",
    context="""
    FILES TO REVIEW:
    - src/models/user.py
    - tests/models/test_user.py

    CHECK:
    - [ ] Follows project conventions and style?
    - [ ] Proper error handling?
    - [ ] Clear variable/function names?
    - [ ] Adequate test coverage?
    - [ ] No obvious bugs or missed edge cases?
    - [ ] No security issues?

    OUTPUT FORMAT:
    - Critical Issues: [must fix before proceeding]
    - Important Issues: [should fix]
    - Minor Issues: [optional]
    - Verdict: APPROVED or REQUEST_CHANGES
    """,
    toolsets=['file']
)
```

**If quality issues found:** Fix issues, re-review. Continue only when approved.

#### Step 4: Mark Complete

```python
todo([{"id": "task-1", "content": "Create User model with email field", "status": "completed"}], merge=True)
```

### 3. Final Review

After ALL tasks are complete, dispatch a final integration reviewer:

```python
delegate_task(
    goal="Review the entire implementation for consistency and integration issues",
    context="""
    All tasks from the plan are complete. Review the full implementation:
    - Do all components work together?
    - Any inconsistencies between tasks?
    - All tests passing?
    - Ready for merge?
    """,
    toolsets=['terminal', 'file']
)
```

### 4. Verify and Commit

```bash
# Run full test suite
pytest tests/ -q

# Review all changes
git diff --stat

# Final commit if needed
git add -A && git commit -m "feat: complete [feature name] implementation"
```

## Task Granularity (Tracer Bullet)

**Tracer Bullet principle: 1 task ≤ 1 context window.** If a task won't fit in one agent context, split it.

**Each task = 2-5 minutes of focused work.**

**Too big:**
- "Implement user authentication system"

**Right size:**
- "Create User model with email and password fields"
- "Add password hashing function"
- "Create login endpoint"
- "Add JWT token generation"
- "Create registration endpoint"

## DELEGATION IS MANDATORY — THE #1 WORKFLOW RULE

**Core principle: Answer as expert, delegate coding. Never switch to manual coding yourself.**

The user wants an expert/coordinator, not a typist. When they ask a question → answer clearly.
When code needs writing → dispatch a subagent. Any non-trivial coding is delegated.

**This is the #1 user frustration.** Doing code work yourself instead of delegating will make the user angry.

### When to Code DIRECTLY (rare — only these):
- Single-line file edit (patch for var name, typo, formatting)
- Quick terminal command to check state
- Reading/inspecting files
- Short `execute_code` for a single API call, DB write, or one-file create

### DELEGATE EVERYTHING ELSE:
- Creating new files or modules
- Multi-line edits or refactoring
- Running tests and fixing failures
- Any multi-file implementation
- Data processing, classification, batch operations
- Anything that would take 3+ tool calls

### When NOT to delegate (use execute_code instead):
- **Simple API calls** (к LLM прокси, HTTP к внешним сервисам) — delegate_task блокирует чат на минуты. Используйте execute_code с промежуточной отпиской.
- **Запись в БД/Knowledge Cube** — быстрее через прямой Python в execute_code

### After Delegation

**Surface the result immediately.** Don't let the user ask "а что там?" — proactively report: what was created, what passed, what failed.

## Red Flags — Never Do These

- Start implementation without a plan
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed critical/important issues
- Dispatch multiple implementation subagents for tasks that touch the same files
- Make subagent read the plan file (provide full text in context instead)
- Skip scene-setting context (subagent needs to understand where the task fits)
- Ignore subagent questions (answer before letting them proceed)
- Accept "close enough" on spec compliance
- Skip review loops (reviewer found issues → implementer fixes → review again)
- Let implementer self-review replace actual review (both are needed)
- **Start code quality review before spec compliance is PASS** (wrong order)
- Move to next task while either review has open issues
- **Use delegate_task for simple tasks** — delegate_task БЛОКИРУЕТ родительскую сессию. Пользователь видит тишину на 7+ минут. Для простого (API-вызовы, запись в БД, 1-2 файла) используйте execute_code с промежуточными статусами. delegate_task оправдан только для изолированных контекстов (кодинг, отладка, многомодульный анализ).
- **Delegate batch file creation (3+ files)** — subagents create dirs but skip files. Use execute_code + write_file instead. User愤怒 when you fall back to manual coding instead of fixing tool choice.

## Handling Issues

### Free Model Subagent Interruptions (2026-06-08 Finding)

Subagents running on free models (opencode-zen: mimo-v2.5-free, deepseek-v4-flash-free) **frequently get interrupted** before completion. This is a known limitation of free tier providers.

**Root cause (2026-06-28):** Free model inference takes 35-50 seconds per API call. A subagent making 12-17 tool calls = 420-850 seconds total. The 600s timeout is not enough.

**Evidence from logs:**
```
model=mimo-v2.5-free provider=opencode-zen
Subagent 0 timed out after 603.2s (14 API calls)
Subagent 1 timed out after 603.3s (17 API calls)
```
14 calls × 43s average = 602s → timeout.

**Symptoms:**
- Subagent returns status="interrupted" or "timeout" mid-task
- Partial work completed but summary missing
- Task appears to "hang" then fail

**Mitigation strategies:**
1. **Break large tasks into smaller subtasks** — smaller tasks complete before interruption
2. **Check partial results** — interrupted subagents may have created files; inspect before re-dispatching
3. **Retry with simpler context** — shorter context = faster completion = less chance of interruption
4. **Use batch mode** — `delegate_task(tasks=[...])` runs 3 concurrent subagents; even if one interrupts, others may complete
5. **Accept partial progress** — an interrupted subagent that created 2 of 3 files is better than nothing; finish the 3rd file yourself
6. **For file creation: use execute_code** — 60s for 5 sites vs 600s+ timeout for subagents

**When delegating to free model subagents:**
- Keep goal text under 500 words
- Include ONLY essential context (paths, constraints)
- Don't ask subagents to do research + implementation; split into separate subagents
- Prefer `terminal` + `file` toolsets (lighter than `web` + `terminal` + `file`)
- **1 subagent = 1 file = 1-2 API calls = ~70s** (fits within timeout)

### If Subagent Asks Questions

- Answer clearly and completely
- Provide additional context if needed
- Don't rush them into implementation

### If Reviewer Finds Issues

- Implementer subagent (or a new one) fixes them
- Reviewer reviews again
- Repeat until approved
- Don't skip the re-review

### Batch File Creation Failure (2026-06-28 Finding)

**Subagents reliably fail at batch file creation.** Pattern: subagent creates directories but skips files, or only creates 1-2 of N files. This is a known failure mode, not a one-off.

**Root cause:** Subagents on free models get interrupted mid-task, or lose context about which files they've already created. The directory creation (mkdir) succeeds because it's one call; file creation (write_file × N) fails because it's multiple sequential calls that get interrupted.

**User correction:** "почему Субагент не создал файлы!!! а ты полез кодить!!!!" — user is angry when you fall back to manual coding instead of fixing the tool choice.

**Fix:** Use `execute_code` with `write_file` to batch-create all files in one atomic operation:

```python
from hermes_tools import write_file
# Create all files in one script — no race condition, no interruption
write_file("demos/salon/index.html", "...")
write_file("demos/salon/css/style.css", "...")
write_file("demos/salon/js/main.js", "...")
```

**Rule:** When creating 3+ files with shared structure (templates, scaffolding, multi-file projects), ALWAYS use `execute_code` + `write_file`. NEVER delegate batch file creation to subagents.

**If subagent already created partial files:** Don't re-delegate. Check what exists with `search_files`, then use `execute_code` to create the missing files.

### Sibling Subagent Race Condition (2026-06-28 Finding)

**When two subagents write to the same file path, one overwrites the other silently.** The write_file tool warns about sibling modification but still overwrites.

**Evidence:** deleg_0243be38 was creating funeral/index.html. sa-0-fe701f62 also wrote to funeral/index.html. The warning appeared: "D:\...\funeral\index.html was modified by sibling subagent 'sa-0-fe701f62' but this agent never read it."

**Root cause:** When dispatching multiple subagents for the same task (re-dispatching after failure), the old subagent may still be running. Both try to create the same files.

**Fix:**
1. Don't re-dispatch subagents for the same task until you've confirmed the first one is dead
2. Before re-dispatching, check `process(action='list')` and `search_files` to see what exists
3. If partial files exist, use `execute_code` to create only the missing ones
4. If you must re-dispatch, kill the old process first

**Rule:** Before re-dispatching a failed subagent, CHECK if it's still running and what files it already created. Don't create overlapping subagents.

### If Subagent Fails a Task

- Dispatch a new fix subagent with specific instructions about what went wrong
- Don't try to fix manually in the controller session (context pollution)
- **EXCEPTION: batch file creation** — see "Batch File Creation Failure" above. For file-heavy tasks, fix it yourself with execute_code, not another subagent.

### Subagent Timeout on Complex Tasks (2026-06-30)

**Rule:** When subagents consistently timeout at 600s on complex tasks, break them into smaller atomic tasks.

**What happened:** 6+ subagents timed out on chain audits, script mapping, and self-evolving tasks. Each was trying to read 5+ files, check imports, analyze code, and write reports — too much for 600s with free models (43s per API call).

**Atomic task sizing:**
- 1 subagent = 1-3 files = 1-2 API calls = ~70s (fits timeout)
- If task needs >5 file reads → split into multiple subagents
- If task needs research + implementation → split into 2 subagents

**Fallback when subagents timeout:**
1. Switch to `execute_code` with `terminal()` + `read_file()` for mechanical parts
2. Dispatch subagent only for analysis/reasoning
3. Check partial results — interrupted subagents may have created files

## Efficiency Notes

**Why fresh subagent per task:**
- Prevents context pollution from accumulated state
- Each subagent gets clean, focused context
- No confusion from prior tasks' code or reasoning

**Why two-stage review:**
- Spec review catches under/over-building early
- Quality review ensures the implementation is well-built
- Catches issues before they compound across tasks

**Cost trade-off:**
- More subagent invocations (implementer + 2 reviewers per task)
- But catches issues early (cheaper than debugging compounded problems later)

## Integration with Other Skills

### With writing-plans

This skill EXECUTES plans created by the writing-plans skill:
1. User requirements → writing-plans → implementation plan
2. Implementation plan → subagent-driven-development → working code

### With test-driven-development

Implementer subagents should follow TDD:
1. Write failing test first
2. Implement minimal code
3. Verify test passes
4. Commit

Include TDD instructions in every implementer context.

### With requesting-code-review

The two-stage review process IS the code review. For final integration review, use the requesting-code-review skill's review dimensions.

### With systematic-debugging

If a subagent encounters bugs during implementation:
1. Follow systematic-debugging process
2. Find root cause before fixing
3. Write regression test
4. Resume implementation

## Example Workflow

```
[Read plan: docs/plans/auth-feature.md]
[Create todo list with 5 tasks]

--- Task 1: Create User model ---
[Dispatch implementer subagent]
  Implementer: "Should email be unique?"
  You: "Yes, email must be unique"
  Implementer: Implemented, 3/3 tests passing, committed.

[Dispatch spec reviewer]
  Spec reviewer: ✅ PASS — all requirements met

[Dispatch quality reviewer]
  Quality reviewer: ✅ APPROVED — clean code, good tests

[Mark Task 1 complete]

--- Task 2: Password hashing ---
[Dispatch implementer subagent]
  Implementer: No questions, implemented, 5/5 tests passing.

[Dispatch spec reviewer]
  Spec reviewer: ❌ Missing: password strength validation (spec says "min 8 chars")

[Implementer fixes]
  Implementer: Added validation, 7/7 tests passing.

[Dispatch spec reviewer again]
  Spec reviewer: ✅ PASS

[Dispatch quality reviewer]
  Quality reviewer: Important: Magic number 8, extract to constant
  Implementer: Extracted MIN_PASSWORD_LENGTH constant
  Quality reviewer: ✅ APPROVED

[Mark Task 2 complete]

... (continue for all tasks)

[After all tasks: dispatch final integration reviewer]
[Run full test suite: all passing]
[Done!]
```

## Monitoring & Debugging Subagents

### ⚠️ ВАЖНО: delegate_task блокирует родительскую сессию

Пока работает delegate_task, **вы не можете отвечать пользователю.** 
Пользователь видит только спиннер и тишину — это раздражает.

**Правило:** если задача займёт >30 секунд — не используйте delegate_task для неё.
Вместо этого:
1. Разбейте на маленькие шаги
2. Каждый шаг через execute_code с прямыми вызовами API
3. После каждого шага — print("статус") в stdout чтобы user видел прогресс
4. Финальный результат — краткий итог

**Исключение:** задача ДЕЙСТВИТЕЛЬНО требует изолированного контекста
(кодинг с тестами, многомодульная отладка, анализ с веб-поиском).
Тогда delegate_task оправдан — но предупредите пользователя: "запускаю агента, ~X минут".

When a delegate_task is running, the parent only sees a spinner by default. Here's how to get full visibility.

### Tool Progress Levels

The `display.tool_progress` setting in config.yaml (or `/verbose` command) controls what you see:

| Level | What it shows |
|-------|---------------|
| `off` | Silent — just the spinner and final response |
| `new` | Each new tool call (skips repeats of same tool) |
| `all` | Every tool call with emoji + name |
| `verbose` | Full args, results, and think blocks |

Cycle with `/verbose` in-session, or set permanently:
```bash
hermes config set display.tool_progress verbose
```

### What the Spinner Already Shows

During delegate_task, the CLI displays a tree-view ABOVE the spinner:
- `🔀 {goal}` — subagent start (goal truncated to 55 chars)
- `💭 "{thinking text}"` — when subagent is thinking
- `{emoji} {tool_name} "{preview}"` — each tool call in real-time

These are the child agent's tool calls relayed to the parent via the progress callback. On `verbose` level, full args and results are included.

### /agents Command

Type `/agents` during a running delegation to see:
- Active subagent IDs, goals, and status
- Which model each subagent uses
- Which toolsets are assigned
- Tool call count per subagent

This is the primary way to inspect what model and toolsets a running subagent has.

### What's NOT Shown by Default

- **Model used by subagent** — visible in `/agents` but not in tree-view
- **Skills loaded by subagent** — skills are loaded via system prompt, not tracked in progress events
- **System prompt content** — only goal and context are visible

If you need model/skill visibility during a run, check `/agents` or review the session after completion via `hermes sessions browse`.

### Gateway Display

On Telegram/Discord/Slack, delegation progress is batched (every 5 tool calls) and relayed as summary messages. The same tool_progress setting applies. Gateway shows `🔀 {goal}` at start, then batched tool-name lists.

## Remember

```
Fresh subagent per task
Two-stage review every time
Spec compliance FIRST
Code quality SECOND
Never skip reviews
Catch issues early
```

**Quality is not an accident. It's the result of systematic process.**

## Parallel Batch Pattern (load when relevant)

When tasks are **independent** (no shared files, no dependencies), run them in parallel via a single `delegate_task(tasks=[...])` call instead of sequential review. See `references/parallel-batch-pattern.md` for the full pattern, rules, and anti-patterns. Use this for migration, batch data processing, or multi-project setup — NOT for code implementation where review between tasks matters.

## Further reading (load when relevant)

When the orchestration involves significant context usage, long review loops, or complex validation checkpoints, load these references for the specific discipline:

- **`references/delegation-visibility.md`** — Config options, CLI commands, tree-view event types, identity kwargs, gateway behavior, and spinner details for monitoring running subagents. Load when you need to debug delegation display or configure verbosity.
- **`references/context-budget-discipline.md`** — Four-tier context degradation model (PEAK / GOOD / DEGRADING / POOR), read-depth rules that scale with context window size, and early warning signs of silent degradation. Load when a run will clearly consume significant context (multi-phase plans, many subagents, large artifacts).
- **`references/gates-taxonomy.md`** — The four canonical gate types (Pre-flight, Revision, Escalation, Abort) with behavior, recovery, and examples. Load when designing or reviewing any workflow that has validation checkpoints — use the vocabulary explicitly so each gate has defined entry, failure behavior, and resumption rules.
- **`references/windows-encoding-fixes.md`** — Windows Python encoding pitfalls: `ensure_ascii=True` for charmap, SQLite NOT NULL column mismatches. Load when debugging encoding errors or INSERT failures on Windows.

Both references adapted from gsd-build/get-shit-done (MIT © 2025 Lex Christopherson).
