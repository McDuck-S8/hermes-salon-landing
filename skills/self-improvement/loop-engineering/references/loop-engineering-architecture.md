# Loop Engineering Architecture — Full Description

## Overview

Loop Engineering is the practice of designing systems where AI agents run continuously and autonomously, managed by an outer loop (Orchestrator) that coordinates inner loops (Maker → Checker).

## Core Loop

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR LOOP                         │
├─────────────────────────────────────────────────────────────┤
│  1. READ STATE (loop-state.md)                              │
│  2. SELECT NEXT ACTION (evaluate_actions)                   │
│  3. CREATE WORKTREE (git worktree add)                      │
│  4. SPAWN MAKER SUBAGENT                                     │
│  5. WAIT FOR MAKER RESULT                                    │
│  6. SPAWN CHECKER SUBAGENT                                   │
│  7. READ CHECKER OUTPUT (PASS/FAIL)                          │
│  8. DECIDE: PR / KILL / RETRY                                │
│  9. UPDATE STATE (loop-state.md)                             │
│ 10. CLEANUP WORKTREE                                         │
└─────────────────────────────────────────────────────────────┘
```

## Subagent Contracts

### Maker Contract
**Input:** Task ID, Scheme/Task description, Worktree path, Acceptance criteria
**Output:** Changes made, test results, validation output (verbatim)
**MUST run before reporting:**
1. `python scripts/autonomous_agent.py --dry` (dry-run verification)
2. `bash scripts/validate-fix.sh <scheme_name>` (deterministic validation)

### Checker Contract
**Input:** Task ID, Scheme name, Worktree path
**Output:** PASS/FAIL + metrics (verbatim from validate-fix.sh)
**MUST NOT:** Look at Maker's code, invent rules, interpret results

## Worktree Management

```bash
# Create
git worktree add ../hermes-wt-<task-id>/ <branch-name>

# Cleanup (after PASS or FAIL)
git worktree remove ../hermes-wt-<task-id>/
git branch -D <branch-name>
```

## State Persistence

`state/loop-state.md` — YAML-like markdown with:
- Current task ID
- Current phase
- Maker result (truncated)
- Checker result (full output)
- Orchestrator decision
- Next scheduled run
- Scheme metrics (from finance_core)

## Validation Script Contract

`scripts/validate-fix.sh <scheme_name>`
- Input: Scheme name
- Output: PASS/FAIL + metrics (Revenue, Withdrawals, Tax, etc.)
- Exit code: 0 = PASS, 1 = FAIL
- Deterministic: No LLM, no randomness
- Queries: finance_core.db, ARBITRAGE_WORKSHOP.md, logs

## Hermes-Specific Extensions

### Finance-Aware Validation
For arbitrage schemes, validate-fix.sh checks:
1. Scheme exists in ARBITRAGE_WORKSHOP.md with ЦА template
2. ЦА template has all 4 sections (Offer, Audience, Traffic, Math)
3. Scheme tracked in finance_core.db
3. Revenue ≥ $1 recorded
4. ≥ 1 confirmed withdrawal (status=confirmed)
4. Tax liability ≤ $500 pending
5. No critical errors in autonomous_agent.log

### Finance-Aware Orchestrator Actions
In `evaluate_actions()`, finance state generates:
- `produce-scale-<scheme>` — if ROI > 100% and status profitable
- `produce-kill-<scheme>` — if ROI < 0 after $10 spend
- `produce-deploy-new-scheme` — if cash OK and taxes manageable
- `produce-confirm-withdrawals` — if pending withdrawals exist
- `produce-pay-taxes` — if tax pending > $50

## Failure Modes & Handling

| Failure | Detection | Response |
|---------|-----------|----------|
| Maker timeout | Orchestrator watches | Kill worktree, log, retry once |
| Checker FAIL | validate-fix.sh exit 1 | Kill worktree, log lesson, no PR |
| Validator bug | PASS but broken | Add test case to validate-fix.sh |
| State corruption | Missing loop-state.md | Reconstruct from finance_core + logs |
| Worktree conflict | Git error | Force remove, recreate |

## Demo Mode

```bash
DEMO_MODE=true ./scripts/loop-demo.sh
```
- Uses `fixtures/demo-issues.json` instead of GitHub API
- No network calls
- Writes to `state/loop-state.md`
- Perfect for CI/testing

## Production Mode

```bash
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx ./scripts/loop-demo.sh
```
- Finds issues with label `loop-demo`
- Processes ONE per run
- Creates PR, closes issue
- Updates loop-state.md