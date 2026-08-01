# Cost Tracking & HITL Gates — Loop Engineering Integration (2026-07-05)

## What Changed for Loop Engineering

### New Sensors in the Validation Loop
The Loop Engineering pattern (Orchestrator → Maker → Checker) now has **two new sensors** feeding into the decision:

1. **Cost Sensor** — `check_daily_limit()` at cycle start
2. **HITL Sensor** — `require_approval()` before irreversible actions

### Integration Points

#### Orchestrator Level (autonomous_agent.py)
```python
# At start of main():
cost_check = check_daily_limit()
log(f"Cost check: daily ${cost_check['daily_cost_usd']:.4f} / ${cost_check['daily_limit_usd']:.2f}")
if cost_check["limit_exceeded"]:
    log("DAILY COST LIMIT EXCEEDED — skipping LLM actions", "WARNING")
    # Filter out LLM-heavy actions from candidates
```

#### Maker Level (finance-aware actions)
```python
# Each finance action checks HITL gate before execution
def _action_scale_scheme(state, profile):
    if not require_approval(HITLAction.SCALE_BUDGET, details):
        return "HITL: Waiting for budget scale approval"
    # execute
```

#### Checker Level (validate-fix.sh)
```bash
# Already checks finance state:
# - Revenue ≥ $1
# - ≥1 confirmed withdrawal
# - Tax < $500
# Now cost tracking adds: scheme deployment cost tracked in cost_tracker
```

### Decision Matrix Update
The autonomous agent's `evaluate_actions()` now generates candidates with cost/HITL awareness:
- `produce-scale-<scheme>` — checks `SCALE_BUDGET` gate
- `produce-kill-<scheme>` — checks `SCHEME_KILL` gate  
- `produce-deploy-new-scheme` — checks `NEW_SCHEME_DEPLOY` gate
- `produce-confirm-withdrawals` — checks `WITHDRAWAL_CONFIRM` gate
- `produce-pay-taxes` — checks `TAX_PAYMENT` gate

### Loop State Persistence
`state/loop-state.md` now implicitly includes cost/HITL state via decision logging:
```json
{
  "daily_cost_usd": 0.0013,
  "daily_limit_usd": 50.0,
  "cost_limit_exceeded": false
}
```

### Anti-Patterns Prevented
| Anti-Pattern | Loop Engineering Fix |
|--------------|---------------------|
| LLM runs without cost limit | Orchestrator checks `check_daily_limit()` at cycle start |
| Maker executes irreversible action | HITL gate blocks until human approves |
| Checker doesn't verify real metrics | `validate-fix.sh` queries finance_core for real data |
| Agent idles waiting for permission | Gate creates request, continues on approve; Orchestrator retries next cycle |
| Truncated deployment | `done_when = money on card` enforced by withdrawal_received check |

## Templates Updated
- `templates/validate-fix.sh` — already queries finance_core
- `templates/AGENTS.md` — already documents finance integration
- `templates/loop-state.md` — already has scheme metrics section

## Files
- `scripts/cost_tracker.py` — cost tracking module
- `scripts/hitl_gates.py` — HITL gates module
- `scripts/validate-fix.sh` — deterministic validation (queries finance_core)
- `scripts/autonomous_agent.py` — orchestrator with cost/HITL integration
- `state/loop-state.md` — persistent loop state