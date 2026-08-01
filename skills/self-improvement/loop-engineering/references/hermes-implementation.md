# Hermes Loop Engineering Implementation

## Session: 2026-07-05 — Full Loop Engineering Integration

This document captures the concrete implementation of Loop Engineering in Hermes from the July 5, 2026 session.

## Files Created/Modified

| File | Purpose | Status |
|------|---------|--------|
| `scripts/validate-fix.sh` | Deterministic validation (PASS/FAIL) | ✅ Created |
| `.omp/AGENTS.md` | Project conventions for all agents | ✅ Updated |
| `.omp/agents/maker.md` | Maker subagent definition | ✅ Created |
| `.omp/agents/checker.md` | Checker subagent definition | ✅ Created |
| `state/loop-state.md` | Orchestrator persistent state | ✅ Created |
| `scripts/finance_core.py` | Finance tracking for validation | ✅ Enhanced |
| `scripts/autonomous_agent.py` | Orchestrator with finance integration | ✅ Enhanced |
| `ARBITRAGE_WORKSHOP.md` | Scheme catalog with ЦА templates | ✅ Updated |
| `ARBITRAGE_LOG.md` | Test journal for schemes | ✅ Created |

## Key Implementation Details

### validate-fix.sh — Windows Compatible
- Uses Python for math instead of `bc` (missing on Windows)
- Runs from HERMES_HOME via `cwd='D:/Portable_Soft/hermes'`
- Queries finance_core.py for real metrics
- Outputs only PASS/FAIL + metrics

### Finance Integration in Orchestrator
```python
# In collect_system_state()
from scripts.finance_core import get_finance_summary
state["finance"] = get_finance_summary()
```

Finance-aware PRODUCE actions generated in `evaluate_actions()`:
- `produce-scale-<scheme>` — ROI > 100%
- `produce-kill-<scheme>` — ROI < 0 after spend > $10
- `produce-deploy-new-scheme` — net > -$500, tax < $100
- `produce-confirm-withdrawals` — pending withdrawals exist
- `produce-pay-taxes` — tax pending > $50

### Worktree Pattern (Ready for Production)
```python
# Orchestrator creates worktree
subprocess.run(["git", "worktree", "add", f"../hermes-wt-{task_id}/", branch])

# Maker works in ../hermes-wt-<task-id>/
# Checker validates there
# After: cleanup worktree + branch
```

### State Persistence
`state/loop-state.md` updated after each cycle with:
- Current task + phase
- Maker result (truncated)
- Checker result (full output)
- Orchestrator decision
- Next scheduled run

### Validation Script Tests
```bash
# Manual test from HERMES_HOME
bash scripts/validate-fix.sh Content-Locking-CPA
# Output: PASS with Revenue: $235.0, Withdrawals: 2, Tax: $9.4
```

## Integration Points

| Component | Calls | Data Flow |
|-----------|-------|-----------|
| `autonomous_agent.py` → `finance_core.py` | `get_finance_summary()` | state["finance"] |
| `evaluate_actions()` | reads state["finance"] | generates finance actions |
| `validate-fix.sh` → `finance_core.py` | `get_scheme_economics()`, `get_pending_withdrawals()`, `get_tax_liability()` | real metrics for PASS/FAIL |
| Maker → Checker | via worktree + validate-fix.sh | PASS/FAIL only |

## Lessons Learned (This Session)

1. **Windows `bc` missing** — Use Python for math: `python -c "import sys; sys.exit(0 if float(x) >= 1 else 1)"`
2. **Subprocess cwd critical** — `validate-fix.sh` must run from HERMES_HOME for relative paths
3. **Finance integration is the verification backbone** — Without finance_core queries, validate-fix.sh is just syntax checking
4. **Worktree isolation ready but not yet wired** — `autonomous_agent.py` doesn't yet create worktrees; that's the next wiring step
5. **State file is the only memory** — Orchestrator has no other memory between cycles

## Next Wiring Steps (Priority Order)

1. **Wire worktree creation** in `autonomous_agent.py` before Maker spawn
2. **Wire Maker/Checker subagents** via `delegate_task` with maker.md/checker.md prompts
3. **Add cost/token tracking** to prevent runaway API costs
4. **Add HITL gates** for irreversible actions (CPA registration, withdrawal requests)
5. **Containerize** with Docker + uv for reproducible deployment