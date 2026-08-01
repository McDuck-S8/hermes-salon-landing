---
id: sensor-array
type: skill
namespace: knowledge/ai-core
status: canon
version: 1.0.0
owner: operator
created: 2026-06-29T00:00:00Z
summary: Internal system sensors (CPU, RAM, disk, processes, errors, files)
description: |
  Sensor Array collects internal system metrics and emits events to the event bus.
  Monitors: CPU usage, memory usage, disk usage, process health, error logs,
  file system changes. Runs continuously as background sensors.
depends_on:
  - event-bus
tags:
  - sensors
  - system-metrics
  - monitoring
  - internal
confidence: 0.9
retrieval_class: hot
export_class: operator
---

# Sensor Array — Internal System Sensors

## Monitored Metrics
| Metric | Source | Frequency |
|--------|--------|-----------|
| CPU Usage | `psutil` | Continuous |
| Memory Usage | `psutil` | Continuous |
| Disk Usage | `psutil` | Continuous |
| Process Health | `psutil` + `pgrep` | On-change |
| Error Log Tail | `logs/` | Continuous |
| File Watchers | `watchdog` | On-change |

## Output Events
- `system_metric` — CPU/RAM/disk/process metrics
- `process_event` — Process start/stop/crash
- `file_change` — File create/modify/delete
- `error_detected` — Error patterns in logs

## Integration
- `scripts/sensor_array.py` — Main sensor loop
- Emits to `scripts/event_bus.py`

## Related Entities
- [[event-bus]] — Event bus consumer
- [[procedural-executor]] — Reflexes consumer