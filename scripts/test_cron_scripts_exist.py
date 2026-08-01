#!/usr/bin/env python3
"""Verify every script referenced in cron/jobs.json exists on disk.

Runs at startup and periodically. Exits 0 if all OK, 1 if any missing.
Integrates with health_check.py (importable) and standalone (cron).
"""
import json, sys
from pathlib import Path

HERMES_HOME = Path(__file__).resolve().parent.parent
CRON_JOBS = HERMES_HOME / "cron" / "jobs.json"
SCRIPTS_DIR = HERMES_HOME / "scripts"


def verify_cron_scripts(json_report: bool = False) -> dict:
    """
    Scan cron/jobs.json, check every referenced script exists on disk.
    
    Returns dict with:
      - total: number of scripts referenced
      - ok: number found
      - missing: list of missing script filenames
      - all_ok: boolean
    """
    result = {"total": 0, "ok": 0, "missing": [], "all_ok": True}
    
    if not CRON_JOBS.exists():
        result["error"] = f"cron/jobs.json not found at {CRON_JOBS}"
        result["all_ok"] = False
        return result
    
    try:
        data = json.loads(CRON_JOBS.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        result["error"] = f"Failed to read {CRON_JOBS}: {e}"
        result["all_ok"] = False
        return result
    
    jobs = data.get("jobs", [])
    seen = set()
    
    for job in jobs:
        script = job.get("script")
        if not script or script in seen:
            continue
        seen.add(script)
        result["total"] += 1
        
        # Extract just the script filename (first token before space)
        script_name = script.split()[0]
        script_path = SCRIPTS_DIR / script_name
        if script_path.exists():
            result["ok"] += 1
        else:
            result["missing"].append(script)
            result["all_ok"] = False
    
    if json_report:
        return result
    
    # Human-readable output
    if result["all_ok"]:
        print(f"[OK] All {result['total']} cron-referenced scripts exist on disk")
    else:
        print(f"[FAIL] {len(result['missing'])} script(s) referenced in cron/jobs.json are MISSING:")
        for s in result["missing"]:
            print(f"       - {s}")
        print(f"       ({result['ok']}/{result['total']} found)")
    
    return result


if __name__ == "__main__":
    report_json = "--json" in sys.argv
    r = verify_cron_scripts(json_report=report_json)
    if report_json:
        import json as j
        print(j.dumps(r, indent=2))
    sys.exit(0 if r["all_ok"] else 1)
