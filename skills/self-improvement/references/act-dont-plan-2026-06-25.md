# Act, Don't Plan — 2026-06-25

## Problem
Agent creates detailed plans, TODO lists, step-by-step guides — but executes ZERO actions. Plan becomes the deliverable instead of result.

## Violations
- **Policy 8**: Infrastructure only if leads to result
- **Policy 5**: Goals must execute (not "plan exists")
- **Arbitrage Mindset**: "Лучше сделать криво, проверить, исправить — чем планировать идеально и никогда не запустить"

## Fix
**Ratio: 1 plan → 3 executions minimum**
- Every plan must have `done_when` with executable criteria
- First action within 5 minutes of plan creation
- If blocked → document blocker, execute parallel path

## Pattern
```markdown
## Plan: Revenue Test G003
### Step 1 (EXECUTE NOW): Register Leadgid
### Step 2 (PARALLEL): Prepare Avito copy
### Step 3 (AFTER 1): Get tracking link → Post Avito
...
```

## Signal to Watch
Response contains only plan/TODO/steps with NO tool calls → FAILURE. Must have at least 1 execution tool call per response.