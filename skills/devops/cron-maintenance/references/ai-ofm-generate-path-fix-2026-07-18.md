# AI OFM Generate Cron Job — Path Fix (2026-07-18)

## Issue
The cron job `ai-ofm-generate` (every 180m) failed with:
```
Script not found: D:\Portable_Soft\hermes\scripts\projects\ai-ofm-tribute\scripts\cron.sh
```

The job's `script` field was:
```json
"script": "projects/ai-ofm-tribute/scripts/cron.sh"
```

The cron runner resolves relative paths from `HERMES_HOME/scripts/`, so it looked for `scripts/projects/ai-ofm-tribute/scripts/cron.sh` which doesn't exist.

## Fix Applied
Changed the `script` field in `cron/jobs.json` to an absolute Windows path:
```json
"script": "D:/Portable_Soft/hermes/projects/ai-ofm-tribute/scripts/cron.sh"
```

This works because the cron runner executes absolute paths directly without prepending `scripts/`.

## Alternative Fixes (per skill)
1. **Wrapper script** — create `scripts/ai-ofm-generate.sh` that calls the project script
2. **Move script** — move `projects/ai-ofm-tribute/scripts/cron.sh` → `scripts/projects/ai-ofm-tribute/scripts/cron.sh`

## Verification
- Ran the generator manually: `python scripts/generate.py --count 5 --style realistic`
- Generated 2/5 images successfully (3 failed due to Pollinations.ai SSL timeouts)
- Config JSON is valid
- Next cron run will use the fixed absolute path