# Project Conventions for Loop Engineering Agents

## Project Root
D:/Portable_Soft/hermes

## Package Manager
Python (pip/uv). All package operations use `pip install` or `uv pip install`.

## Test Command
```bash
python -m pytest tests/ -v --tb=short
```

## Lint/Typecheck Command
```bash
python -m ruff check scripts/
python -m mypy scripts/ --ignore-missing-imports
```

## Branch Naming
`fix/<issue-number>` — e.g. `fix/43` for GitHub issue #43
`feature/<scheme-name>` — e.g. `feature/content-locking-cpa`

## PR Title Format
`[<issue-number>] <issue title>` — e.g. `[43] Fix add() returning subtraction result`

## State File Location
`state/loop-state.md`

## Validation Script
`scripts/validate-fix.sh` — the checker runs this to determine PASS/FAIL.

### What validate-fix.sh tests:
1. **Revenue recorded** — scheme has at least $1 revenue in finance_core
2. **Withdrawal confirmed** — at least 1 withdrawal_received event with status=confirmed
3. **Tax liability manageable** — pending tax <= $500
4. **Scheme-specific checks** — additional per-scheme validation

**Output:** PASS or FAIL. No third option.

---

## Maker Requirements

Before reporting completion, the maker MUST run both:
1. `python scripts/autonomous_agent.py --dry` (if tests exist for the task)
2. `bash scripts/validate-fix.sh <scheme_name>`

Report the results of both commands verbatim.

### Maker Workflow:
1.ow:
1. Change to the worktree's project directory
2. Read the issue/scheme description
3. Implement the fix/deployment
3. Run `python scripts/autonomous_agent.py --dry` (if applicable)
4. Run `scripts/validate-fix.sh <scheme_name>`
5. Report what you changed, the test results, and which validation rules your fix satisfies.

**Do NOT:**
- Create a PR
- Update state/loop-state.md
- Merge branches
- Push to origin

---

## Checker Rules

The checker MUST NOT invent rules beyond those in `scripts/validate-fix.sh`.

Run the script and report its output verbatim.

### Checker Workflow:
1. Change to the worktree's project directory
2. Run `scripts/validate-fix.sh <scheme_name>`
3. Report the output verbatim (PASS/FAIL + details)

**Do NOT:**
- Create a PR
- Modify code
- Run tests beyond validate-fix.sh
- Interpret results beyond PASS/FAIL

---

## Orchestrator Conventions

### Loop Cycle (every 15 min via cron):
1. **Read** state/loop-state.md
2. **Select** next action based on phase
3. **Execute** via subagents (maker/checker)
4. **Update** state/loop-state.md with results
5. **Decide**: PR / Kill / Retry

### Phase Transitions:
```
ORCHESTRATOR_PLAN → MAKER_DEPLOY → CHECKER_VALIDATE → ORCHESTRATOR_DECIDE
                                    ↓ FAIL
                              KILL_SCHEME → LOG_LESSON
```

### State File Updates:
- Append to Phase History table
- Update Maker Result / Checker Result sections
- Record Orchestrator Decision
- Update Scheme Metrics from finance_core

---

## Subagent Definitions

### Maker (loop-maker)
**Purpose:** Implements a GitHub issue / deploys an arbitrage scheme.

**Input:**
- Issue key / Scheme name
- Issue summary / Scheme description
- Acceptance criteria / ЦА template
- Worktree path: `../hermes-wt-<task-id>/`

**Tools:** Full code access, terminal, web_search, delegate_task

### Checker (loop-checker)
**Purpose:** Independent validation of maker's work.

**Input:**
- Scheme name / Issue key
- Worktree path: `../hermes-wt-<task-id>/`

**Tools:** Terminal only (run validate-fix.sh)

---

## Worktree Management

```bash
# Create worktree for task
git worktree add ../hermes-wt-<task-id>/ <branch-name>

# Cleanup after completion
git worktree remove ../hermes-wt-<task-id>/
git branch -D <branch-name>
```

---

## Demo Mode (for testing without GitHub credentials)

```bash
DEMO_MODE=true ./scripts/loop-demo.sh
```

- Tasks from `fixtures/demo-issues.json`
- State written to `state/loop-state.md`
- **No network calls**

---

## Production Mode (requires GitHub PAT)

```bash
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx ./scripts/loop-demo.sh
```

- Finds open issues with label `loop-demo`
- Processes **one per run**
- Creates PR and closes issue

---

## File Structure Reference

```
.omp/
├── AGENTS.md              # This file
├── mcp.json               # MCP server: GitHub (issues + PR)
├── mcp.json.template      # Template for token substitution
├── agents/
│   ├── maker.md           # Maker subagent definition
│   └── checker.md         # Checker subagent definition
└── skills/loop-demo/
    └── SKILL.md           # Orchestrator logic + shared conventions

scripts/
├── loop-demo.sh           # Entry point (env, checks, runs omp)
├── validate-fix.sh        # Deterministic validation (PASS/FAIL)
└── validate-fix-<scheme>.sh  # Scheme-specific validators

state/
└── loop-state.md          # Orchestrator memory

fixtures/
└── demo-issues.json       # Demo mode tasks
```

---

## Quick Reference: Commands

| Action | Command |
|--------|---------|
| Run tests | `python -m pytest tests/ -v` |
| Validate fix | `./scripts/validate-fix.sh <scheme>` |
| Lint | `ruff check scripts/` |
| Typecheck | `mypy scripts/` |
| Create worktree | `git worktree add ../wt-name branch` |
| Remove worktree | `git worktree remove ../wt-name && git branch -D branch` |
| View state | `cat state/loop-state.md` |
| Finance summary | `python scripts/finance_core.py summary` |