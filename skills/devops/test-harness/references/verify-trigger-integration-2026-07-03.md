# Verify Trigger Integration (2026-07-03)

## Integration with Procedural Executor

Created `scripts/verify_trigger.py` as a standalone module to avoid procedural_executor syntax issues.

### Usage
```python
from verify_trigger import verify_with_test_harness

result = verify_with_test_harness(
    "gateway_dead",
    "Gateway process not found — removed stale locks, killed zombies, restarted via hermes CLI",
    "D:/Portable_Soft/hermes/scripts/procedural_executor.py"
)
```

### Trigger-Specific Health Checks
Each trigger gets relevant behavioral checks:
- `gateway_dead` → gateway_process + telegram_proxy
- `network_dead` → network connectivity
- `memory` → memory_usage
- `port_3264` → qwen_api
- etc.

### Key Learning
**Separate verification module** avoids contaminating procedural_executor with Test Harness imports. The procedural_executor has complex syntax (Cyrillic, arrows, special chars) that breaks imports. A clean separate module solves this.

### Files
- `scripts/verify_trigger.py` — standalone verification module
- `scripts/procedural_executor.py` — imports and calls `verify_with_test_harness`