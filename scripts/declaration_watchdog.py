#!/usr/bin/env python3
"""
Declaration Watchdog — Checks compliance with DECLARATION.md every N seconds.
Does NOT check if processes are alive — checks if BEHAVIOR matches Declaration.
"""

import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timezone

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
LOGS_DIR = HERMES_HOME / "logs"
WATCHDOG_LOG = LOGS_DIR / "declaration_watchdog.log"

sys.path.insert(0, str(HERMES_HOME / "scripts"))
from session_boot import (
    load_declaration, gather_reality, check_compliance, execute_repair
)


def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [WATCHDOG] {msg}"
    print(line)
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        with open(WATCHDOG_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def run_check_cycle() -> Dict:
    """One compliance check cycle."""
    log("Running compliance check...")
    
    declaration = load_declaration()
    reality = gather_reality()
    violations = check_compliance(declaration, reality)
    
    if violations:
        log(f"  ⚠ {len(violations)} violations:")
        for v in violations:
            log(f"    [{v['severity'].upper()}] {v['violation']} → repair: {v['repair']}")
        
        # Execute repairs
        for v in violations:
            execute_repair(v["repair"], reality, declaration)
    else:
        log("  ✅ Compliant")
    
    return {
        "violations": len(violations),
        "reality": reality,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def run_daemon(interval_seconds: int = 300):
    """Run watchdog as daemon."""
    log(f"Declaration Watchdog started (interval: {interval_seconds}s)")
    
    # Initial check
    run_check_cycle()
    
    while True:
        time.sleep(interval_seconds)
        try:
            run_check_cycle()
        except Exception as e:
            log(f"Check cycle error: {e}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Declaration Watchdog")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--interval", type=int, default=300, help="Interval in seconds")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    args = parser.parse_args()
    
    if args.once or not args.daemon:
        result = run_check_cycle()
        print(json.dumps(result, indent=2, default=str))
    else:
        run_daemon(args.interval)


if __name__ == "__main__":
    main()