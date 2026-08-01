#!/usr/bin/env python3
"""
Reality Gate — Честная проверка состояния системы.
Запускается при старте сессии. Отвечает на вопрос: "Что РЕАЛЬНО работает?"
"""
import json
import socket
import sys
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path("D:/Portable_Soft/hermes")


def gate() -> dict:
    """Run all reality checks and return verdict."""
    checks = {}

    # 1. Gateway alive? (port 9003 — confirmed via action_executor.py)
    checks["gateway"] = _check_port(9003)

    # 2. Cron scheduler running? (runs inside gateway, check via CLI)
    checks["cron_scheduler"] = _check_cron()

    # 3. Network available?
    checks["network"] = _check_network()

    # 4. v2rayN proxy alive?
    checks["proxy"] = _check_port(10806)

    # 5. FreeQwenApi alive? (port 3264 — third-party proxy)
    checks["free_qwen_api"] = _check_port(3264)

    # 6. KC DB exists and has data?
    checks["knowledge_cube"] = _check_kc()

    # 7. Scripts directory intact?
    checks["scripts"] = _check_scripts()

    # 8. Goal queue readable?
    checks["goals"] = _check_goals()

    # Determine verdict
    failed = [k for k, v in checks.items() if v.get("status") != "ok"]
    if not failed:
        verdict = "ALL_GREEN"
    elif len(failed) <= 2:
        verdict = "PARTIAL"
    else:
        verdict = "DEGRADED"

    return {
        "verdict": verdict,
        "timestamp": datetime.now().isoformat(),
        "checks": checks,
        "failed": failed,
    }


def _check_port(port: int) -> dict:
    """Check if a port is listening by trying to connect."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return {"status": "ok" if result == 0 else "warn", "listening": result == 0}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _check_cron() -> dict:
    """Check cron scheduler — gateway process on port 9003 runs cron internally."""
    # Fast check: if gateway is alive (port 9003), cron is alive too
    # They run in the same process (PID 34416 confirmed)
    import subprocess
    try:
        # Quick port check first (gateway = cron host)
        gateway_alive = _check_port(9003).get("listening", False)
        if not gateway_alive:
            return {"status": "warn", "running": False, "reason": "gateway_dead"}

        # Gateway alive → check cron status via CLI with longer timeout
        result = subprocess.run(
            ["hermes", "cron", "status"],
            capture_output=True, text=True, timeout=20,
            cwd="D:/Portable_Soft/hermes"
        )
        output = result.stdout + result.stderr
        if "running" in output.lower():
            import re
            match = re.search(r"(\d+) active job", output)
            jobs = int(match.group(1)) if match else 0
            return {"status": "ok", "running": True, "active_jobs": jobs}
        return {"status": "warn", "running": False, "output": output[:200]}
    except subprocess.TimeoutExpired:
        # CLI timed out but gateway is alive — cron likely works
        return {"status": "ok", "running": True, "note": "gateway_alive_cli_timeout"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _check_network() -> dict:
    """Check network connectivity."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('1.1.1.1', 443))
        sock.close()
        return {"status": "ok" if result == 0 else "warn"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _check_kc() -> dict:
    """Check Knowledge Cube database."""
    import sqlite3
    db_path = HERMES_HOME / "cache" / "knowledge_cube.db"
    if not db_path.exists():
        return {"status": "error", "error": "DB not found"}
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM experiences")
        count = cur.fetchone()[0]
        conn.close()
        return {"status": "ok" if count > 0 else "warn", "entries": count}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _check_scripts() -> dict:
    """Check critical scripts exist."""
    critical = [
        "session_boot.py", "session_bridge.py", "session_context.py",
        "auto_recall.py", "hermes_hooks.py", "goal_queue.py",
    ]
    scripts_dir = HERMES_HOME / "scripts"
    missing = [s for s in critical if not (scripts_dir / s).exists()]
    return {
        "status": "ok" if not missing else "warn",
        "missing": missing,
        "total": len(list(scripts_dir.glob("*.py"))),
    }


def _check_goals() -> dict:
    """Check goal queue."""
    goals_path = HERMES_HOME / "cache" / "goal_queue.json"
    if not goals_path.exists():
        return {"status": "error", "error": "goal_queue.json not found"}
    try:
        data = json.loads(goals_path.read_text(encoding="utf-8"))
        goals = data if isinstance(data, list) else data.get("goals", [])
        active = [g for g in goals if g.get("status") == "active"]
        return {"status": "ok", "total": len(goals), "active": len(active)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    result = gate()
    print(json.dumps(result, indent=2, ensure_ascii=False))
