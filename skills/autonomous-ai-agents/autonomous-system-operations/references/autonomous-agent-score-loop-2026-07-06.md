# Autonomous Agent Session Analysis — 2026-07-06

## Problem Observed: Score Inversion in Action Selection

The autonomous agent (autonomous_agent.py) ran in `--dry` mode and selected:
```
>>> SELECTED: [PRODUCE] Apply improvement suggestions (4 critical, 4 high)
     Score: 9.2 (urgency=12, impact=5)
```

**But the logged decision history shows this action has score = -40.8** (negative!)

### Root Cause

In `agent_decisions.json` (200+ entries), the action `produce-apply-suggestions` appears ~20 times with:
- `urgency: 12`
- `impact: 5` 
- `score: -40.8`

The scoring formula in autonomous_agent.py appears to compute:
```
score = urgency * 0.4 + impact * 0.6 = 12*0.4 + 5*0.6 = 4.8 + 3.0 = 7.8
```

But the logged score is **-40.8** — this is a different formula or the score is being transformed somewhere.

### Pattern: Agent Loops on Same Action

The agent has chosen `produce-apply-suggestions` **20+ consecutive times** (every ~2 minutes via cron). Despite:
- Anti-loop tracking in `agent_decisions.json` (`last_5_actions`, `consecutive_same`)
- The action having a NEGATIVE logged score
- Other actions available with positive scores (e.g., `produce-deploy-new-scheme` score 4.4, `produce-confirm-withdrawals` urgency 6 impact 7)

### Finance-Aware Decision Matrix Status

The integration described in this skill says:
> "Autonomous agent now has finance-aware decision matrix. It reads Finance Core (P&L, tax liability, pending withdrawals, scheme unit economics) to make scale/kill/deploy/confirm/pay-tax decisions."

But in practice:
1. **$235 pending withdrawals** — action exists (`produce-confirm-withdrawals`) but never selected
2. **TG-MiniApps-CPA deployment** — HITL gate blocks it, but agent doesn't try to resolve the gate
3. **Content-Locking-CPA test** — Active test in ARBITRAGE_LOG.md but agent doesn't advance it
4. **Agent keeps "applying suggestions"** that don't produce measurable value (just logs patterns)

### Missing Pieces in Current Architecture

| Missing | Impact |
|---|---|
| HITL gate resolution in action loop | Agent waits forever, never escalates |
| `done_when = money on card` enforcement | Agent optimizes for "suggestions applied" not revenue |
| Score formula transparency | Negative logged score but positive computed score |
| Anti-loop actually working | 20+ same action despite tracking |

### Recommended Fixes for autonomous_agent.py

1. **Fix scoring**: Ensure computed score matches logged score. Add debug output.
2. **Finance-weighted scoring**: Multiply base score by `(1 + roi_pct/100)` for PRODUCE actions tied to schemes.
3. **HITL-aware selection**: If action requires HITL and gate pending > 24h → boost urgency to force resolution.
4. **Value verification gate**: After action executes, verify `result` contains measurable output (file, revenue, deployment). If only "noted patterns" → mark as low-value, don't repeat.
5. **Consecutive same action kill**: If `consecutive_same >= 3` → force tier rotation AND filter out that action for N cycles.

### Test Evidence

Run: `python scripts/autonomous_agent.py --dry`
Expected: Different action each run (or at least tier rotation)
Actual: Same action 20+ times, negative logged score, positive displayed score

---

## Related Session: 2026-07-05

The `autonomous-system-operations` skill already documents:
- "Waiting for permission" anti-pattern
- "Incomplete verification" anti-pattern  
- "Truncated execution" anti-pattern
- Finance Core integration
- HITL Gates pattern

This reference adds the **score inversion + action loop** evidence from 2026-07-06.