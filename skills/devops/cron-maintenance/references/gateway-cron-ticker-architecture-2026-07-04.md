# Gateway Cron Ticker Architecture — 2026-07-04

## How Cron Jobs Actually Run in Hermes

**There is NO standalone cron daemon.** Cron jobs run inside the Hermes gateway process.

## Architecture

```
hermes gateway (pythonw.exe, PID 3376)
    │
    ├── Main event loop (Telegram adapter, message handling)
    │
    └── Background thread: InProcessCronScheduler
          │
          ├── Ticker: every 60 seconds (configurable via TICKER_INTERVAL_SECONDS)
          │
          ├── On each tick:
          │    1. Load jobs from ~/.hermes/cron/jobs.json
          │    2. Check which jobs are due (next_run_at <= now)
          │    3. For each due job with no_agent: true:
          │           → subprocess.Popen([python, script_path], ...)
          │    4. For each due job with no_agent: false:
          │           → Spawn agent via delegate_task / ACP
          │    5. Update job state (last_run_at, last_status, next_run_at)
          │
          └── Heartbeat files (for status checking):
               - cron/ticker_heartbeat (updated every tick)
               - cron/ticker_last_success (updated only on successful tick)
```

## Key Files
| File | Role |
|------|------|
| `hermes-agent/cron/scheduler.py` | Core tick logic, job execution |
| `hermes-agent/cron/scheduler_provider.py` | `InProcessCronScheduler` provider |
| `hermes-agent/gateway/run.py` | Gateway startup, starts ticker via `_start_cron_ticker()` |
| `hermes-agent/cron/jobs.py` | Job storage, locking, next_run_at calculation |
| `hermes-agent/hermes_cli/cron.py` | CLI commands (`hermes cron list/create/pause/run/status`) |

## Cron Ticker Startup
```python
# In gateway/run.py → start_gateway()
# ...
from cron.scheduler_provider import InProcessCronScheduler
InProcessCronScheduler().start(stop_event, adapters=adapters, loop=loop, interval=60)
```

## Job Execution Flow (no_agent: true)
```python
# In scheduler.py → _run_job()
if job["no_agent"]:
    # Direct script execution
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        timeout=job.get("timeout", 120),
        cwd=HERMES_HOME,
        **windows_hide_flags  # CREATE_NO_WINDOW on Windows
    )
    # stdout/stderr captured, exit_code checked
```

## Critical Implications

1. **No gateway = no cron** — jobs won't fire automatically
2. **Gateway restart = ticker restart** — no missed ticks (next_run_at persists in jobs.json)
3. **Process isolation** — each job = separate Python subprocess (explains "window spam")
4. **Windows: CREATE_NO_WINDOW** — `windows_hide_flags` prevents console windows, but processes still appear in tasklist
5. **Heartbeat monitoring** — `hermes cron status` checks `ticker_heartbeat` freshness to detect stuck ticker

## Debugging Cron Issues

```bash
# Check if gateway is running (required for cron)
hermes cron status

# Check ticker heartbeat
cat ~/.hermes/cron/ticker_heartbeat

# Check job state
cat ~/.hermes/cron/jobs.json | jq '.jobs[] | {id, name, last_status, last_error, next_run_at}'

# Run a job manually (bypasses ticker)
hermes cron run <job_id>

# View job output
cat ~/.hermes/cron/output/<job_id>/*.md
```

## Common Pitfalls

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Jobs never fire | Gateway not running | `hermes gateway install` + `hermes gateway start` |
| Jobs fire but fail | Script error / missing deps | Run script manually, fix, verify |
| "Window spam" | Too many short-interval no_agent jobs | Increase intervals, pause, or use event-driven |
| Ticker stuck | Exception in tick loop | Check `ticker_last_success` age, restart gateway |
| Jobs run but no output | `deliver: local` (default) | Check `cron/output/<job_id>/` |