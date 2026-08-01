"""Health check — verifies all critical files and processes exist.
Run at startup or periodically to catch issues early.
"""

# Revisit: when health checks, critical files, or process requirements change. Last touched: 2026-07-02.
import json, os, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE = HERMES_HOME / "cache"
SCRIPTS_DIR = HERMES_HOME / "scripts"

checks = []

def check(name, ok, detail=""):
    status = "[OK]" if ok else "[FAIL]"
    checks.append({"name": name, "ok": ok, "detail": detail})
    print(f"  {status} {name}" + (f" - {detail}" if detail else ""))

# 1. MEMORY.md
check("MEMORY.md exists", (HERMES_HOME / "MEMORY.md").exists())

# 2. knowledge_cube.db
check("knowledge_cube.db", (CACHE / "knowledge_cube.db").exists())

# 3. goal_queue.json
check("goal_queue.json", (CACHE / "goal_queue.json").exists())

# 4. event_bus.json
check("event_bus.json", (CACHE / "event_bus.json").exists())

# 5. signal_daemon PID
pid_file = CACHE / "signal_daemon.pid"
daemon_alive = False
if pid_file.exists():
    try:
        pid = int(pid_file.read_text().strip())
        import psutil
        daemon_alive = psutil.pid_exists(pid)
    except:
        pass
check("signal_daemon alive", daemon_alive)

# 6. scanner_state.json
check("scanner_state.json", (CACHE / "scanner_state.json").exists())

# 7. knowledge_cube.db has data
try:
    import sqlite3
    conn = sqlite3.connect(str(CACHE / "knowledge_cube.db"))
    count = conn.execute("SELECT COUNT(*) FROM experiences").fetchone()[0]
    conn.close()
    check(f"knowledge_cube.db entries", count > 0, f"{count} entries")
except:
    check("knowledge_cube.db entries", False, "can't read")

# 8. bayesian_scorer_history
check("scorer_history.json", (CACHE / "scorer_history.json").exists())

# 9. memory_guard.py points to right path
try:
    mg = (HERMES_HOME / "scripts" / "memory_guard.py").read_text(encoding="utf-8")
    correct = 'MEMORY_FILE = HERMES_HOME / "MEMORY.md"' in mg
    check("memory_guard.py path", correct)
except:
    check("memory_guard.py path", False, "can't read")

# 10. event-heartbeat calls event_bus.py process
try:
    hb = (HERMES_HOME / "scripts" / "hermes_heartbeat.py").read_text(encoding="utf-8")
    calls_event_bus = "event_bus.py" in hb
    check("hermes_heartbeat -> event_bus", calls_event_bus)
except:
    check("hermes_heartbeat -> event_bus", False, "can't read")

# 11. cron scripts integrity
try:
    import sys
    sys.path.insert(0, str(SCRIPTS_DIR))
    from test_cron_scripts_exist import verify_cron_scripts
    result = verify_cron_scripts()
    check("cron scripts integrity", result["all_ok"],
          f"{result['ok']}/{result['total']} found" + (f", MISSING: {result['missing']}" if result["missing"] else ""))
except Exception as e:
    check("cron scripts integrity", False, f"can't verify: {e}")

# Summary
total = len(checks)
passed = sum(1 for c in checks if c["ok"])
failed = sum(1 for c in checks if not c["ok"])
print(f"\n  === HEALTH: {passed}/{total} OK, {failed} FAIL ===")
if failed == 0:
    print("  [OK] System healthy")
else:
    print(f"  [FAIL] {failed} issues found:")
    for c in checks:
        if not c["ok"]:
            print(f"    -> {c['name']}: {c['detail'] or 'FAIL'}")