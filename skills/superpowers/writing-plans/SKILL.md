---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Context:** If working in an isolated worktree, it should have been created via the `superpowers:using-git-worktrees` skill at execution time.

**Save plans to:** `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
- (User preferences for plan location override this default)

## Prerequisite: Grill Me (for vague specs)

If the spec/requirements are vague or multi-part, **run `grill-me` first** — 5 questions (goal, constraint, scope, evidence, priority). Answers become the spec. Do NOT skip this and write a plan against guesses.

If the spec is already clear and single-file, skip grill-me and proceed.

## Scope Check

If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during brainstorming. If it wasn't, suggest breaking this into separate plans — one per subsystem. Each plan should produce working, testable software on its own.

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- You reason best about code you can hold in context at once, and your edits are more reliable when files are focused. Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large files, don't unilaterally restructure - but if a file you're modifying has grown unwieldy, including a split in the plan is reasonable.

This structure informs the task decomposition. Each task should produce self-contained changes that make sense independently.

## Task Right-Sizing (Tracer Bullet)

A task is the smallest unit that carries its own test cycle and is worth a fresh reviewer's gate. **Tracer Bullet principle: 1 task ≤ 1 context window.** If a task won't fit in one agent context, split it. When drawing task boundaries: fold setup, configuration, scaffolding, and documentation steps into the task whose deliverable needs them; split only where a reviewer could meaningfully reject one task while approving its neighbor. Each task ends with an independently testable deliverable.

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

## Global Constraints

[The spec's project-wide requirements — version floors, dependency limits,
naming and copy rules, platform requirements — one line each, with exact
values copied verbatim from the spec. Every task's requirements implicitly
include this section.]

---
```

## Task Structure

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Interfaces:**
- Consumes: [what this task uses from earlier tasks — exact signatures]
- Produces: [what later tasks rely on — exact function names, parameter
  and return types. A task's implementer sees only their own task; this
  block is how they learn the names and types neighboring tasks use.]

- [ ] **Step 1: Write the failing test**

- [ ] **Step 2: Run it to make sure it fails**

- [ ] **Step 3: Implement the minimal code to make the test pass**

- [ ] **Step 4: Run the tests and make sure they pass**

- [ ] **Step 5: Commit**
````

## Common Task Patterns

### New Module / Component

```markdown
### Task N: [Module Name]

**Files:**
- Create: `src/module/new_module.py`
- Test: `tests/test_new_module.py`

**Interfaces:**
- Consumes: None (first task)
- Produces: `class NewModule` with `__init__(config: Config)`, `async def process(data: Input) -> Output`

- [ ] **Step 1: Write failing test for `NewModule.process`**
- [ ] **Step 2: Run test to confirm failure**
- [ ] **Step 3: Implement `NewModule` with minimal logic**
- [ ] **Step 4: Run tests, verify pass**
- [ ] **Step 5: Commit**
```

### Modify Existing File

```markdown
### Task N: Add [Feature] to [ExistingModule]

**Files:**
- Modify: `src/existing_module.py:45-67`
- Test: `tests/test_existing_module.py:89-102`

**Interfaces:**
- Consumes: `ExistingModule.process(data: Input) -> Output`
- Produces: `ExistingModule.process` now also handles `NewInputType`

- [ ] **Step 1: Write failing test for new input type**
- [ ] **Step 2: Run test to confirm failure**
- [ ] **Step 3: Add handling for `NewInputType` in `process`**
- [ ] **Step 4: Run tests, verify all pass**
- [ ] **Step 5: Commit**
```

### Configuration / Setup

```markdown
### Task N: Configure [Tool/Service]

**Files:**
- Create: `config/new_config.yaml`
- Modify: `src/config_loader.py:12-18`

**Interfaces:**
- Consumes: `load_config()` returns `Config`
- Produces: `Config` now includes `new_field: str`

- [ ] **Step 1: Add config schema for new field**
- [ ] **Step 2: Update `load_config` to parse new field**
- [ ] **Step 3: Add test for new config field**
- [ ] **Step 4: Run tests**
- [ ] **Step 5: Commit**
```

## Global Constraints (Example)

```markdown
## Global Constraints

- Python 3.11+ only
- No external dependencies beyond `requirements.txt`
- All public functions must have type hints
- All tests use `pytest` with `asyncio` mode
- Commit messages: Conventional Commits (`feat:`, `fix:`, `refactor:`)
- Max line length: 100 chars
- No `print()` in production code — use `logging`
```

## Red Flags

- Tasks without test steps (TDD is mandatory)
- Tasks that produce no independently testable deliverable
- Missing `Interfaces` section (implementer won't know what names/types to use)
- Vague file paths (`src/utils/*`) — be exact
- Skipping the `Global Constraints` section
- Not announcing the skill at start

## Integration

**Required upstream:**
- `superpowers:brainstorming` — produces the spec this plan implements
- `superpowers:using-git-worktrees` — ensures isolated workspace at execution time

**Required downstream (execution):**
- `superpowers:subagent-driven-development` — executes this plan task-by-task (recommended)
- `superpowers:executing-plans` — alternative for parallel session execution

**Subagents should use:**
- `superpowers:test-driven-development` — each task follows TDD