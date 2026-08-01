# Cost Tracking & HITL Gates — 2026-07-05 Session Notes

## What Was Built

### Cost Tracker (`scripts/cost_tracker.py`)
- Tracks token usage and USD cost per LLM call
- Model pricing table with 14+ models (OpenAI, Anthropic, Google, DeepSeek, Qwen, Nemotron)
- Daily limit enforcement: $50/day default
- SQLite database: `cache/cost_tracker.db`
- Integration: `log_cost(model, input_tokens, output_tokens, action_id, tier, provider)`

### HITL Gates (`scripts/hitl_gates.py`)
- Human-in-the-Loop approval for irreversible actions
- Actions gated: withdrawal confirmation, CPA registration, tax payment, scheme kill, budget scale, new scheme deploy
- Pending requests stored in `cache/hitl_pending.json`
- CLI: `python scripts/hitl_gates.py list|approve|reject <id> [reason]`

### Integration Points
1. **autonomous_agent.py**: Cost check at start, HITL gates in all finance-aware actions
2. **llm_analyst.py**: `call_llm()` extracts token usage from response and logs via `log_cost()`
3. **Decision logging**: Includes cost fields (daily_cost_usd, daily_limit_usd, cost_limit_exceeded)

## Key Patterns

### Cost Tracking Pattern
```python
from scripts.cost_tracker import log_cost

# In LLM call wrapper
usage = response.get("usage", {})
input_tokens = usage.get("prompt_tokens", 0)
output_tokens = usage.get("completion_tokens", 0)
if input_tokens > 0 or output_tokens > 0:
    log_cost(model=model, input_tokens=input_tokens, output_tokens=output_tokens,
             action_id=action_id, tier=tier, provider=provider)
```

### HITL Gate Pattern
```python
from scripts.hitl_gates import require_approval, HITLAction

def _action_something(state, profile):
    if not require_approval(HITLAction.SOMETHING, details):
        return f"HITL: Waiting for approval - {details}"
    # ... execute action
```

## Daily Limit Check
```python
from scripts.cost_tracker import check_daily_limit

cost_check = check_daily_limit()
log(f"Cost check: daily ${cost_check['daily_cost_usd']:.4f} / ${cost_check['daily_limit_usd']:.2f} ({cost_check['usage_pct']:.1f}%)")
if cost_check["limit_exceeded"]:
    log("DAILY COST LIMIT EXCEEDED — skipping LLM actions", "WARNING")
```

## Testing
```bash
# Test cost tracker
python scripts/cost_tracker.py summary
python scripts/cost_tracker.py limit

# Test HITL gates
python scripts/hitl_gates.py list

# Test autonomous agent with cost/HITL
python scripts/autonomous_agent.py --dry
```

## Files Modified
- `scripts/autonomous_agent.py` — cost check at start, HITL gates in 5 finance actions
- `scripts/llm_analyst.py` — cost tracking in `call_llm()`
- `scripts/cost_tracker.py` — NEW module
- `scripts/hitl_gates.py` — NEW module
- `scripts/validate-fix.sh` — already existed, deterministic verification