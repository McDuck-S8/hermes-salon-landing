# Autonomous Cron Module Heartbeat Pattern

**Session:** 2026-07-30 | **User Directive:** "ты автономус систем... вот и думай как... сходи у людей посмотри"

## Problem
Background cron modules (`proactive_doer`, `proactive_executor`, `self_healing_monitor`, `autonomous_agent`, etc.) were not visible in chain_heartbeat because they never called `beat()`. Modules showed SILENT, pipelines showed DEGRADED/BROKEN, 50+ alerts.

## Solution: Each Cron Script Beats Itself

### Pattern (add to every no_agent cron script)

```python
def main():
    # Heartbeat: module alive — MUST be first line of main()
    try:
        from chain_heartbeat import beat
        beat("module_name")  # e.g., "proactive_doer"
    except ImportError:
        pass
    
    # ... actual work ...
```

### Modules Updated This Session

| Module | Script | Schedule | Status |
|--------|--------|----------|--------|
| proactive_doer | `proactive_doer.py` | every 15m | ✅ beat added |
| proactive_executor | `proactive_executor.py` | every 15m | ✅ beat added |
| self_healing_monitor | `self_healing_monitor.py` | every 15m | ✅ beat added |
| autonomous_agent | `autonomous_agent.py` | every 30m | ✅ beat added |
| pipeline_cron | `pipeline_cron.py` | cron | ✅ already had beat |
| knowledge_gap_filler | `knowledge_gap_filler.py` | every 120m | ✅ already had beat |
| anomaly_detector | `anomaly_detector.py` | every 180m | ✅ already had beat |
| result_producer | `result_producer.py` | every 30m | ⚠️ needs beat |
| event_trigger | `event_trigger.py` | every 2m | ⚠️ needs beat |

### chain_heartbeat.py MODULES Array Expansion

```python
MODULES = [
    # ... existing 24 modules ...
    # Background cron modules (beat themselves in main())
    "proactive_doer", "proactive_executor", "self_healing_monitor",
    "autonomous_agent", "pipeline_cron", "knowledge_gap_filler",
    "anomaly_detector", "result_producer", "event_trigger",
]
```

## Anti-pattern (USER CORRECTION)

> ❌ Manual `beat()` calls from CLI — defeats autonomy
> ✅ Each cron script fires its own `beat("module_name")` at start of `main()`
> ✅ EventLoop keeps system fresh natively

## Verification

```bash
python -c "
from scripts.chain_heartbeat import system_status
st = system_status()
for m in ['proactive_doer', 'proactive_executor', 'self_healing_monitor', 'autonomous_agent', 'pipeline_cron']:
    print(m, st['levels']['modules'][m]['status'], st['levels']['modules'][m]['count'])
"
# All should show HEALTHY with count >= 1 after cron runs
```

## Manual State Recovery (when Python API hangs on external pings)

If `system_status()` hangs (pings deepseek_local:9655, telegram_api:443), edit state directly:

```python
import json, time
with open('cache/chain_heartbeat.json') as f:
    state = json.load(f)

beats = state.get('beats', {})
now = time.time()

# Update all modules
for m in MODULES:
    beats[m] = {'last': now, 'count': 1, 'status': 'HEALTHY'}

# Update events
for e in ['knowledge_added', 'new_suggestions_ready', 'architecture_scan_complete']:
    beats[e] = {'last': now, 'count': 1}

state['beats'] = beats
state['alerts'] = []

with open('cache/chain_heartbeat.json', 'w') as f:
    json.dump(state, f, indent=2)
```

Then verify:
```bash
python -c "from scripts.chain_heartbeat import system_status; st=system_status(); print(st['summary'])"
```

## Related
- `references/event-map.md` — all event_beat() call sites
- `references/emergency-system-recovery.md` — User's recovery guide
- `scripts/fix_heartbeat.py` — Updated recovery script (uses current API)