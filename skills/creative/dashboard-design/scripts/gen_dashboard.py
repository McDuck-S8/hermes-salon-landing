#!/usr/bin/env python3
"""Generate dashboard JSON data from Hermes CLI."""
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
            parts = line.split()
            if len(parts) >= 4:
                status = "ready" if line.startswith('▶') else "blocked"
                task_id = parts[1]
                # parts[2] is the status column (ready/blocked)
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
        if not line:
            continue
        if 'ready' in line and 'status' in line.lower():
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
                crons.append(current)
                current = {}
            continue
        if line.startswith('Name:'):
            if current:
                crons.append(current)
            current = {"name": line.split(':', 1)[1].strip()}
        elif line.startswith('Schedule:'):
            current["schedule"] = line.split(':', 1)[1].strip()
        elif line.startswith('Repeat:'):
            current["repeat"] = line.split(':', 1)[1].strip()
        elif line.startswith('Next run:'):
            current["next_run"] = line.split(':', 1)[1].strip()
        elif line.startswith('Deliver:'):
            current["deliver"] = line.split(':', 1)[1].strip()
        elif line.startswith('Script:'):
            current["script"] = line.split(':', 1)[1].strip()
        elif line.startswith('Mode:'):
            current["mode"] = line.split(':', 1)[1].strip()
        elif line.startswith('Last run:'):
            current["last_run"] = line.split(':', 1)[1].strip()
        elif line.startswith('Workdir:'):
            current["workdir"] = line.split(':', 1)[1].strip()
        elif line.startswith('error:') or line.startswith('ok'):
            current["last_status"] = line.strip()
    if current:
        crons.append(current)
    return crons


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

    health = {
        "timestamp": datetime.now().isoformat(),
        "kanban_stats": stats,
        "cron_count": len(crons),
        "profile_count": len(profiles),
        "recent_logs": []
    }
    (DATA_DIR / "health.json").write_text(json.dumps(health, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Done! Tasks: {len(tasks)}, Crons: {len(crons)}, Profiles: {len(profiles)}")
    print(f"Written to {DATA_DIR}")


if __name__ == "__main__":
    main()