---
name: loop-engineering
description: "Deterministic validation loop for autonomous agents: Orchestrator → Maker (isolated worktree) → Checker (validate-fix.sh) → PASS/FAIL. Eliminates LLM hallucination in verification. Based on Loop Engineering pattern (Addy Osmani)."
version: 1.1.0
author: Hermes
metadata:
  hermes:
    tags: [loop-engineering, deterministic-validation, maker-checker, autonomous-agent, orchestrator]
    trigger: event (new task requiring validation) | manual
---

# Loop Engineering — Deterministic Validation for Autonomous Agents

## Core Principle

**LLM cannot reliably verify its own work.** Separate the *doer* (Maker) from the *verifier* (Checker) and force the verifier to run a deterministic script that outputs only PASS/FAIL.

> "Третьего не дано: проверка либо пройдена (PASS), либо нет (FAIL)."

## Architecture

```
Orchestrator (Hermes)
    │
    ├─► Create Git worktree for task isolation
    │
    ├─► Maker Subagent (hermes-maker)
    │     • Receives: task, scheme details, worktree path
    │     • Implements: code, content, deployment
    │     • MUST run before reporting:
    │         python scripts/autonomous_agent.py --dry
    │         bash scripts/validate-fix.sh <scheme_name>
    │     • Reports: changes, test results, validation output
    │
    ├─► Checker Subagent (hermes-checker)
    │     • NEVER sees Maker's work directly
    │     • Runs ONLY: bash scripts/validate-fix.sh <scheme_name>
    │     • Reports output VERBATIM: PASS or FAIL with details
    │
    └─► Orchestrator Decision
          • PASS → Create PR, close issue, update state, delete worktree
          • FAIL → Log reason, delete worktree/branch, NO PR
```

## Key Components

### 1. Validation Script (`scripts/validate-fix.sh`)

Deterministic, zero-LLM verification. For arbitrage schemes checks:
- Scheme exists in Workshop with ЦА template
- ЦА template filled (all 4 sections)
- Tracked in finance_core.db
- Revenue recorded (≥ $1)
- ≥1 confirmed withdrawal (withdrawal_received, status=confirmed)
- Tax liability manageable (< $500)
- No critical errors in logs

**Output:** Only `PASS` or `FAIL` with metrics. No interpretation.

**Windows-compatible:** Uses Python for math instead of `bc`:
```bash
# Instead of: if (( $(echo "$REVENUE < 1" | bc -l) )); then
if python -c "import sys; sys.exit(0 if float('$REVENUE') >= 1 else 1)" 2>/dev/null; then
    : # OK
else
    echo "FAIL: No revenue recorded"
    exit 1
fi
```

### 2. Project Conventions (`.omp/AGENTS.md`)

Single source of truth for all agents:
- Test commands, build commands
- Branch naming, PR format
- State file locations
- Validation script references
- Maker/Checker requirements
- Arbitrage-specific rules (ЦА template, withdrawal verified)

### 3. Maker Definition (`.omp/agents/maker.md`)

- Works in isolated worktree
- Receives task + scheme details
- Implements task
- **MANDATORY** runs both validations before reporting
- Reports verbatim validation output

### 4. Checker Definition (`.omp/agents/checker.md`)

- **NEVER sees Maker's work**
- Runs ONLY `validate-fix.sh`
- Reports output VERBATIM
- No interpretation, no invented rules

### 5. Orchestrator State (`state/loop-state.md`)

Persistent memory between cycles:
```
## Current Task: #1 Fix add() returning subtraction
## Phase: CHECKER_VALIDATION
## Maker Result: npm test PASS, npm run build PASS
## Checker Result: PASS
## Next: Create PR
```

## Worktree Isolation

Each task gets its own Git worktree:
```bash
git worktree add ../hermes-wt-<task-id>/ <branch>
# Maker works here
# Checker validates here
# After: worktree deleted, branch deleted
```
Enables true parallelism without conflicts.

## Integration with Autonomous Agent

In `collect_system_state()`:
```python
from scripts.finance_core import get_finance_summary
state["finance"] = get_finance_summary()
```

In `evaluate_actions()` — Finance-aware PRODUCE actions:
- Scale profitable schemes (ROI > 100%)
- Kill unprofitable (ROI < 0 after $0 spend >$10)
- Deploy new from Workshop if cash allows
- Confirm pending withdrawals
- Pay accrued taxes

## Anti-Patterns Prevented

| Anti-Pattern | How Loop Engineering Fixes |
|--------------|---------------------------|
| LLM self-verification | Checker never sees Maker's work; runs deterministic script only |
| "Looks good to me" | validate-fix.sh outputs only PASS/FAIL with metrics |
| Truncated execution | Orchestrator only accepts PASS → PR; FAIL → kill worktree |
| Permission waiting | Maker executes if $0 budget + withdrawal verified |
| Incomplete verification | validate-fix.sh checks ALL gates (ЦА, finance, withdrawal, tax, logs) |

## Usage

### For New Arbitrage Scheme
1. Add scheme to `ARBITRAGE_WORKSHOP.md` with ЦА template
2. Deploy via autonomous agent → creates worktree → Maker deploys
3. Checker runs `validate-fix.sh <scheme_name>`
4. PASS → log to `ARBITRAGE_LOG.md` with ROI/withdrawal proof

### For Code Tasks
1. Issue created with acceptance criteria
2. Orchestrator creates worktree → Maker implements
3. Maker runs tests + build
4. Checker runs `validate-fix.sh` (or custom script)
5. PASS → PR created automatically

## Support Files

| File | Purpose |
|------|---------|
| `scripts/validate-fix.sh` | Deterministic validation (PASS/FAIL) |
| `.omp/AGENTS.md` | Project conventions for all agents |
| `.omp/agents/maker.md` | Maker subagent definition |
| `.omp/agents/checker.md` | Checker subagent definition |
| `state/loop-state.md` | Orchestrator persistent state |
| `references/cost-tracking-hitl.md` | Cost tracking + HITL gates integration details |

## Templates

- `templates/AGENTS.md` — Project conventions template
- `templates/maker.md` — Maker subagent definition template
- `templates/checker.md` — Checker subagent definition template
- `templates/validate-fix.sh` — Validation script template
- `templates/loop-state.md` — State file template

## Scripts

- `scripts/validate-fix.sh` — Deterministic validation (PASS/FAIL)
- `scripts/loop-demo.sh` — Orchestrator entry point

## Pitfalls & Hard Lessons (Updated from Session 2026-07-05)

1. **Never let Maker create PR** — Orchestrator owns the merge decision
2. **Never let Checker invent rules** — Only what's in validate-fix.sh
3. **Never skip validation** — Even "obvious" fixes need PASS
4. **Never share worktree** — Isolation = parallelism = no conflicts
5. **State file is mandatory** — Without it, orchestrator has amnesia
6. **Windows `bc` missing** → Use Python for math comparisons
7. **Subprocess cwd matters** — `validate-fix.sh` must run from HERMES_HOME
8. **Finance integration critical** — validate-fix.sh MUST query finance_core for real metrics
9. **Cost tracking mandatory at cycle start** — check_daily_limit() before any LLM action
10. **HITL gates for irreversible actions** — withdrawal, CPA registration, tax payment require user confirmation
11. **Structured JSON logging** — log_json() with trace_id for observability
12. **Docker only on VPS** — local dev uses uv venv only

---

### Session 2026-07-05 Integration Learnings

#### Cost Tracking + HITL Gates Integration
- **Cost check at start of every cycle**: `check_daily_limit()` logs daily usage %, blocks if exceeded
- **Cost fields in decision log**: `daily_cost_usd`, `daily_limit_usd`, `cost_limit_exceeded`
- **HITL gates on finance actions**: `WITHDRAWAL_CONFIRM`, `CPA_REGISTRATION`, `TAX_PAYMENT`, `SCHEME_KILL`, `SCALE_BUDGET`, `NEW_SCHEME_DEPLOY`
- **HITL persists to JSON**: 24h TTL, approve/reject via CLI

#### Token Compression Integration
- **auto_compress() in call_llm()**: Compresses messages before sending to LLM
- **40-75% savings** on tool outputs
- **Integrated in**: `llm_analyst.py` (analyze_batch + call_llm) and `autonomous_agent.py` (imported)

#### Structured Logging / Observability
- **Trace/span IDs via contextvars**: `trace_id_var`, `span_id_var`
- **New trace per agent run**: `new_trace_id()` at start of main()
- **JSON log entries**: timestamp, level, trace_id, span_id, message, kwargs
- **Human-readable + machine-parseable**: Both stdout and file

#### LLM Provider: localhost:9655 (DeepSeek-V4-Flash)
- **Free, no auth**: Runs locally, no API key needed
- **Models**: `deepseek-chat`, `deepseek-reasoner`, `deepseek-chat-search`, etc.
- **Rate limit**: ~1 req/3-5 sec, back off 30s on 429/5xx
- **Cost**: ~$0.14/1M in, $0.28/1M out (very cheap)
- **Access**: `curl` / `urllib` directly from execute_code (no delegate_task)

#### Windows Compatibility
- **validate-fix.sh uses Python** for math (bc not on Windows)
- **Subprocess cwd = HERMES_HOME** required for relative paths
- **uv for deps** (no Docker locally)

## Related Skills

- `white-spot-explorer` — Feeds domains for exploration (uses same deterministic approach)
- `arbitrage-execution` — Uses validate-fix.sh as verification gate
- `finance-core` — Provides scheme economics for validation
- `autonomous-system-operations` — Orchestrator runs the loop