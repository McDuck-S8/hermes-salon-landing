# Chaos Monkey Test — System Stress Protocol

**Date:** 2026-07-19  
**Target:** Chain Heartbeat v3 (Event-Driven)  
**Tester:** Hermes Agent  

## Purpose

Verify that the event-driven self-healing system actually detects failures, creates alerts, and recovers — not just reports itself as HEALTHY in quiet conditions.

## Test Suite (6 tests)

### Test 1: External Service DOWN
1. Kill the external process (e.g., BrowserOS on 9003)
2. Run `ping_all_external()` — should show DOWN
3. Run `system_status()` — alert should exist
4. Restore service (start stub)
5. Run `ping_all_external()` — should show HEALTHY

### Test 2: Module DEGRADED
1. Remove a file tracked by `architecture_model.py` (e.g., rename `scripts/hermes_health.py`)
2. Run `architecture_model.scan()` — module count should decrease
3. Verify `architecture_model.json` shows the module with missing files
4. Restore file
5. Run `architecture_model.scan()` — module should return to HEALTHY

### Test 3: Pipeline BLOCKED (Event SILENT)
1. Monkey-patch `event_beat("knowledge_added")` to no-op
2. Clear the event's heartbeat state (`last: 0, count: 0`)
3. Call `check_events()` — should show SILENT with alert
4. Restore `event_beat` and refire
5. Verify event shows HEALTHY again

### Test 4: Event Source BLOCKED
1. Remove/comment `event_beat("architecture_scan_complete")` in `architecture_model.py`
2. Run the scan
3. Clear the event's beat state
4. Call `check_events()` — should detect SILENT
5. Restore and re-run scan
6. Verify HEALTHY

### Test 5: System File Auto-Recovery
1. Confirm `system_status()` regenerates `cache/system_heartbeat.json` on every call
2. Check that all 5 levels are present in the output

### Test 6: Dual Simultaneous Failure
1. Kill external service (Test 1) + Block event (Test 3) SIMULTANEOUSLY
2. Run `check_events()` + `ping_all_external()`
3. Verify TWO distinct alerts, different levels, different causes
4. Restore BOTH
5. Verify both HEALTHY

## What to Measure

| Metric | How | Target |
|--------|-----|--------|
| Detection time | Time between failure and first alert | <1s (on next check call) |
| Alert content | Does alert name the broken component? | ✅ |
| Cause isolation | Single vs dual — are causes distinct? | ✅ |
| Recovery detection | After restore — is component HEALTHY? | ✅ |
| Alert accumulation | Do old alerts persist after recovery? | ❌ (bug: manual clear needed) |

## Known Gaps Post-Test (2026-07-19)

1. **Alert auto-clear**: alerts DO NOT auto-close when component recovers. Must implement: on `ping_all_external()`, clear cleared alerts.
2. **system_status() is cached**: returns last-known beat state, not real-time. Does NOT auto-ping. Design choice — add real-time flag.
3. **Dual-layer health**: chain_heartbeat (beat-based) and architecture_model (file-based) use different metrics. Module can be HEALTHY in heartbeat but DEGRADED in architecture scan.
4. **Pipeline degradation**: SILENT event does NOT propagate to pipeline status. knowledge_pipeline stays HEALTHY even when knowledge_added is SILENT.
