# Cron Script Integrity Watchdog Pattern

After fixing broken cron scripts, add a permanent monitor so re-breakage is detected within minutes.

## The Pattern

1. Create `scripts/test_cron_scripts_exist.py` — reads `cron/jobs.json`, collects all `script` fields, checks each file on disk. Exit 0 = all ok, 1 = missing.
2. Integrate into `health_check.py` as check #N (e.g. "cron scripts integrity").
3. Create a `no_agent=True` cron job running `test_cron_scripts_exist.py` every 15 min.
4. Update `auto-wake` skill (step 2) to run the check at session start.

## Implementation Reference

See `scripts/test_cron_scripts_exist.py` in the Hermes repo. Design:
- `verify_cron_scripts(json_report=False)` function — importable from health_check.py
- Standalone `if __name__` for cron use (`no_agent=True`)
- Reports `[OK] All N cron-referenced scripts exist` on success
- Silent on success (no delivery spam), alerts on failure (exit 1)
