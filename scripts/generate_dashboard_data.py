#!/usr/bin/env python3
"""Generate JSON data files for Hermes Dashboard"""
import json
import subprocess
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "D:/Portable_Soft/hermes/scripts")

# Try to import hermes modules
try:
    from hermes_hooks import get_hooks
    HOOKS_AVAILABLE = True
except ImportError:
    HOOKS_AVAILABLE = False

DATA_DIR = Path("D:/Portable_Soft/hermes/data")
DATA_DIR.mkdir(exist_ok=True)


def run_cmd(cmd, cwd=None):
    """Run command and return stdout"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd or "D:/Portable_Soft/hermes", timeout=30)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "timeout", 1
    except Exception as e:
        return "", str(e), 1


def get_kanban_tasks():
    """Get kanban tasks from hermes kanban list"""
    stdout, stderr, code = run_cmd("hermes kanban list --all --format json 2>&1")
    if code == 0 and stdout:
        try:
            data = json.loads(stdout)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "tasks" in data:
                return data["tasks"]
        except json.JSONDecodeError:
            pass
    # Fallback: parse text output
    tasks = []
    if stdout:
        lines = stdout.strip().split('\n')
        for line in lines:
            if line.strip() and not line.startswith('┌') and not line.startswith('│') and not line.startswith('└'):
                # Try to parse table row
                parts = [p.strip() for p in line.split('│')]
                if len(parts) >= 4:
                    tasks.append({
                        "id": parts[1],
                        "title": parts[2] if len(parts) > 2 else "",
                        "status": parts[3] if len(parts) > 3 else "unknown",
                        "assignee": parts[4] if len(parts) > 4 else "unassigned",
                        "created_at": parts[5] if len(parts) > 5 else "",
                        "updated_at": parts[6] if len(parts) > 6 else "",
                        "age": 0
                    })
    return tasks


def get_cron_jobs():
    """Get cron jobs from hermes cron list"""
    stdout, stderr, code = run_cmd("hermes cron list --format json 2>&1")
    if code == 0 and stdout:
        try:
            data = json.loads(stdout)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "jobs" in data:
                return data["jobs"]
        except json.JSONDecodeError:
            pass
    # Parse text output
    jobs = []
    if stdout:
        lines = stdout.strip().split('\n')
        current_job = {}
        for line in lines:
            line = line.strip()
            if line.startswith('─') or line.startswith('┌') or line.startswith('└'):
                continue
            if line and not line.startswith('Name:') and not line.startswith('Schedule:') and not line.startswith('Repeat:') and not line.startswith('Next run:') and not line.startswith('Deliver:') and not line.startswith('Script:') and not line.startswith('Mode:') and not line.startswith('Workdir:') and not line.startswith('Last run:'):
                # Job ID line
                if current_job:
                    jobs.append(current_job)
                parts = line.split()
                if parts:
                    current_job = {"id": parts[0], "name": " ".join(parts[1:]) if len(parts) > 1 else ""}
            elif line.startswith('Name:'):
                current_job["name"] = line[5:].strip()
            elif line.startswith('Schedule:'):
                current_job["schedule"] = line[9:].strip()
            elif line.startswith('Repeat:'):
                current_job["repeat"] = line[7:].strip()
            elif line.startswith('Next run:'):
                current_job["next_run"] = line[9:].strip()
            elif line.startswith('Deliver:'):
                current_job["deliver"] = line[8:].strip()
            elif line.startswith('Script:'):
                current_job["script"] = line[7:].strip()
            elif line.startswith('Mode:'):
                current_job["mode"] = line[5:].strip()
            elif line.startswith('Workdir:'):
                current_job["workdir"] = line[8:].strip()
            elif line.startswith('Last run:'):
                parts = line[9:].split('  ')
                current_job["last_run"] = parts[0].strip() if parts else ""
                current_job["last_status"] = parts[1].strip() if len(parts) > 1 else ""
        if current_job:
            jobs.append(current_job)
    return jobs


def get_profiles():
    """Get profiles from hermes profile list"""
    stdout, stderr, code = run_cmd("hermes profile list --format json 2>&1")
    if code == 0 and stdout:
        try:
            data = json.loads(stdout)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "profiles" in data:
                return data["profiles"]
        except json.JSONDecodeError:
            pass
    # Parse text
    profiles = []
    if stdout:
        lines = stdout.strip().split('\n')
        for line in lines:
            if '│' in line and not line.startswith('┌') and not line.startswith('└') and not line.startswith('│ Profile'):
                parts = [p.strip() for p in line.split('│')]
                if len(parts) >= 4:
                    profiles.append({
                        "name": parts[1],
                        "model": parts[2] if len(parts) > 2 else "",
                        "gateway": parts[3] if len(parts) > 3 else "",
                        "active": "active" in line.lower() or "✓" in line
                    })
    return profiles


def get_system_health():
    """Get system health metrics"""
    health = {}
    # Uptime
    stdout, _, _ = run_cmd("wmic os get LastBootUpTime /value 2>&1")
    if stdout:
        for line in stdout.split('\n'):
            if 'LastBootUpTime' in line:
                boot_str = line.split('=')[1].strip()
                try:
                    # WMI format: 20240611170000.000000+180
                    boot_time = datetime.strptime(boot_str[:14], "%Y%m%d%H%M%S")
                    uptime = datetime.now() - boot_time
                    days = uptime.days
                    hours, rem = divmod(uptime.seconds, 3600)
                    minutes, _ = divmod(rem, 60)
                    health["uptime"] = f"{days}d {hours}h {minutes}m"
                except:
                    health["uptime"] = "unknown"
                break

    # Memory
    stdout, _, _ = run_cmd("wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /value 2>&1")
    if stdout:
        free = total = 0
        for line in stdout.split('\n'):
            if 'FreePhysicalMemory' in line:
                free = int(line.split('=')[1].strip()) * 1024  # KB to bytes
            elif 'TotalVisibleMemorySize' in line:
                total = int(line.split('=')[1].strip()) * 1024
        if total > 0:
            used_pct = (total - free) / total * 100
            health["memory"] = f"{used_pct:.0f}% used ({free/1024/1024/1024:.1f}GB free / {total/1024/1024/1024:.1f}GB)"

    # Disk
    stdout, _, _ = run_cmd("wmic logicaldisk get DeviceID,FreeSpace,Size /value 2>&1")
    if stdout:
        for line in stdout.split('\n'):
            if 'DeviceID=D:' in line or 'DeviceID=C:' in line:
                drive = 'D:' if 'D:' in line else 'C:'
                free = size = 0
                for l in stdout.split('\n'):
                    if f'DeviceID={drive}' in l:
                        continue
                    if 'FreeSpace=' in l:
                        free = int(l.split('=')[1].strip())
                    elif 'Size=' in l:
                        size = int(l.split('=')[1].strip())
                if size > 0:
                    free_gb = free / 1024 / 1024 / 1024
                    health["disk_free"] = f"{free_gb:.0f}GB free on {drive}"
                break

    # CPU
    stdout, _, _ = run_cmd("wmic cpu get LoadPercentage /value 2>&1")
    if stdout:
        for line in stdout.split('\n'):
            if 'LoadPercentage' in line:
                try:
                    health["cpu_percent"] = int(line.split('=')[1].strip())
                except:
                    pass
                break

    # Recent logs
    logs = []
    log_dir = Path("D:/Portable_Soft/hermes/logs")
    if log_dir.exists():
        log_files = sorted(log_dir.glob("*.log"), key=lambda f: f.stat().st_mtime, reverse=True)[:3]
        for log_file in log_files:
            try:
                lines = log_file.read_text(encoding='utf-8', errors='ignore').strip().split('\n')
                for line in lines[-10:]:
                    if line.strip():
                        level = "info"
                        if "ERROR" in line.upper() or "FAIL" in line.upper() or "TRACEBACK" in line.upper():
                            level = "error"
                        elif "WARN" in line.upper():
                            level = "warn"
                        elif "OK" in line.upper() or "SUCCESS" in line.upper():
                            level = "ok"
                        logs.append({
                            "time": datetime.fromtimestamp(log_file.stat().st_mtime).strftime("%H:%M:%S"),
                            "message": f"[{log_file.name}] {line[:120]}",
                            "level": level
                        })
            except:
                pass
    health["recent_logs"] = logs[-20:]  # last 20 entries
    return health


def main():
    print("Generating dashboard data...")

    tasks = get_kanban_tasks()
    crons = get_cron_jobs()
    profiles = get_profiles()
    health = get_system_health()

    # Add timestamps
    for task in tasks:
        if "created_at" not in task:
            task["created_at"] = datetime.now().isoformat()
        if "updated_at" not in task:
            task["updated_at"] = datetime.now().isoformat()

    for cron in crons:
        if "last_run" not in cron:
            cron["last_run"] = "never"
        if "last_status" not in cron:
            cron["last_status"] = "—"

    # Write JSON files
    (DATA_DIR / "tasks.json").write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA_DIR / "crons.json").write_text(json.dumps(crons, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA_DIR / "profiles.json").write_text(json.dumps(profiles, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA_DIR / "health.json").write_text(json.dumps(health, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Tasks: {len(tasks)}")
    print(f"Crons: {len(crons)}")
    print(f"Profiles: {len(profiles)}")
    print(f"Health: {len(health)} metrics")
    print(f"Written to {DATA_DIR}")


if __name__ == "__main__":
    main()