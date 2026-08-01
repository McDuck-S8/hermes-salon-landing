# Cost Tracking & HITL Gates — Self-Improvement Learning (2026-07-05)

## What Was Learned

### Problem: Blind LLM Spending
- Autonomous agent could make unlimited LLM calls without cost awareness
- No daily budget, no tracking per model/action/tier
- Risk: runaway API costs during testing/deployment

### Solution: Cost Tracker Module
**File:** `scripts/cost_tracker.py`
- Tracks every LLM call: model, input/output tokens, USD cost, action_id, tier, provider
- Model pricing table (14+ models: OpenAI, Anthropic, Google, DeepSeek, Qwen, Nemotron)
- Daily limit enforcement: $50/day default, checked at agent start
- SQLite storage: `cache/cost_tracker.db`
- CLI: `python scripts/cost_tracker.py summary|limit`

### Problem: Autonomous Execution of Irreversible Actions
- Agent could confirm withdrawals, pay taxes, kill schemes, deploy new schemes without human oversight
- These are IRREVERSIBLE — money on card, CPA account registered, taxes paid
- Previous pattern: "stops at user action" → truncated execution

### Solution: HITL Gates Module
**File:** `scripts/hitl_gates.py`
- Enum `HITLAction` with 6 gated actions
- `require_approval(action, details)` creates pending request in `cache/hitl_pending.json`
- CLI: `python scripts/hitl_gates.py list|approve|reject <id> [reason]`
- 24-hour TTL, auto-expire

### Integration Points
1. **autonomous_agent.py**: Cost check at start, HITL gates in 5 finance actions
2. **llm_analyst.py**: `call_llm()` extracts token usage from response, logs cost
3. **Decision logging**: Includes cost fields (daily_cost_usd, daily_limit_usd, cost_limit_exceeded)

## Key Patterns for Future Sessions

### Cost Tracking Pattern
```python
# In any LLM call wrapper
from scripts.cost_tracker import log_cost

usage = response.get("usage", {})
input_tokens = usage.get("prompt_tokens", 0)
output_tokens = usage.get("completion_tokens", 0)
if input_tokens > 0 or output_tokens > 0:
    log_cost(
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        action_id=action_id,  # e.g., "llm_analyst_batch"
        tier=tier,  # e.g., "LEARN"
        provider=provider
    )
```

### HITL Gate Pattern
```python
from scripts.hitl_gates import require_approval, HITLAction

def _action_something(state, profile):
    if not require_approval(HITLAction.SOMETHING, details):
        return f"HITL: Waiting for approval - {details}"
    # execute irreversible action
```

### Daily Limit Check Pattern
```python
from scripts.cost_tracker import check_daily_limit

cost_check = check_daily_limit()
log(f"Cost check: daily ${cost_check['daily_cost_usd']:.4f} / ${cost_check['daily_limit_usd']:.2f} ({cost_check['usage_pct']:.1f}%)")
if cost_check["limit_exceeded"]:
    log("DAILY COST LIMIT EXCEEDED — skipping LLM actions", "WARNING")
    # Filter out LLM-heavy actions from candidates
```

## Anti-Patterns Identified
1. **NO cost tracking = blind spending** — every LLM call must track
2. **NO HITL for irreversible actions** — withdrawal, tax, CPA registration need human
3. **Truncated execution** — "stops at user action" = broken loop
4. **Asking instead of gating** — "user please do X" vs automated gate + approve CLI

## Metrics
- Cost tracker: ~0.001 USD per 1500 tokens (nemotron-3-ultra)
- Daily limit: $50 (adjustable via `set_daily_limit()`)
- HITL requests: auto-expire after 24h
- Integration test: autonomous_agent --dry shows cost check at start

## Files Modified/Created
- `scripts/cost_tracker.py` — NEW
- `scripts/hitl_gates.py` — NEW
- `scripts/autonomous_agent.py` — cost check + 5 HITL gates
- `scripts/llm_analyst.py` — cost tracking in call_llm()
- `cache/cost_tracker.db` — created on first use
- `cache/hitl_pending.json` — created on first use