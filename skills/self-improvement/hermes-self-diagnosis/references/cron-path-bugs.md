# Cron Job Script Path Bugs — Reference

Recurring issue: cron jobs fail with "Script not found" because the
`script` field in `cron/jobs.json` contains arguments or path prefixes
that the scheduler treats as part of the filename.

## Bug Variants

### Variant 1: Arguments baked into script field
```json
{ "script": "hermes_health.py --watch" }
{ "script": "jarvis_security_monitor.py --warnings-only" }
{ "script": "event_daemon.py beat" }
```
Scheduler resolves `D:\...\scripts\hermes_health.py --watch` → not found.

**Fix options:**
- A) Edit `cron/jobs.json`, strip arguments from script field
- B) Create wrapper script that calls original with args
- C) `cronjob(action="update")` — NOTE: only updates `prompt`, NOT `script`

### Variant 2: Double path prefix
```json
{ "script": "scripts/event_daemon.py beat" }
```
Scheduler prepends `scripts/` → `scripts/scripts/event_daemon.py` → not found.

**Fix:** Edit jobs.json → `"script": "event_daemon.py"`

### Variant 3: Stale last_error
`last_error` shows `scripts/scripts/` even after fix. This is cached from
previous run. Verify by running the job again.

## Detection Script

```python
import json, os
with open('cron/jobs.json') as f:
    data = json.load(f)
for j in data['jobs']:
    if j.get('enabled') and j.get('script'):
        script_file = j['script'].split()[0]
        full = os.path.join('scripts', script_file)
        if not os.path.exists(full):
            print(f"BROKEN: {j['name']}: {j['script']}")
```

## Key Constraint

`cronjob(action="update")` cannot update the `script` field.
Must edit `cron/jobs.json` directly or create a wrapper script.
