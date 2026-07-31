#!/usr/bin/env python3
"""
Bootstrap — Autonomous System Initialization
Запускается при старте системы: восстанавливает состояние, применяет фиксы, запускает кроны.
"""

import json
import os
import sys
import subprocess
import tarfile
import time
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
CACHE_DIR = HERMES_HOME / "cache"
BACKUP_FILE = HERMES_HOME / "system_state_backup.tar.gz"
SUGGESTIONS_FILE = CACHE_DIR / "improvement_suggestions.json"
APPLIED_FILE = CACHE_DIR / "applied_suggestions.json"


def log(msg: str) -> None:
    print(f"[{datetime.now().isoformat()}] {msg}")


def load_json(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def restore_backup() -> bool:
    """Распаковать последний бандл состояния."""
    if not BACKUP_FILE.exists():
        log(f"Backup not found: {BACKUP_FILE}")
        return False
    try:
        with tarfile.open(BACKUP_FILE, "r:gz") as tar:
            tar.extractall(HERMES_HOME, filter='data')
        log(f"Restored backup from {BACKUP_FILE}")
        return True
    except Exception as e:
        log(f"Failed to restore backup: {e}")
        return False


def verify_modules() -> bool:
    """Проверить, что все критичные модули на месте."""
    critical = [
        "scripts/action_executor.py",
        "scripts/chain_heartbeat.py",
        "scripts/kc_rag.py",
        "scripts/autonomous_agent.py",
        "scripts/proactive_doer.py",
        "scripts/proactive_executor.py",
        "scripts/self_healing_monitor.py",
        "scripts/self_improvement_loop.py",
        "scripts/architecture_model.py",
        "scripts/auto_recall.py",
    ]
    missing = [m for m in critical if not (HERMES_HOME / m).exists()]
    if missing:
        log(f"Missing critical modules: {missing}")
        return False
    log("All critical modules verified")
    return True


def apply_pending_fixes() -> int:
    """Применить ожидающие фиксы из improvement_suggestions.json."""
    sys.path.insert(0, str(HERMES_HOME / "scripts"))

    suggestions = load_json(SUGGESTIONS_FILE)
    applied = load_json(APPLIED_FILE)
    applied_ids = {a.get("id") for a in applied.get("applied", [])}

    # Импортировать applier
    sys.path.insert(0, str(HERMES_HOME / "skills" / "self-improvement" / "suggestion_applier" / "scripts"))
    from suggestion_applier import apply_suggestion, verify_changes, FIX_DISPATCH

    candidates = [
        s for s in suggestions.get("suggestions", [])
        if s.get("severity") in ("critical", "high")
        and s.get("id") not in applied_ids
        and s.get("issue_type") in FIX_DISPATCH
    ][:5]  # топ-5 за цикл

    if not candidates:
        log("No pending critical fixes")
        return 0

    log(f"Applying {len(candidates)} pending fixes...")
    count = 0
    for s in candidates:
        sid = s.get("id")
        log(f"  Applying: {sid} [{s.get('severity')}] {s.get('title', '')[:60]}")
        result = apply_suggestion(s)
        if result.get("success") and verify_changes(s, result):
            applied.setdefault("applied", []).append({
                "id": sid, "timestamp": datetime.now().isoformat(),
                "issue_type": s.get("issue_type"), "severity": s.get("severity"),
                "title": s.get("title"), "result": result
            })
            count += 1
            log(f"    ✅ Verified")
        else:
            applied.setdefault("failed", []).append({
                "id": sid, "timestamp": datetime.now().isoformat(),
                "issue_type": s.get("issue_type"), "result": result
            })
            log(f"    ❌ Failed: {result.get('error', result.get('message', 'unknown'))}")

    save_json(APPLIED_FILE, applied)
    log(f"Applied {count} fixes this cycle")
    return count


def start_cron_jobs() -> bool:
    """Verify cron scheduler is operational."""
    try:
        # Initialize heartbeat
        sys.path.insert(0, str(HERMES_HOME / "scripts"))
        from chain_heartbeat import register_all_modules
        register_all_modules()

        # Quick verification: cron list works (scheduler is running)
        r = subprocess.run(
            ["hermes", "cron", "list"],
            capture_output=True, text=True, timeout=10, cwd=str(HERMES_HOME),
            encoding="utf-8", errors="replace"
        )
        if r.returncode == 0:
            log("Cron scheduler verified (cron list works)")
            return True
        else:
            log(f"Cron list failed: {r.stderr}")
            return False
    except Exception as e:
        log(f"Cron verification error: {e}")
        return False


def send_ready_heartbeat() -> None:
    """Отправить сигнал готовности системы."""
    try:
        sys.path.insert(0, str(HERMES_HOME / "scripts"))
        from chain_heartbeat import event_beat
        event_beat("system_ready")
        log("Event beat: system_ready")
    except Exception as e:
        log(f"Heartbeat failed: {e}")
    
    # Mark system as ready
    mark_system_ready()


def install_cron_at_boot() -> bool:
    """Установить запуск bootstrap.py при старте системы (Windows Task Scheduler)."""
    try:
        task_name = "HermesBootstrap"
        script = str(HERMES_HOME / "scripts" / "bootstrap.py")
        python_exe = sys.executable

        # Проверить, существует ли задача
        check = subprocess.run(
            ["schtasks", "/Query", "/TN", task_name],
            capture_output=True, text=True
        )
        if check.returncode == 0:
            log("Boot task already installed")
            return True

        # Создать задачу при логине
        cmd = [
            "schtasks", "/Create",
            "/TN", task_name,
            "/TR", f'"{python_exe}" "{script}"',
            "/SC", "ONLOGON",
            "/RL", "HIGHEST",
            "/F"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            log(f"Installed boot task: {task_name}")
            return True
        else:
            log(f"Failed to install boot task: {result.stderr}")
            return False
    except Exception as e:
        log(f"Boot task install error: {e}")
        return False


READY_FLAG = CACHE_DIR / "system_ready.flag"
READY_FLAG_MAX_AGE = 24 * 3600  # 24 hours in seconds


def should_skip_bootstrap() -> bool:
    """Check if bootstrap should be skipped (system ready flag exists and is fresh)."""
    if not READY_FLAG.exists():
        return False
    try:
        mtime = READY_FLAG.stat().st_mtime
        age = time.time() - mtime
        if age < READY_FLAG_MAX_AGE:
            log(f"⏭️ Skipping bootstrap: system_ready.flag is fresh (age: {age/3600:.1f}h)")
            return True
        else:
            log(f"🔄 system_ready.flag is stale (age: {age/3600:.1f}h), running bootstrap")
            return False
    except OSError:
        return False


def mark_system_ready() -> None:
    """Create/update system ready flag."""
    READY_FLAG.parent.mkdir(parents=True, exist_ok=True)
    READY_FLAG.write_text(datetime.now().isoformat(), encoding="utf-8")
    log("🏁 System ready flag created")


def main():
    log("=" * 50)
    log("HERMES BOOTSTRAP — Autonomous System Initialization")
    log("=" * 50)

    # Check if bootstrap should be skipped
    if should_skip_bootstrap():
        log("✅ System already ready, bootstrap skipped")
        return 0

    # 1. Restore state
    restore_backup()

    # 2. Verify integrity
    if not verify_modules():
        log("❌ Module verification failed")
        return 1

    # 3. Apply pending fixes
    apply_pending_fixes()

    # 4. Install boot task
    install_cron_at_boot()

    # 5. Start cron jobs
    if not start_cron_jobs():
        log("⚠️ Cron start had issues")

    # 6. System ready heartbeat
    send_ready_heartbeat()

    log("✅ System ready for autonomous operation")
    return 0


if __name__ == "__main__":
    sys.exit(main())