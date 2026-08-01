# Cost Tracking & HITL Gates for Arbitrage Execution — 2026-07-05

## What Changed for Arbitrage Execution

### Cost Tracking Integration
- Every LLM call during arbitrage deployment now tracked: cost_tracker.log_cost()
- Daily limit: $50/day prevents runaway spending during scheme testing
- Finance-aware decisions in autonomous_agent use cost data

### HITL Gates for Irreversible Arbitrage Actions
New gates added to `autonomous_agent.py` finance-aware actions:

| Action | HITL Gate | Details Required |
|--------|-----------|------------------|
| `_action_scale_scheme` | `SCALE_BUDGET` | scheme_name, budget_usd |
| `_action_kill_scheme` | `SCHEME_KILL` | scheme_name, reason |
| `_action_deploy_scheme` | `NEW_SCHEME_DEPLOY` | scheme_id, title |
| `_action_confirm_withdrawals` | `WITHDRAWAL_CONFIRM` | network, amount_usd, method |
| `_action_pay_taxes` | `TAX_PAYMENT` | amount_usd, amount_rub |

### Impact on Arbitrage Execution Workflow

**BEFORE (2026-06-29):**
1. Agent prepares scheme fully
2. Stops at "user action needed" (CPA registration, withdrawal check)
3. Waits for user → truncated execution

**NOW (2026-07-05):**
1. Agent prepares scheme fully
2. HITL gate creates pending request in `cache/hitl_pending.json`
3. User runs: `python scripts/hitl_gates.py approve <id>`
4. Agent continues execution immediately after approval
5. Loop closes: `done_when = money on card`

### Testing the Gates
```bash
# Check pending approvals
python scripts/hitl_gates.py list

# Approve withdrawal confirmation
python scripts/hitl_gates.py approve <request_id>

# Reject if needed
python scripts/hitl_gates.py reject <request_id> "Reason"

# Test cost tracking
python scripts/cost_tracker.py summary
python scripts/cost_tracker.py limit

# Run autonomous agent with dry-run
python scripts/autonomous_agent.py --dry
```

### Arbitrage Workshop Integration
- Schemes in `ARBITRAGE_WORKSHOP.md` now have HITL requirements documented
- `validate-fix.sh` checks still apply: revenue ≥ $1, ≥1 confirmed withdrawal, tax < $500
- Cost tracking adds new dimension: scheme deployment cost vs revenue

### Files
- `scripts/cost_tracker.py` — cost tracking module
- `scripts/hitl_gates.py` — HITL gates module
- `scripts/autonomous_agent.py` — integration point (5 finance actions gated)
- `scripts/llm_analyst.py` — cost tracking in LLM calls
- `cache/hitl_pending.json` — pending approvals
- `cache/cost_tracker.db` — cost records