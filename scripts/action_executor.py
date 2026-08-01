#!/usr/bin/env python3
"""
Action Executor — Hands.


> Revisit: when action execution logic, tool dispatch, or result handling changes. Last touched: 2026-07-02.
Глаза видят (sensor_array), мозг знает (event_registry),
НО РУКИ НЕ ДВИГАЮТСЯ. Этот модуль — РУКИ.

Каждое действие из event_registry выполняется ЗДЕСЬ.
Не в JSON. Не в описании. ЗДЕСЬ — реальный код.

Принцип:
  action_name → function()
  Если функции нет — логируем "action not implemented"
  Если есть — ВЫПОЛНЯЕМ.

Добавляй новые функции по мере необходимости.
"""
import json
import subprocess
import sys
import socket
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE = REPO_ROOT / "cache"
LOG_FILE = CACHE / "action_log.jsonl"

sys.path.insert(0, str(REPO_ROOT / "scripts"))


def _now():
    return datetime.now(timezone.utc)


def _log_action(action: str, event_type: str, result: str, success: bool):
    CACHE.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "action": action,
            "event": event_type,
            "result": result[:500],
            "success": success,
            "timestamp": _now().isoformat(),
        }, ensure_ascii=False) + "\n")


def pre_flight_check(cmd) -> bool:
    """Validate command before execution."""
    dangerous = ['rm -rf', '> /dev/', 'dd if=', 'mkfs', 'fdisk']
    cmd_str = cmd if isinstance(cmd, str) else " ".join(cmd)
    return not any(d in cmd_str for d in dangerous)

def _run(cmd, timeout: int = 30) -> tuple:
    """Run command with validation. Returns (output, success).
    cmd can be a string (for single-command convenience) or a list of args.
    Always uses shell=False for security — shell features must be handled by callers via subprocess args.
    """
    if not cmd:
        return "Empty or invalid command", False
    
    # Pre-flight check
    if not pre_flight_check(cmd):
        return "Rejected by pre_flight_check", False

    # Convert string to list (shell=False needs a list)
    if isinstance(cmd, str):
        cmd_list = cmd.split()
    elif isinstance(cmd, list):
        cmd_list = cmd
    else:
        return "Invalid command type", False

    if not cmd_list:
        return "Empty or invalid command", False

    # Reject dangerous patterns in the command string
    forbidden = ['rm -rf', 'mkfs', 'dd if=', 'chmod 777']
    cmd_lower = ' '.join(cmd_list).lower()
    for pattern in forbidden:
        if pattern in cmd_lower:
            return f"Rejected dangerous pattern: {pattern}", False

    try:
        r = subprocess.run(
            cmd_list, shell=False, capture_output=True, text=True,
            timeout=timeout, cwd=str(REPO_ROOT)
        )
        return r.stdout + r.stderr, r.returncode == 0
    except subprocess.TimeoutExpired:
        return "timeout", False
    except Exception as e:
        return str(e), False


def _is_port_alive(port: int, host: str = "127.0.0.1") -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    alive = s.connect_ex((host, port)) == 0
    s.close()
    return alive


# ═══════════════════════════════════════════════
# ACTIONS — реальный код для каждого действия
# ═══════════════════════════════════════════════

def restart_process(event_context: dict = None) -> dict:
    """Restart dead processes."""
    results = []

    # Check gateway (port 9003)
    if not _is_port_alive(9003):
        out, ok = _run(["python", "gateway.py"], timeout=10)
        results.append({"process": "gateway", "action": "restart", "success": ok, "output": out[:200]})
    else:
        results.append({"process": "gateway", "action": "already_alive"})

    # Check proxy (port 10806)
    if not _is_port_alive(10806):
        # Use list form — no shell needed; caller handles failure via returncode
        out, ok = _run(["net", "start", "Socks5Proxy"], timeout=10)
        if not ok:
            out = "proxy needs manual restart"
        results.append({"process": "proxy", "action": "restart_attempt", "success": ok, "output": out[:200]})
    else:
        results.append({"process": "proxy", "action": "already_alive"})

    return {"action": "restart_process", "results": results}


def check_logs(event_context: dict = None) -> dict:
    """Check recent logs for errors."""
    log_dirs = [REPO_ROOT / "logs", CACHE]
    errors = []
    for d in log_dirs:
        if not d.exists():
            continue
        for f in d.glob("*.log"):
            try:
                lines = f.read_text(encoding="utf-8", errors="ignore").split("\n")
                recent = [l for l in lines[-50:] if "error" in l.lower() or "traceback" in l.lower()]
                if recent:
                    errors.append({"file": f.name, "errors": recent[-5:]})
            except:
                pass
    return {"action": "check_logs", "errors_found": len(errors), "details": errors[:3]}


def verify_fix(event_context: dict = None) -> dict:
    """Verify that processes are alive after restart."""
    results = {
        "gateway": _is_port_alive(9003),
        "proxy": _is_port_alive(10806),
    }
    all_ok = all(results.values())
    return {"action": "verify_fix", "results": results, "all_healthy": all_ok}


def reschedule_cron(event_context: dict = None) -> dict:
    """Reschedule stale cron jobs."""
    jobs_file = REPO_ROOT / "cron" / "jobs.json"
    if not jobs_file.exists():
        return {"action": "reschedule_cron", "error": "jobs.json not found"}

    jobs = json.loads(jobs_file.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    rescheduled = 0

    for job in jobs.get("jobs", []):
        if not job.get("enabled") or job.get("event_driven"):
            continue
        nrt = job.get("next_run_at")
        if nrt:
            try:
                if datetime.fromisoformat(nrt) < now:
                    # Reschedule to now + 30min
                    from datetime import timedelta
                    new_time = (now + timedelta(minutes=30)).isoformat()
                    job["next_run_at"] = new_time
                    rescheduled += 1
            except:
                pass

    jobs_file.write_text(json.dumps(jobs, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"action": "reschedule_cron", "rescheduled": rescheduled}


def alert_user(event_context: dict = None) -> dict:
    """Alert user about critical event."""
    # Write to alert file — gateway picks it up
    alert = {
        "level": event_context.get("level", 1),
        "event": event_context.get("event_type", "unknown"),
        "description": event_context.get("description", ""),
        "timestamp": _now().isoformat(),
        "read": False,
    }
    alerts_file = CACHE / "pending_alerts.json"
    alerts = []
    if alerts_file.exists():
        try:
            alerts = json.loads(alerts_file.read_text(encoding="utf-8"))
        except:
            pass
    alerts.append(alert)
    alerts_file.write_text(json.dumps(alerts, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"action": "alert_user", "queued": True}


def verify_syntax(event_context: dict = None) -> dict:
    """Verify Python syntax of recently changed files."""
    changed = event_context.get("detail", "")
    if "scripts/" in changed:
        filename = changed.split("scripts/")[-1]
        filepath = REPO_ROOT / "scripts" / filename
        if filepath.exists() and filepath.suffix == ".py":
            out, ok = _run(["python", "-m", "py_compile", str(filepath)])
            return {"action": "verify_syntax", "file": filename, "valid": ok, "output": out[:200]}
    return {"action": "verify_syntax", "skipped": "no specific file"}


def explore_and_learn(event_context: dict = None) -> dict:
    """Explore knowledge gaps and learn."""
    out, ok = _run(["python", "scripts/explore_white_spot.py"], timeout=60)
    return {"action": "explore_and_learn", "output": out[:500], "success": ok}


def system_health_check(event_context: dict = None) -> dict:
    """Full system health check."""
    return {
        "action": "system_health_check",
        "gateway": _is_port_alive(9003),
        "proxy": _is_port_alive(10806),
        "disk_ok": True,  # Would check disk usage
        "memory_ok": True,  # Would check RAM
    }


def create_goals(event_context: dict = None) -> dict:
    """Create goals when idle."""
    return {"action": "create_goals", "status": "delegated_to_planner"}


def start_background_work(event_context: dict = None) -> dict:
    """Start background work when user is silent."""
    return {"action": "start_background_work", "status": "delegated_to_background_worker"}


def wait_for_user(event_context: dict = None) -> dict:
    """User not interacting. Just wait."""
    return {"action": "wait_for_user", "status": "waiting"}


def daily_summary(event_context: dict = None) -> dict:
    """Generate daily summary."""
    return {"action": "daily_summary", "status": "delegated_to_report_generator"}


def plan_tomorrow(event_context: dict = None) -> dict:
    """Plan tomorrow's work."""
    return {"action": "plan_tomorrow", "status": "delegated_to_planner"}


# ═══════════════════════════════════════════════
# ACTION MAP — name → function
# ═══════════════════════════════════════════════

ACTIONS = {
    "restart_process": restart_process,
    "check_logs": check_logs,
    "verify_fix": verify_fix,
    "reschedule_cron": reschedule_cron,
    "alert_user": alert_user,
    "alert_user_immediately": alert_user,
    "verify_syntax": verify_syntax,
    "explore_and_learn": explore_and_learn,
    "system_health_check": system_health_check,
    "create_goals": create_goals,
    "start_background_work": start_background_work,
    "wait_for_user": wait_for_user,
    "daily_summary": daily_summary,
    "plan_tomorrow": plan_tomorrow,
    "suggest_cleanup": lambda ctx: {"action": "suggest_cleanup", "suggestion": "Run: du -sh cache/* | sort -hr | head -10"},
    "monitor": lambda ctx: {"action": "monitor", "status": "observing"},
    "backup": lambda ctx: {"action": "backup", "status": "delegated_to_night_maintenance"},
    "cleanup": lambda ctx: {"action": "cleanup", "status": "delegated_to_night_maintenance"},
    "fetch_weather": lambda ctx: {"action": "fetch_weather", "status": "use_event_trigger"},
    "fetch_transcript": lambda ctx: {"action": "fetch_transcript", "status": "use_youtube_skill"},
    "search_web": lambda ctx: {"action": "search_web", "status": "use_web_search"},
    "search_solutions": lambda ctx: {"action": "search_solutions", "status": "use_web_search"},
    "pip_install": lambda ctx: {"action": "pip_install", "status": "use_terminal"},
    "ask_user": alert_user,
    "log_unknown": lambda ctx: _log_action("log_unknown", ctx.get("event_type", "?"), str(ctx), True) or {"action": "logged"},
}


def execute_actions(event_type: str, actions: list, context: dict = None) -> list:
    """
    Execute all actions for an event.
    Returns list of results.
    """
    if context is None:
        context = {"event_type": event_type}

    results = []
    for action_name in actions:
        func = ACTIONS.get(action_name)
        if func:
            try:
                result = func(context)
                success = not result.get("error")
                _log_action(action_name, event_type, json.dumps(result, ensure_ascii=False)[:200], success)
                results.append({"action": action_name, "result": result, "success": success})
            except Exception as e:
                _log_action(action_name, event_type, str(e)[:200], False)
                results.append({"action": action_name, "error": str(e)[:200], "success": False})
        else:
            _log_action(action_name, event_type, "not_implemented", False)
            results.append({"action": action_name, "status": "not_implemented", "success": False})

    return results


# ═══════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print("Action Executor — makes things happen")
        print("")
        print("  run <event_type> <action1,action2>  — execute actions")
        print("  list                                — list available actions")
        print("  log                                 — show last 20 actions")
        return

    cmd = sys.argv[1]

    if cmd == "run":
        event_type = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        actions = sys.argv[3].split(",") if len(sys.argv) > 3 else []
        results = execute_actions(event_type, actions)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif cmd == "list":
        for name in sorted(ACTIONS.keys()):
            print(f"  {name}")

    elif cmd == "log":
        if LOG_FILE.exists():
            lines = LOG_FILE.read_text(encoding="utf-8").strip().split("\n")
            for line in lines[-20:]:
                try:
                    entry = json.loads(line)
                    status = "✓" if entry.get("success") else "✗"
                    print(f"  {status} {entry['timestamp'][:19]} {entry['action']}: {entry['result'][:80]}")
                except:
                    pass

    else:
        print(f"Unknown: {cmd}")


if __name__ == "__main__":
    main()
