# Chaos Monkey Stress Test — 2026-07-19

## Goal
Verify that Chain Heartbeat v3 event-driven architecture actually detects failures, creates alerts, and recovers when components return.

## Tests executed

| # | Component | Failure mode | Detection | Recovery |
|---|-----------|-------------|-----------|----------|
| 1 | BrowserOS (port 9003) | Process killed | `ping_all_external()` — TCP connect fails → DOWN | HTTP stub restarted → HEALTHY |
| 2 | health module (hermes_health.py) | File renamed | `architecture_model.scan()` — file_exists=False → DEGRADED | File restored → 21/24 HEALTHY |
| 3 | knowledge_pipeline (knowledge_added) | event_beat monkey-patched to no-op | `check_events()` — last=0 → SILENT alert | Original restored + event refired → HEALTHY |
| 4 | Crystal (architecture_scan_complete) | event_beat commented out in .py | `check_events()` — never fired → SILENT alert | Comment restored + scan → HEALTHY |
| 5 | system_heartbeat.json | Simulated missing | `system_status()` regenerates on every call | Auto-recovery: always recreated |
| 6 | DUAL: BrowserOS + knowledge_added | Both failed simultaneously | Two independent alerts at different levels (4 + 1) | Both restored → HEALTHY |

## Key weaknesses found & fixed

**#1 Alert auto-clear** — alerts accumulated indefinitely. Fixed in chain-heartbeat v3.1:  
`_cleanup_alerts()` integrated into `event_beat()`, `ping_external()`, `system_status()`.

**#2 Stale data** — `system_status()` returned cached state, not real-time. Fixed in v3.2:  
Auto-refreshes external pings older than `EXTERNAL_TIMEOUT` (300s) on every `system_status()` call.

**#3 Dual-layer health** — chain-heartbeat (beat-based) ≠ architecture_model (file-based). Fixed in v3.2:  
`beat()` accepts `status=` parameter. `architecture_model.py` passes `status=ms["health"]`. `system_status()` uses explicit status over beat-based inference.

**#4 Push SILENT** — only detected on explicit `check_events()` call. Fixed in v3.2:  
`system_status()` calls `check_events()` + `check_modules()` internally on every invocation.

**#5 Pipeline propagation** — event SILENT didn't cascade to pipeline. Fixed in v3.2:  
`check_pipelines()` checks `PIPELINE_EVENTS` mapping — events linked to pipelines affect DEGRADED/BROKEN status.

## Verification

All 5 weaknesses confirmed fixed via `system_status()` after chaos tests.  
Final state: Events 2/3, Modules 21/24 (2 real DEGRADED), Pipelines 2/3 (1 real DEGRADED from SILENT event), alerts only for real-DOWN services.
