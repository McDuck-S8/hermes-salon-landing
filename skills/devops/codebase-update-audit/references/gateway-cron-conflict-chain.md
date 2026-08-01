# Gateway Crash from Cron Module Conflict

## Symptom

Gateway exits seconds after starting with no visible error in the startup logs:

```
┌─────────────────────────────────────────────────────────┐
│           ⚕ Hermes Gateway Starting...                 │
├─────────────────────────────────────────────────────────┤
│  Messaging platforms + cron scheduler                    │
│  Press Ctrl+C to stop                                   │
└─────────────────────────────────────────────────────────┘
<process exits silently after 1-2 seconds>
```

The `errors.log` or `gateway.log` may show nothing useful. The actual traceback appears in the **process stderr** (background task output), not in log files.

## Root Cause

`cron/scheduler.py` contains unresolved git conflict markers (`<<<<<<<` / `=======` / `>>>>>>>`), causing a SyntaxError when the gateway's `_start_cron_ticker` thread imports `from cron.scheduler import tick`.

The import chain:
```
gateway/run.py → _start_cron_ticker()
  → cron/__init__.py (line 29: "from cron.scheduler import tick")
    → cron/scheduler.py line 1: "<<<<<<< Updated upstream" ← SyntaxError
```

This error happens in a background thread (`cron-ticker`), so it doesn't propagate to the main asyncio loop. The gateway exits with code 1.

## Diagnosis

### Check for conflict markers
```bash
grep -rn '<<<<<<<\|\|=======\|\|>>>>>>>' --include='*.py' hermes-agent/cron/ 2>/dev/null
git status --short | grep 'UU'           # Unmerged paths
```

### Check if cron module loads
```bash
python -c "from cron.scheduler import tick; print('OK')" 2>&1
# If SyntaxError → conflict markers present
```

### Check gateway-exit-diag.log
```bash
tail -5 logs/gateway-exit-diag.log        # Last gateway exit reason
```

## Fix

1. Resolve the conflict (keep upstream HEAD version for stale stash conflicts)
2. `git add path/to/file.py && git status` — verify UU cleared
3. Kill ALL stale `hermes` processes before restarting:
   ```bash
   ps aux | grep hermes    # Find PIDs
   kill -9 <PID1> <PID2>   # Kill all
   ```
4. Start fresh gateway:
   ```bash
   hermes gateway run &
   sleep 5 && kill %1      # Smoke test after 5s
   ```
5. Verify in gateway.log:
   ```bash
   tail -5 logs/gateway.log | grep -i "connected"
   # Should see: ✓ telegram connected
   ```

## Key Insight

A conflict marker in ANY file imported by the gateway's cron-ticker thread will silently kill the gateway. This includes:
- `cron/scheduler.py`
- `cron/jobs.py` (imported by scheduler)
- `cron/__init__.py`
- Any module transitively imported by these files

After fixing the file, old gateway processes that already imported the broken module **must be killed** — Python caches compiled modules in memory. The new process reads the fixed file from disk, but if the old process still holds the Telegram token lock, the new one fails with "Telegram bot token already in use".
