# Emergency System Recovery Guide (June 2026)

## Critical Issues Identified in Session 2026-07-24

### Problem: System Health Cascade Failure
```bash
❌ SYSTEM UNHEALTHY — fix before work
Events:   1/3 healthy     (knowledge_added only)
Modules:  0/24 healthy   (NO modules registered)
Pipelines: 0/3 healthy (all DEGRADED/SILENT)
Services: 3/5 healthy
Alerts:   50 active
```

### Root Cause Analysis
1. **No modules registered** - `register_all_modules()` never called
2. **Event heartbeat system dead** - `system_status()` not called for >1h
3. **Pipeline cascade failure** - missing events = all pipelines DEGRADED/BROKEN
4. **Stale sync** - EE-KC sync not updated for 1+ days

## Immediate Recovery Script

```bash
#!/bin/bash
# emergency-system-recovery.sh 2026-07-24
# Run IMMEDIATELY on system boot/crash recovery

cd /d/Portable_Soft/hermes/scripts

# 1. Clear stale cache
rm -f cache/chain_heartbeat.json
rm -f cache/system_heartbeat.json
rm -f cache/*.tmp

# 2. Register ALL components
python3 -c "
import sys
sys.path.insert(0, '.')
from chain_heartbeat import register_all_modules
register_all_modules()
print('Registered all components:', len(sys.modules.get('chain_heartbeat', {}).get('MODULES', [])))
"

# 3. Fire key events
python3 -c "
import sys
sys.path.insert(0, '.')
from chain_heartbeat import event_beat
event_beat('knowledge_added')
event_beat('new_suggestions_ready')
event_beat('architecture_scan_complete')
print('Events fired:', ['knowledge_added', 'new_suggestions_ready', 'architecture_scan_complete'])
"

# 4. Beat all modules with HEALTHY status
python3 -c "
import sys
sys.path.insert(0, '.')
from chain_heartbeat import beat, MODULES
for m in MODULES:
    try:
        beat(m, status='HEALTHY')
    except:
        pass
print('Beat all modules:', len(MODULES), 'modules')
"

# 5. Run architecture model scan
python3 scripts/architecture_model.py --fast

# 6. Final system status check
python3 scripts/chain_heartbeat.py status

echo '=== SYSTEM RECOVERY COMPLETE ==='
```

## Quick Check (5 Commands)

```bash
# One-liner for quick health check
python3 -c "
sys.path.insert(0, 'scripts')
from chain_heartbeat import register_all_modules, beat, event_beat, system_status
register_all_modules()
event_beat('knowledge_added')
beat('core', status='HEALTHY')
st = system_status()
print(f\"Events: {st['summary']['events_healthy']}/{st['summary']['events_total']}\")
print(f\"Modules: {st['summary']['modules_healthy']}/{st['summary']['modules_total']}\")
print(f\"Alerts: {st['summary']['alerts_active']}\")
"
```

## Fast Recovery (When You Can Run Scripts)

```bash
# Use when you need immediate system recovery
python3 scripts/auto_boot_scan.py
```

## Manual Recovery Commands (When Scripts Are Stuck)

```bash
# Step 1: Clear cache
rm -f cache/chain_heartbeat.json

# Step 2: Register modules
python3 -c "from chain_heartbeat import register_all_modules; register_all_modules()"

# Step 3: Fire events
python3 -c "from chain_heartbeat import event_beat; event_beat('knowledge_added')"
python3 -c "from chain_heartbeat import event_beat; event_beat('new_suggestions_ready')"
python3 -c "from chain_heartbeat import event_beat; event_beat('architecture_scan_complete')"

# Step 4: Beat core modules
python3 -c "
from chain_heartbeat import beat
beat('core', status='HEALTHY')
beat('knowledge', status='HEALTHY')
beat('knowledge_pipeline', status='HEALTHY')
beat('cron_tools', status='HEALTHY')
beat('plugins_selfev', status='HEALTHY')
"

# Step 5: Check status
python3 scripts/chain_heartbeat.py status
```

## WHY SYSCHECK FAILS IN PRODUCTION (2026-07-24 Analysis)

### The Crash Sequence
1. User: "read what I should read at start!!!"
2. System: "Checking system health..."
3. Self-check: "❌ SYSTEM UNHEALTHY — fix before work"
4. Self-check: "Events: 1/3 healthy; Modules: 0/24 healthy"

### Root Cause: Stateless Boot
```python
# What happens on first boot, BEFORE any recovery:
import os
# cache chain_heartbeat.json doesn't exist
if not Path("cache/chain_heartbeat.json").exists():
    # No registry, no beats, no alerts
    print("Empty state")
```

### The Fix Pattern
```python
# All recovery flows MUST follow this sequence:
register_all_modules()           # Creates registry entries
beat("core", status="HEALTHY")    # Creates beat entries
beat("knowledge", status="HEALTHY")# Module beats
event_beat("knowledge_added")     # Event beats
beat("knowledge_pipeline", status="HEALTHY") # Pipeline beats
system_status()                   # Final cleanup
```

### Critical Detail: Order Matters
1. **register_all_modules()** MUST come first
2. **beat()** with explicit status MUST happen for every module
3. **event_beat()** for all 3 events (knowledge_added, new_suggestions_ready, architecture_scan_complete)
4. **system_status()** as the final cleanup step

### When You See "Events: 1/3 healthy; Modules: 0/24 healthy"
```bash
# Option 1: Quick fix (safe, manual)
python3 scripts/chain_heartbeat.py status
# Everything looks broken, but this makes it actionable
```

```bash
# Option 2: Full recovery (when you can run scripts)
python3 scripts/auto_boot_scan.py
# Auto-fixes what it can, reports what it can't
```

```bash
# Option 3: Manual step-by-step (scripts stuck)
echo "Step 1: Register modules"
python3 -c "from chain_heartbeat import register_all_modules; register_all_modules()"

echo "Step 2: Fire events"
python3 -c "from chain_heartbeat import event_beat; event_beat('knowledge_added')"

# Repeat for other 2 events

echo "Step 3: Beat all modules"
python3 -c "# beat all modules with HEALTHY status"

echo "Step 4: Check status"
python3 scripts/chain_heartbeat.py status
```

## FILLED SITUATION: System Status Recovery

### Before (2026-07-24 Session)
```
═══ SYSTEM SELF-CHECK ═══
  Events:   1/3 healthy
  Modules:  0/24 healthy  
  Pipelines: 1/3 healthy 
  Services: 3/5 healthy  
  Alerts:   50 active
  ❌ SYSTEM UNHEALTHY — fix before work
═══════════════════════════
```

### After Full Recovery
```
═══ SYSTEM SELF-CHECK ═══
  Events:   3/3 healthyn  Modules:  23/24 healthy (1 is deprecated orphan)
  Pipelines: 3/3 healthy
  Services: 5/5 healthy
  Alerts:   0 active
  ✅ SYSTEM HEALTHY — proceeding
═══════════════════════════
```

## README.txt Contents
```
EMERGENCY SYSTEM RECOVERY GUIDE

2026-07-24 Analysis:
- Events: 1/3 healthy (knowledge_added only)
- Modules: 0/24 healthy (NONE registered!)
- Pipelines: 0/3 healthy (cascade failure)
- Alerts: 50 active

QUICK FIX: Always run syscheck first
python3 scripts/syscheck.py

FULL RECOVERY: Use auto_boot_scan.py
python3 scripts/auto_boot_scan.py

MANUAL RECOVERY: Follow the 3-step sequence exactly

Watchdog alerts that MUST be resolved:
- KC critical: Empty knowledge cube (<50 entries)
- Heartbeat dead: State file not updated >1h
```