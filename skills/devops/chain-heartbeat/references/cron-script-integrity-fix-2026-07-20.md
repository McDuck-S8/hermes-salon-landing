# Cron Script Integrity Check Fix (2026-07-20)

## Problem
`scripts/test_cron_scripts_exist.py` was flagging scripts as "MISSING" when they had command-line arguments in the `script` field:
- `pinterest_image_gen.py --all --count 1`
- `telegram_poster.py cycle`

The check was looking for the full string as a filename, which doesn't exist.

## Fix
Modified `verify_cron_scripts()` to extract just the script filename (first token before space):

```python
# Extract just the script filename (first token before space)
script_name = script.split()[0]
script_path = SCRIPTS_DIR / script_name
if script_path.exists():
    result["ok"] += 1
else:
    result["missing"].append(script)
    result["all_ok"] = False
```

## Files Changed
- `scripts/test_cron_scripts_exist.py` - Added `.split()[0]` to extract script name

## Result
```bash
$ python scripts/test_cron_scripts_exist.py
[OK] All 45 cron-referenced scripts exist on disk
```

## Health Check Impact
`scripts/health_check.py` imports this module, so it now also passes the "cron scripts integrity" check (9/11 OK instead of 8/11).

## Pattern for Future
When cron jobs have script + args in one field, always split on space to get the actual filename.