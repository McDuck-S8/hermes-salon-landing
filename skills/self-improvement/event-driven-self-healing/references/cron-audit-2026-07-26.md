# 62 Cron Jobs Audit — 2026-07-26

## Summary

| Class | Count | Fate |
|-------|-------|------|
| **A — Fully event-driven** | **35** | Remove cron. React to `session_end`, `service_down`, `knowledge_added`, etc. |
| **B — Scheduled delivery via time:tick handler** | **17** | Remove cron. Handle on `EventLoop.time:tick` → check "my hour" and execute. |
| **C — External sensors (minimal poll)** | **10** | Keep rare poll (1h-4h). On new data → `emit_event()`. |

## Class A — Fully Event-Driven (35)

These run on a schedule but do work triggered by real events.
Remove cron; register event handlers instead.

| Current Cron | Schedule | Trigger Event | Replacement |
|-------------|----------|--------------|-------------|
| `event-trigger` | every 2m | — (already integrated) | **REMOVED** — EventLoop does this inline |
| `proactive-executor` | every 15m | `session_start` / `event_processed` | `emit_event("session_start")` → handler |
| `proactive-doer` | every 15m | `session_start` / `event_processed` | `emit_event("session_start")` → handler |
| `self-healing-monitor` | every 15m | `cron_failed` / `service_down` | `emit_event("service_down")` → handler |
| `result-producer` | every 30m | `cron_failed` | `emit_event("cron_failed")` → handler |
| `autonomous-agent` | every 30m | `session_start` / `time:tick` | `emit_event("session_start")` → handler |
| `system-watcher` | every 60m | — (already covered by EventLoop heartbeat) | **REMOVED** — EventLoop heartbeat covers this |
| `auto-fetch-sessions` | every 60m | `session_end` | `emit_event("session_end")` → handler |
| `subconscious-loop` | every 120m | `session_end` | `emit_event("session_end")` → handler |
| `unified-system-cycle` | every 120m | `session_end` | `emit_event("session_end")` → handler |
| `knowledge-pipeline` | every 120m | `knowledge_added` | `emit_event("knowledge_added", {"count": N})` → handler |
| `knowledge-gap-filler` | every 120m | `knowledge_added` | `emit_event("knowledge_added", {"count": N})` → handler |
| `anomaly-detector` | every 180m | `error_rate > threshold` | `emit_event("anomaly_detected")` → handler |
| `nightly-self-analysis` | 02:00 | `session_end` | `emit_event("session_end")` → handler |
| `memory-consolidation` | 03:00 | `session_end` | `emit_event("session_end")` → handler |
| `nightly-brain-scan` | 03:00 | `session_end` | `emit_event("session_end")` → handler |
| `dream-memory` | 03:00 | `session_end` | `emit_event("session_end")` → handler |
| `self-improvement-loop` | 05:00 | `new_suggestions_ready` | Already event-driven; cron is safety net. Remove cron. |
| `skill-evolution` | 04:00 | `session_end` | `emit_event("session_end")` → handler |
| `self-assessment` | 01:00 | `session_end` | `emit_event("session_end")` → handler |
| `update-runtime-context` | 04:30 | `session_end` | `emit_event("session_end")` → handler |
| `cube-feeder` | 04:15 | `session_end` | `emit_event("session_end")` → handler |
| `dimension-discovery` | 04:45 | `session_end` | `emit_event("session_end")` → handler |
| `cube-session-ingester` | every 6h | `session_end` | `emit_event("session_end")` → handler |
| `cube-to-memory` | every 6h | `knowledge_added` | `emit_event("knowledge_added")` → handler |
| `cube-categorizer` | every 6h | `knowledge_added` | `emit_event("knowledge_added")` → handler |
| `bot-watchdog` | every 10m | `service_down` | `emit_event("service_down")` → handler |
| `skill-watchdog` | every 10m | `skill_modified` | `emit_event("skill_modified")` → handler |
| `system-heartbeat-fixer` | every 10m | — (anti-pattern) | **REMOVED** — EventLoop manages heartbeat |
| `hermes-heartbeat` | every 60m | — (anti-pattern) | **REMOVED** — EventLoop has built-in heartbeat |
| `EE-KC Sync` | every 60m | `knowledge_added` | `emit_event("knowledge_added")` → handler |
| `JARVIS Security` | every 120m | `security_scan_requested` | `emit_event("security_scan_requested")` |
| `crystal-self-learning` | every 360m | `session_end` | `emit_event("session_end")` → handler |
| `knowledge-surfacer` | every 360m | `knowledge_added` | `emit_event("knowledge_added", {"count": N})` → handler |
| `system-metrics` | every 360m | `session_end` | `emit_event("session_end")` → handler |

## Class B — Scheduled Delivery via time:tick (17)

These need a time trigger but should use `EventLoop.time:tick`
event (generated every 60s) to check "is it my time?"

| Current Cron | Schedule | Event Loop Check |
|-------------|----------|-----------------|
| `morning-report` | 08:00 | `time:tick` → if h=8,m=0: generate report |
| `daily-digest` | 08:00 | `time:tick` → if h=8,m=5: digest |
| `daily-patch-review` | 08:00 | `time:tick` → if h=8,m=10: patch review |
| `daily-pnl-budget` | 07:00 | `time:tick` → if h=7,m=0: PnL |
| `daily-report` | 21:00 | `time:tick` → if h=21,m=0: daily report |
| `telegram-delivery` | every 60m | `time:tick` → every hour: deliver |
| `telegram-channel-poster` | 5x daily | `time:tick` → if h in {9,12,15,18,21},m=0 |
| `pinterest-auto-pinner` | every 30m | `time:tick` → every 30m in hour |
| `trend-scout-morning` | 10:00 | `time:tick` → if h=10,m=0 |
| `trend-scout-evening` | 18:00 | `time:tick` → if h=18,m=0 |
| `ai-ofm-generate` | every 180m | `time:tick` → every 3h |
| `sales-machine-scan` | 08:00 | `time:tick` → if h=8,m=0 |
| `uncertainty-observer` | 09:00 | `time:tick` → if h=9,m=0 |
| `weekly-portfolio-review` | Sun 09:00 | `time:tick` → if wd=6,h=9,m=0 |
| `market-research` | Mon 08:00 | `time:tick` → if wd=0,h=8,m=0 |
| `always-on-fast` | every 30m | `time:tick` → every 30m |
| `always-on-medium` | every 60m | `time:tick` → every hour |
| `self-evolution-cycle` | 04:00 | `time:tick` → if h=4,m=0 |

## Class C — External Sensors (10)

These poll external APIs that don't push events.
Keep minimal poll but emit_event on new data.

| Current Cron | Schedule | Notes |
|-------------|----------|-------|
| `rss-monitor` | every 240m | Poll RSS feeds. Emit `new_rss_item` on new. |
| `youtube-watch` | every 360m | Poll YouTube. Emit `new_youtube_video` on new. |
| `free-api-health-check` | every 360m | Poll external API health. |
| `llm-analyst` | every 1m | Poll `pending_analysis.json`. Reduce to 5m+. |
| `skill-self-improve` | PAUSED | Duplicate of `self-improve-skills`. REMOVE. |
| `self-upgrade-loop` | PAUSED | Overlaps others. REMOVE. |
| `arbitrage-scan` | every 6h | Poll CPA offers. Emit `new_offer` on new. |
| `daily-monitoring` | ? | Unknown. Investigate. |
| `pinterest-auto-pinner` | every 30m | Also in Class B. |
| `rediscovery-queue` | Not listed | Check if exists. |

## Migration Order

1. **Remove Class A cron jobs** — all 35 at once. Register event handlers.
2. **Convert Class B to time:tick handlers** — 17 remain but registered as
   `@EventLoop.on("time:tick")` handlers that check hour/minute.
3. **Minimize Class C poll frequency** — keep only 10, reduce frequency.
4. **Verify** — after each batch, run `cron list` to confirm count drops.
