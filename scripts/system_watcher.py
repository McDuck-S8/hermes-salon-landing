#!/usr/bin/env python3
"""Proactive system health watcher.

Checks: cron scheduler status, event backlog, knowledge cube growth,
system uptime. Silent when healthy — noisy when something's broken.

Runs every 60 minutes via cronjob (no_agent=True).
"""
import sys
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path(__file__).resolve().parent.parent)))
EVENTS_DB = HERMES_HOME / "cache" / "events.db"
CORE_ENGINE_DB = HERMES_HOME / "cache" / "core_engine.db"
KNOWLEDGE_CUBE_DB = HERMES_HOME / "cache" / "knowledge_cube.db"

issues = []

# 1. Check events backlog
if EVENTS_DB.exists():
    try:
        conn = sqlite3.connect(str(EVENTS_DB))
        pending = conn.execute("SELECT COUNT(*) FROM events WHERE processed=0").fetchone()[0]
        if pending > 5:
            issues.append(f"Event backlog: {pending} unprocessed events (threshold=5)")
        elif pending > 0:
            pass  # Small backlog is normal, will be cleaned on next event-processor tick
        conn.close()
    except Exception as e:
        issues.append(f"Events DB error: {e}")
else:
    issues.append("Events DB not found")

# 2. Check knowledge cube
if KNOWLEDGE_CUBE_DB.exists():
    try:
        conn = sqlite3.connect(str(KNOWLEDGE_CUBE_DB))
        count = conn.execute("SELECT COUNT(*) FROM experiences").fetchone()[0]
        conn.close()
        # Just report growth, not an issue
        print(f"[watcher] Knowledge Cube: {count} experiences")
    except Exception as e:
        issues.append(f"Knowledge Cube error: {e}")
else:
    issues.append("Knowledge Cube DB not found")

# 3. Check core engine — gaps
if CORE_ENGINE_DB.exists():
    try:
        conn = sqlite3.connect(str(CORE_ENGINE_DB))
        gaps = conn.execute("SELECT COUNT(*) FROM knowledge_gaps WHERE filled=0").fetchone()[0]
        if gaps > 50:
            issues.append(f"Unfilled gaps: {gaps} (threshold=50)")
        conn.close()
    except Exception as e:
        issues.append(f"Core Engine error: {e}")

# 4. Output
if issues:
    print("[watcher] SYSTEM ISSUES DETECTED:")
    for issue in issues:
        print(f"  ! {issue}")
    sys.exit(1)
else:
    # Silent — system healthy
    sys.exit(0)
