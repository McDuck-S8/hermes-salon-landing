# Cost Tracking + HITL Gates Integration

## Overview
Added in Session 2026-07-05 as part of Loop Engineering hardening.

## Cost Tracking (`scripts/cost_tracker.py`)

### Features
- Tracks token usage (input/output) per model
- Calculates USD cost using current model pricing
- Stores in SQLite (`cache/cost_tracker.db`)
- Daily limit enforcement ($50 default)
- Per-action, per-model, per-tier breakdown
- CLI: `python cost_tracker.py summary [days]` | `limit`

### Integration Points
1. **`autonomous_agent.py`** — `check_daily_limit()` at cycle start, logs daily cost
2. **`llm_analyst.py`** — `call_llm()` extracts `usage.prompt_tokens` / `completion_tokens` and calls `log_cost()`
3. **Decision logging** — adds `daily_cost_usd`, `daily_limit_usd`, `cost_limit_exceeded` to decision record

### Pricing Table (2025 rates, per 1M tokens)
| Model | Input | Output |
|-------|-------|--------|
| gpt-4o | $5.00 | $15.00 |
| gpt-4o-mini | $0.15 | $0.60 |
| claude-3-5-sonnet | $3.00 | $15.00 |
| claude-3-5-haiku | $1.00 | $5.00 |
| gemini-1.5-pro | $3.50 | $10.50 |
| deepseek-chat | $0.14 | $0.28 |
| nemotron-3-ultra | $0.50 | $1.50 |

### Daily Limit Logic
```python
cost_check = check_daily_limit()
if cost_check["limit_exceeded"]:
    log("DAILY COST LIMIT EXCEEDED — skipping LLM actions", "WARNING")
    # Filter out LLM-heavy actions from candidates
```

## HITL Gates (Human-In-The-Loop)

### Purpose
Prevent irreversible autonomous actions without user confirmation.

### Required Gates
| Action | Trigger | Implementation |
|--------|---------|----------------|
| CPA account registration | `_action_deploy_scheme` | Prompt user before registering |
| Withdrawal request | `_action_confirm_withdrawals` | User must confirm amount/network |
| Tax payment | `_action_pay_taxes` | User confirms amount before payment |
| Scheme kill (large spend) | `_action_kill_scheme` | If spend > $100, require confirmation |

### Implementation Pattern
```python
def hitl_confirm(action: str, details: dict) -> bool:
    """Request human confirmation for irreversible action."""
    if os.environ.get("HERMES_HITL_ENABLED", "true").lower() != "true":
        return True  # Bypass in automated test mode
    
    # Log request
    log_json({
        "event": "hitl_request",
        "action": action,
        "details": details,
        "timestamp": datetime.now().isoformat()
    })
    
    # In production: send Telegram message, wait for callback
    # For now: return False to block
    return False
```

## Structured Logging (Observability)

### log_json() Format
```json
{
  "trace_id": "uuid4",
  "span_id": "uuid4", 
  "event": "llm_call|cost_log|hitl_request|decision",
  "timestamp": "ISO8601",
  "action_id": "produce-scale-content-locking-cpa",
  "tier": "PRODUCE",
  "model": "nemotron-3-ultra",
  "tokens": {"input": 1000, "output": 500},
  "cost_usd": 0.00125,
  "daily_total_usd": 0.05
}
```

### Usage
```python
log_json({
    "trace_id": trace_id,
    "event": "llm_call",
    "model": model,
    "tokens": {"input": input_tokens, "output": output_tokens},
    "cost_usd": total_cost,
    "action_id": action_id,
    "tier": tier
})
```

## Updated Validation Flow

```
Orchestrator Cycle Start
    │
    ├─► check_daily_limit() → if exceeded: filter LLM actions
    │
    ├─► evaluate_actions() → includes cost-aware candidates
    │
    ├─► pick_best_action() → selected action
    │
    ├─► IF action requires HITL:
    │     hitl_confirm() → wait for user → proceed/abort
    │
    ├─► Execute action (Maker)
    │     log_cost() on any LLM call
    │     log_json() structured events
    │
    ├─► Checker runs validate-fix.sh
    │
    └─► Decision logged with cost fields
```

## Files Modified This Session
- `scripts/cost_tracker.py` — NEW: cost tracking module
- `scripts/autonomous_agent.py` — cost check at start, cost fields in decision
- `scripts/llm_analyst.py` — cost logging in call_llm()
- `scripts/validate-fix.sh` — already had finance integration
- `skills/self-improvement/loop-engineering/SKILL.md` — updated pitfalls