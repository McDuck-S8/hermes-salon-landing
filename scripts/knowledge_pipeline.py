#!/usr/bin/env python3
"""
RSS+YouTube → Knowledge Filter → Knowledge Cube Pipeline
Runs: rss_monitor.py → youtube_watch.py → knowledge_filter
Schedule: every 2 hours via cron
"""
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

HERMES = Path("D:/Portable_Soft/hermes")
PYTHON = str(HERMES / ".venv" / "Scripts" / "python.exe")

def run_step(name, cmd, timeout=120):
    print(f"\n{'='*50}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Running: {name}")
    print(f"{'='*50}")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(HERMES))
        if r.stdout:
            # Print last 10 lines of output
            lines = r.stdout.strip().split('\n')
            for line in lines[-10:]:
                print(f"  {line}")
        if r.returncode != 0 and r.stderr:
            print(f"  WARN: {r.stderr[-200:]}")
        return r.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT after {timeout}s")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def main():
    print(f"=== PIPELINE START {datetime.now().isoformat()} ===")
    
    # Step 1: RSS Monitor
    ok1 = run_step("RSS Monitor", [PYTHON, str(HERMES / "scripts" / "rss_monitor.py")], timeout=180)
    
    # Step 2: YouTube Watch
    ok2 = run_step("YouTube Watch", [PYTHON, str(HERMES / "scripts" / "youtube_watch.py")], timeout=120)
    
    # Step 3: Knowledge Filter
    filter_script = str(HERMES / "skills" / "automation" / "knowledge-filter" / "scripts" / "filter.py")
    ok3 = run_step("Knowledge Filter", [PYTHON, filter_script, "--test-rss", "--limit", "50"], timeout=120)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"PIPELINE DONE: RSS={'OK' if ok1 else 'FAIL'} YT={'OK' if ok2 else 'FAIL'} Filter={'OK' if ok3 else 'FAIL'}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
