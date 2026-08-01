# Event ↔ Handler Mapping

Every event_beat() call location in the codebase.
All events fire at the DATA MUTATION point — not at cron or task completion.

## Events with expected interval

| Event | File | Trigger Point |
|---|---|---|
| `knowledge_added` | `scripts/kc_rag.py` | `upsert()` — immediately after INSERT/UPDATE commits. **Primary data entry point.** |
| `knowledge_added` | `scripts/cube_feeder.py` | `feed_entries()` — when `added > 0`. Secondary fallback for batch imports. |
| `knowledge_added` | `scripts/hermes_hooks.py` | `on_task_complete()` — legacy, kept for backward compat. |
| `new_suggestions_ready` | `scripts/self_improvement_loop.py` | `main()` — right before return, after suggestions generated. |
| `new_suggestions_ready` | `scripts/self_system.py` | `run_analysis()` — after `suggest_new_directions()`. |
| `new_suggestions_ready` | `scripts/suggestion_consumer.py` | `consume()` — after processing suggestions. |
| `architecture_scan_complete` | `scripts/architecture_model.py` | End of scan — after modules/connections scanned. |
| `user_correction` | `scripts/hermes_hooks.py` | `on_user_correction()` — when user issues a correction. |

## Architecture principle

Events must be wired at the **exact point where data enters the system**:

```
GOOD: kc_rag.upsert() → INSERT → COMMIT → event_beat("knowledge_added")
WRONG: cube_feeder (cron at 4:15) → feed_entries() → event_beat("knowledge_added")
WORST: hermes_hooks.on_task_complete() → event_beat("knowledge_added")
```

If the cron is paused or scheduler skips — data-mutation-point events still fire.

## Adding a new event

1. Add to `EVENTS` dict in `scripts/chain_heartbeat.py` with `expected_interval_s` and optional `pipeline`
2. Find the function that actually mutates data for this event
3. Call `event_beat("event_name")` at that function, not at its scheduler
4. Add to this mapping

## Alert-only events (no expected interval)

| Event | Trigger | Notes |
|---|---|---|
| `cron_job_died` | `scripts/cron_maintenance.py` | When a cron job fails consecutively |
| `external_service_down` | `scripts/chain_heartbeat.py` `ping_all_external()` | Auto-detected on ping |
