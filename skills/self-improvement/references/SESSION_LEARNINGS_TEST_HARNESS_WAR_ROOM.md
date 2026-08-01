# Session Learnings: Test Harness + War Room + Kill Switches Integration

## Key Techniques Discovered

### 1. Test Harness Integration Pattern
**Problem**: `procedural_executor.py` needed to verify triggers via Test Harness
**Solution**: Created separate `verify_trigger.py` module instead of embedding in procedural_executor:
```python
# verify_trigger.py - standalone module
from skills.devops.test-harness.scripts.harness import Harness

def verify_with_test_harness(trigger_spec):
    harness = Harness()
    return harness.verify(trigger_spec)
```
**Why**: Avoids circular imports, keeps procedural_executor clean, allows independent testing.

### 2. War Room Mock Runner
**Problem**: `claude` CLI not installed on system (`D:\npm-global/node_modules/@anthropic-ai/claude-code/bin/claude.exe: No such file or directory`)
**Solution**: Created `war_room_mock.py` that simulates agent responses without external CLI
**Pattern**: 
```python
# Mock mode for development/testing
def run_mock_standup(agents):
    for agent in agents:
        print(f"[{agent}] Standup: Ready")
```

### 3. Kill Switch Integration Pattern (Standardized)
```python
# At module top level
import os

# 1. Kill Switch check FIRST
if os.environ.get("HERMES_<SWITCH>_ENABLED", "true").lower() != "true":
    return {"status": "blocked", "reason": "HERMES_<SWITCH>_ENABLED=false"}

# 2. Exfiltration Guard check SECOND
try:
    from skills.devops.exfiltration_guard.scripts.exfil_guard import scan_outbound
    exfil_result = scan_outbound(content, source=f"<component>:<id>")
    if exfil_result.get("blocked"):
        return {"status": "blocked", "reason": f"Exfiltration: {exfil_result['matches']}"}
except ImportError:
    pass

# 3. Proceed
```

### 4. Async Delegation Reliability
**Problem**: 3 parallel subagents all timed out at 600s
**Root cause**: Network/API instability + no circuit breaker
**Workaround**: Direct execution in main thread for critical paths, small atomic steps

## User Preference Corrections

1. **No `write_file` for full Python files** — use `patch` or `sed -i`
2. **Correct tools only**: `read_file`, `search_files`, `patch` — NOT `terminal` with cat/grep
3. **Russian responses** — user writes in Russian
4. **Autonomous execution** — "бери и делай", don't wait
5. **Save before report** — Pre-Report Checklist mandatory

## Integration Status

| Component | Test Harness | War Room | Kill Switches | Exfil Guard |
|-----------|--------------|----------|---------------|-------------|
| procedural_executor.py | ✅ verify_trigger.py | — | — | — |
| telegram_bridge.py | — | — | ✅ HERMES_BRIDGE_ENABLED | ✅ check_telegram_message |
| knowledge_cube.py | — | — | ✅ HERMES_KC_WRITE_ENABLED | ✅ scan_outbound |
| cron/scheduler.py | — | — | ✅ HERMES_CRON_ENABLED (tick + run_job) | ✅ scan_outbound |
| llm_analyst.py | — | — | ✅ HERMES_LLM_ENABLED | — |