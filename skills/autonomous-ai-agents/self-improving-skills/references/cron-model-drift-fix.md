# Cron Job Model Drift Fix

## Problem
The `self-improve-skills` cron job (job ID: `6702b8f1b014`, daily 03:00) fails with:
```
RuntimeError: Skipped to prevent unintended spend: global inference config drifted 
since this job was created (model 'nemotron-3-ultra-free' -> 'deepseek-v4-flash-free')
```

## Root Cause
The cron job was created with model `nemotron-3-ultra-free` but the global config now uses `deepseek-v4-flash-free`. The job is unpinned, so Hermes refuses to run it on the drifted config.

## Fix
Pin the cron job to the current model explicitly:

```bash
# From Hermes root
hermes cronjob action=update job_id=6702b8f1b014 provider=opencode-zen model=deepseek-v4-flash-free
```

Or via terminal directly:
```bash
cd /d/Portable_Soft/hermes
python -c "
import json
with open('cron/jobs.json') as f:
    jobs = json.load(f)
for job in jobs['jobs']:
    if job['id'] == '6702b8f1b014':
        job['provider'] = 'opencode-zen'
        job['model'] = 'deepseek-v4-flash-free'
        job['provider_snapshot'] = 'opencode-zen'
        job['model_snapshot'] = 'deepseek-v4-flash-free'
        break
with open('cron/jobs.json', 'w') as f:
    json.dump(jobs, f, indent=2)
print('Updated')
"
```

## Verification
After fix, next scheduled run (03:00) should execute successfully. Check `cron/output/6702b8f1b014/` for new log files.

## Note
This is an operational/maintenance issue, not a skill defect. The self-improvement pipeline itself works correctly (100% pass rate, proper auto-revert on no-improvement).