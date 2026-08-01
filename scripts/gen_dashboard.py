#!/usr/bin/env python3
"""Generate dashboard data JSON files for the Hermes dashboard."""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERMES_ROOT = Path(__file__).parent.parent
DATA_DIR = HERMES_ROOT / "dashboard_data"
DATA_DIR.mkdir(exist_ok=True)


def run(cmd, timeout=10):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=HERMES_ROOT)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "timeout", 124
    except Exception as e:
        return "", str(e), 1


def parse_kanban_list(output):
    tasks = []
    for line in output.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('▶') or line.startswith('⊘'):
            # Parse task line: ▶ e3d20e1f  ready     (unassigned)          Salon bot: нужен второй токен от BotFather
            # or: ⊘ t_a70b1bbb  blocked   default               EverOS — запуск сервера, интеграция с кристаллом
            parts = line.split()
            if len(parts) >= 5:
                status = "ready" if line.startswith('▶') else "blocked"
                task_id = parts[1]
                # parts[2] is the status column (ready/blocked)
                # parts[3] is the assignee column (could be (unassigned) or profile name)
                assignee = parts[3] if parts[3] != "(unassigned)" else "unassigned"
                title = ' '.join(parts[4:])
                tasks.append({
                    "id": task_id,
                    "status": status,
                    "assignee": assignee,
                    "title": title,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                })
    return tasks


def parse_kanban_stats(output):
    stats = {"ready": 0, "running": 0, "blocked": 0, "done": 0, "total": 0}
    for line in output.split('\n'):
        line = line.strip()
        if 'ready' in line and 'status' in line.lower():
            # parse "ready     18"
            parts = line.split()
            if len(parts) >= 2 and parts[0] in stats:
                stats[parts[0]] = int(parts[1])
        elif 'blocked' in line.lower() and 'status' in line.lower():
            parts = line.split()
            if len(parts) >= 2 and parts[0] in stats:
                stats[parts[0]] = int(parts[1])
        elif 'running' in line.lower() and 'status' in line.lower():
            parts = line.split()
            if len(parts) >= 2 and parts[0] in stats:
                stats[parts[0]] = int(parts[1])
        elif 'done' in line.lower() and 'status' in line.lower():
            parts = line.split()
            if len(parts) >= 2 and parts[0] in stats:
                stats[parts[0]] = int(parts[1])
    stats["total"] = sum(stats.values())
    return stats


def parse_cron_list(output):
    crons = []
    current = {}
    for line in output.split('\n'):
        line = line.rstrip()
        if not line:
            if current:
                crons.append(normalize_cron(current))
                current = {}
            continue
        if line.startswith('  ') and ':' in line:
            key, val = line.split(':', 1)
            current[key.strip()] = val.strip()
        elif line.startswith('Name:'):
            if current:
                crons.append(normalize_cron(current))
            current = {"Name": line.split(':', 1)[1].strip()}
        elif line.startswith('Schedule:'):
            current["Schedule"] = line.split(':', 1)[1].strip()
        elif line.startswith('Repeat:'):
            current["Repeat"] = line.split(':', 1)[1].strip()
        elif line.startswith('Next run:'):
            current["Next run"] = line.split(':', 1)[1].strip()
        elif line.startswith('Deliver:'):
            current["Deliver"] = line.split(':', 1)[1].strip()
        elif line.startswith('Script:'):
            current["Script"] = line.split(':', 1)[1].strip()
        elif line.startswith('Mode:'):
            current["Mode"] = line.split(':', 1)[1].strip()
        elif line.startswith('Last run:'):
            current["Last run"] = line.split(':', 1)[1].strip()
        elif line.startswith('Workdir:'):
            current["Workdir"] = line.split(':', 1)[1].strip()
        elif line.startswith('error:') or line.startswith('ok'):
            current["Last status"] = line.strip()
    if current:
        crons.append(normalize_cron(current))
    return crons


def normalize_cron(c):
    """Normalize cron keys to lowercase with underscores for dashboard."""
    # Extract last_status and last_run from "Last run" field
    last_run = c.get("Last run", "")
    last_status = c.get("Last status", "unknown")
    if "  " in last_run:
        parts = last_run.rsplit("  ", 1)
        if len(parts) == 2:
            last_run, last_status = parts[0].strip(), parts[1].strip()
    return {
        "name": c.get("Name", ""),
        "schedule": c.get("Schedule", ""),
        "repeat": c.get("Repeat", ""),
        "next_run": c.get("Next run", ""),
        "deliver": c.get("Deliver", ""),
        "script": c.get("Script", ""),
        "mode": c.get("Mode", ""),
        "last_run": last_run,
        "last_status": last_status.lower() if last_status else "unknown",
        "workdir": c.get("Workdir", "")
    }


def parse_profiles(output):
    profiles = []
    for line in output.split('\n'):
        line = line.strip()
        if line and not line.startswith('Profile') and not line.startswith('─'):
            parts = line.split()
            if len(parts) >= 4:
                name = parts[0]
                model = parts[1] if len(parts) > 1 else "unknown"
                gateway = parts[2] if len(parts) > 2 else "unknown"
                profiles.append({
                    "name": name,
                    "model": model,
                    "gateway": gateway,
                    "active": name.startswith('◆') or name.startswith('●')
                })
    return profiles


def main():
    print("Fetching kanban tasks...")
    out, err, code = run("hermes kanban list")
    tasks = parse_kanban_list(out)

    print("Fetching kanban stats...")
    out2, err2, code2 = run("hermes kanban stats")
    stats = parse_kanban_stats(out2)

    print("Fetching cron jobs...")
    out3, err3, code3 = run("hermes cron list")
    crons = parse_cron_list(out3)

    print("Fetching profiles...")
    out4, err4, code4 = run("hermes profile list")
    profiles = parse_profiles(out4)

    # System health (basic)
    health = {
        "timestamp": datetime.now().isoformat(),
        "kanban_stats": stats,
        "cron_count": len(crons),
        "profile_count": len(profiles),
        "recent_logs": []
    }

    # Write files
    (DATA_DIR / "tasks.json").write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA_DIR / "crons.json").write_text(json.dumps(crons, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA_DIR / "profiles.json").write_text(json.dumps(profiles, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA_DIR / "health.json").write_text(json.dumps(health, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Done! Tasks: {len(tasks)}, Crons: {len(crons)}, Profiles: {len(profiles)}")
    print(f"Written to {DATA_DIR}")


if __name__ == "__main__":
    main()