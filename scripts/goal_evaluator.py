#!/usr/bin/env python3
"""
Goal Evaluator — daily cron script that manages the goal queue.


> Revisit: when goal evaluation logic, urgency/impact scoring, or state collection changes. Last touched: 2026-07-02.
Runs daily at 04:15. Evaluates system state, creates new goals,
updates progress on existing goals, archives completed ones.

Usage:
    python scripts/goal_evaluator.py
"""
import json
import sys
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
sys.path.insert(0, str(HERMES_HOME / "scripts"))

from goal_queue import evaluate_goals, archive_completed_goals, get_active_goals


def safe_print(msg):
    """Print that won't crash on Windows cp1251 encoding."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode())


def collect_state() -> dict:
    """Quick state snapshot for goal evaluation.
    
    2026-06-22: Now includes reality gate output for outcome verification.
    """
    state = {}
    
    # KC stats
    try:
        import sqlite3
        kc_db = CACHE_DIR / "knowledge_cube.db"
        if kc_db.exists():
            conn = sqlite3.connect(str(kc_db))
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM experiences")
            entries = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM experiences WHERE is_white_spot=1")
            white_spots = cur.fetchone()[0]
            conn.close()
            state["knowledge_cube"] = {"entries": entries, "white_spots": white_spots}
    except Exception:
        state["knowledge_cube"] = {}

    # Cron health
    try:
        jobs_file = HERMES_HOME / "cron" / "jobs.json"
        if jobs_file.exists():
            data = json.loads(jobs_file.read_text(encoding="utf-8"))
            jobs = data.get("jobs", [])
            errors = sum(1 for j in jobs if j.get("last_status") == "error")
            state["cron_health"] = {
                "jobs_total": len(jobs),
                "jobs_with_errors": errors,
            }
    except Exception:
        state["cron_health"] = {}

    # Reality Gate — actual system state (the TRUTH)
    try:
        import importlib.util
        gate_path = HERMES_HOME / "scripts" / "reality_gate.py"
        spec = importlib.util.spec_from_file_location("reality_gate", gate_path)
        gate_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate_mod)
        gate_result = gate_mod.gate()
        state["reality_gate"] = gate_result
    except Exception as e:
        state["reality_gate"] = {"verdict": f"ERROR: {e}", "checks": {}}

    # Disk
    import shutil
    try:
        disk = shutil.disk_usage(str(HERMES_HOME.parent))
        state["resources"] = {"disk_free_gb": round(disk.free / (1023**3), 2)}
    except Exception:
        state["resources"] = {}

    return state


def main():
    print("=== Goal Evaluator ===")
    print(f"Time: {datetime.now().isoformat()}")

    state = collect_state()

    # Evaluate and create new goals
    new_goals = evaluate_goals(state)
    if new_goals:
        print(f"Created {len(new_goals)} new goals: {new_goals}")
    else:
        safe_print("No new goals needed.")

    # Archive completed goals
    archived = archive_completed_goals()
    if archived:
        safe_print(f"Archived {archived} completed goals")

    # Report active goals
    active = get_active_goals()
    if active:
        safe_print(f"\nActive goals ({len(active)}):")
        for g in active:
            progress = g.get("progress", 0) * 100
            safe_print(f"  [{g['id']}] P{g.get('priority', '?')} | {progress:.0f}% | {g['title']}")
    else:
        safe_print("No active goals.")


if __name__ == "__main__":
    main()
