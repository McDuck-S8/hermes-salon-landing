"""Proactive DOER — автономный исполнитель фиксов.

В отличие от self_healing_monitor (который только отчитывается),
этот скрипт реально чинит проблемы:
- Перезапускает упавшие cron-задачи
- Чистит залипшие lock-файлы
- Удаляет устаревший кеш
- Перезапускает зависшие процессы
- Чинит битые JSON/state-файлы

Логика: 1 попытка фикса → если удалось → молча.
        3+ неудач одной категории → алерт.

Работает как no_agent cron (каждые 15 минут).
"""
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
STATE_FILE = HERMES_HOME / "cron" / "proactive_doer_state.json"
LOG_FILE = HERMES_HOME / "logs" / "proactive_doer.log"
LOCK_DIRS = [
    HERMES_HOME / "cron",
    HERMES_HOME / "data",
    HERMES_HOME / "cache",
    HERMES_HOME / "logs",
    HERMES_HOME,
]
CACHE_DIRS = [
    HERMES_HOME / "cache",
    HERMES_HOME / "logs",
    HERMES_HOME / "sessions",
]
MAX_LOCK_AGE = 3600  # 1 hour — lock older than this is stale
ALERT_THRESHOLD = 3  # consecutive failures before alerting

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(str(LOG_FILE), encoding="utf-8"),
              logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("proactive-doer")


# ── State ──

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}

def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Check types (each returns list of (issue_type, description, fix_action)) ──

def check_stale_locks() -> list:
    """Find and remove lock files older than MAX_LOCK_AGE."""
    found = []
    for lock_dir in LOCK_DIRS:
        if not lock_dir.exists():
            continue
        for f in lock_dir.iterdir():
            if f.name.endswith(".lock") and f.is_file():
                age = time.time() - f.stat().st_mtime
                if age > MAX_LOCK_AGE:
                    found.append(("stale_lock", str(f.name), lambda p=f: remove_lock(p)))
    return found


def check_broken_json() -> list:
    """Check state files for valid JSON, fix if corrupted."""
    state_files = [
        HERMES_HOME / "cron" / "jobs.json",
        HERMES_HOME / "cron" / "self_healing_state.json",
        HERMES_HOME / "cron" / "skill_evolution_state.json",
        STATE_FILE,
    ]
    found = []
    for sf in state_files:
        if sf.exists() and sf.stat().st_size > 0:
            try:
                json.loads(sf.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, ValueError) as e:
                found.append(("broken_json", str(sf.name), lambda p=sf: fix_broken_json(p)))
    return found


def check_dead_jobs() -> list:
    """Find cron jobs with errors and restart them."""
    try:
        result = subprocess.run(
            ["hermes", "cron", "list"],
            capture_output=True, text=True, timeout=30,
            cwd=str(HERMES_HOME),
        )
        output = result.stdout + result.stderr
    except Exception as e:
        log.warning("Cannot list cron jobs: %s", e)
        return []

    found = []
    # Find jobs with "error" status but ignore self
    for line in output.split("\n"):
        m = re.match(r"Last run:\s+\S+\s+error", line)
        if m:
            # Find the job ID - it's in a previous block
            found.append(("dead_job", "cron job with error", lambda: restart_all_errors()))
            break
    return found


def check_stale_cache() -> list:
    """Remove cache/log/session files older than 7 days."""
    now = time.time()
    max_age = 7 * 86400
    removed_count = 0
    for cache_dir in CACHE_DIRS:
        if not cache_dir.exists():
            continue
        for f in cache_dir.iterdir():
            if f.is_file() and not f.name.endswith(".lock"):
                try:
                    if now - f.stat().st_mtime > max_age and f.stat().st_size > 0:
                        f.unlink()
                        removed_count += 1
                except OSError:
                    pass
    if removed_count > 0:
        return [("stale_cache", f"removed {removed_count} stale files", None)]
    return []


# ── Fix actions ──

def remove_lock(path: Path) -> bool:
    try:
        path.unlink(missing_ok=True)
        log.info("Removed stale lock: %s", path.name)
        return True
    except OSError as e:
        log.error("Failed to remove lock %s: %s", path.name, e)
        return False


def fix_broken_json(path: Path) -> bool:
    try:
        # Try to recover: write empty {} or []
        content = path.read_text(encoding="utf-8").strip()
        if content.startswith("["):
            path.write_text("[]", encoding="utf-8")
        else:
            path.write_text("{}", encoding="utf-8")
        log.info("Fixed broken JSON: %s", path.name)
        return True
    except OSError as e:
        log.error("Failed to fix %s: %s", path.name, e)
        return False


def restart_all_errors() -> bool:
    success = True
    try:
        result = subprocess.run(
            ["hermes", "cron", "list"],
            capture_output=True, text=True, timeout=30,
            cwd=str(HERMES_HOME),
        )
        output = result.stdout + result.stderr
        # Find job IDs with errors
        blocks = re.split(r"\n\s*\n", output)
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            lines = block.split("\n")
            job_id = lines[0].split()[0] if lines else ""
            last_run_status = ""
            for line in lines:
                if "Last run:" in line:
                    parts = line.rsplit(" ", 1)
                    if len(parts) > 1:
                        last_run_status = parts[1].strip()
            if last_run_status == "error" and job_id:
                log.info("Restarting failed job: %s", job_id)
                subprocess.run(
                    ["hermes", "cron", "run", job_id],
                    capture_output=True, text=True, timeout=60,
                    cwd=str(HERMES_HOME),
                )
        return True
    except Exception as e:
        log.error("Error restarting jobs: %s", e)
        return False


# ── Main ──

def main():
    log.info("=== Proactive DOER run ===")
    state = load_state()
    now = datetime.now(timezone.utc).isoformat()

    # Track per-category failures
    if "failures" not in state:
        state["failures"] = {}
    if "last_run" not in state:
        state["last_run"] = None

    all_issues = []
    all_issues.extend(check_stale_locks())
    all_issues.extend(check_broken_json())
    all_issues.extend(check_dead_jobs())
    all_issues.extend(check_stale_cache())

    fixed_count = 0
    alert_count = 0
    alerts = []

    for issue_type, description, fix_action in all_issues:
        if fix_action is None:
            # Already fixed (cache cleanup)
            fixed_count += 1
            continue

        success = fix_action()
        cat = state["failures"].setdefault(issue_type, 0)
        if success:
            state["failures"][issue_type] = 0
            fixed_count += 1
            log.info("✓ Fixed %s: %s", issue_type, description)
        else:
            state["failures"][issue_type] = state["failures"].get(issue_type, 0) + 1
            fail_count = state["failures"][issue_type]
            if fail_count >= ALERT_THRESHOLD:
                alert_count += 1
                msg = f"⚠ ALERT: {issue_type} — {description} (failed {fail_count}x)"
                alerts.append(msg)
                log.warning(msg)
            else:
                log.warning("Failed %s (%s): attempt %d/%d",
                            issue_type, description, fail_count, ALERT_THRESHOLD)

    state["last_run"] = now
    state["fixed_count"] = state.get("fixed_count", 0) + fixed_count
    state["alert_count"] = state.get("alert_count", 0) + alert_count
    save_state(state)

    summary = f"DOER: {fixed_count} fixed, {alert_count} alerts"
    if fixed_count or alert_count:
        log.info(summary)

    # Emit alerts to stdout so cron delivery picks them up
    if alerts:
        for a in alerts:
            print(a)

    if fixed_count > 0 and alert_count == 0:
        print(f"✓ {summary}")


if __name__ == "__main__":
    main()
