# Cron Worker Dashboard API Usage — 2026-07-13 Session

## Context
This session: scheduled cron job ran as a backlog worker to process "ready" tasks from the Hermes Kanban dashboard (port 8766).

## What Happened
1. **Fetched backlog** — `GET /data/tasks.json` returned 25 tasks with various statuses
2. **Selected task** — Highest priority "ready" task: `565fef3d` — "Hermes upstream: проверить обновления" (P2)
3. **Performed work** — Researched upstream Hermes Agent releases via web search + GitHub
4. **Verified version match** — Local `pyproject.toml` version 0.18.2 == upstream latest v0.18.2 (v2026.7.7.2)
5. **Marked done** — `POST /api/task/move` with `{"id":"565fef3d","status":"done"}`
6. **Logged** — Appended entry to `dashboard_data/data/agent_log.md`

## API Usage Details

### GET /data/tasks.json
Returns array of task objects:
```json
{
  "id": "565fef3d",
  "status": "ready",
  "assignee": "unassigned",
  "title": "Hermes upstream: проверить обновления",
  "created_at": "2026-07-12T15:22:35.906733",
  "updated_at": "2026-07-13T02:10:12.370296",
  "description": "Проверить upstream Hermes Agent...",
  "priority": "P2",
  "label": "",
  "type": "task",
  "trigger": ""
}
```

### POST /api/task/move
```bash
curl -X POST http://localhost:8766/api/task/move \
  -H "Content-Type: application/json" \
  -d '{"id":"565fef3d","status":"done"}'
```

**Success:**
```json
{"ok": true, "task": {"id": "565fef3d", "status": "done", ...}}
```

**Error:**
```json
{"ok": false, "error": "invalid id or status"}
```

## Critical Implementation Notes

| Aspect | Detail |
|--------|--------|
| **Required header** | `Content-Type: application/json` (missing → 400/422) |
| **Body fields** | `id` + `status` (NOT `task_id` / `new_status`) |
| **Valid statuses** | `ready`, `running`, `blocked`, `done` |
| **Server process** | `python.exe` PID 45208 listening on 0.0.0.0:8766 |
| **Health check** | `curl -s http://localhost:8766/ → 301 → /dashboard.html` |

## Priority Sorting for Task Selection
```python
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
ready_tasks.sort(key=lambda t: PRIORITY_ORDER.get(t.get("priority", "P2"), 2))
```

## Cron Worker Template

```python
import json, subprocess, sys
from datetime import datetime

def fetch_tasks():
    out = subprocess.check_output(["curl", "-s", "http://localhost:8766/data/tasks.json"])
    return json.loads(out.decode())

def select_task(tasks):
    ready = [t for t in tasks if t["status"] == "ready"]
    if not ready:
        return None
    ready.sort(key=lambda t: {"P0":0,"P1":1,"P2":2,"P3":3}.get(t.get("priority","P2"), 2))
    return ready[0]

def complete_task(task_id):
    payload = json.dumps({"id": task_id, "status": "done"}).encode()
    subprocess.run([
        "curl", "-s", "-X", "POST",
        "http://localhost:8766/api/task/move",
        "-H", "Content-Type: application/json",
        "-d", payload
    ], capture_output=True)

def log_completion(task, description):
    with open("dashboard_data/data/agent_log.md", "a") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(f"[{ts}] Completed {task['id']} - {task['title']} - {description}\n")

if __name__ == "__main__":
    tasks = fetch_tasks()
    task = select_task(tasks)
    if not task:
        print("[SILENT]")
        sys.exit(0)
    
    # ... DO THE WORK HERE ...
    description = "checked upstream, local 0.18.2 matches latest"
    
    complete_task(task["id"])
    log_completion(task, description)
```

## Log Entry Format
```
[YYYY-MM-DD HH:MM] Completed TASK_ID - TASK_TITLE - what was done
```
Example:
```
[2026-07-13 04:05] Completed 565fef3d - Hermes upstream: проверено обновлений - local version 0.18.2 matches upstream latest v0.18.2 (2026.7.7.2). No updates available.
```

## Related
- SKILL.md: dashboard-visualization (REST API endpoints section)
- SKILL.md: cron-maintenance (Dashboard Task API Pattern section)
- Dashboard source: `hermes-agent/web` (FastAPI + vanilla JS frontend)