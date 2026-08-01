# Dashboard Task API Usage — 2026-07-13 Session

## Context
Cron job ran as backlog worker to process ready tasks from the Hermes Kanban dashboard.

## What Happened
1. Fetched task backlog from `http://localhost:8766/data/tasks.json`
2. Identified highest-priority "ready" task: `565fef3d` — "Hermes upstream: проверить обновления" (P2)
3. Researched upstream Hermes Agent releases via GitHub API and web search
4. Verified local version (0.18.2 from pyproject.toml) matches upstream latest (v0.18.2 / v2026.7.7.2)
5. Updated task status via `POST /api/task/move` with `{"id":"565fef3d","status":"done"}`
6. Logged completion to `dashboard_data/data/agent_log.md`

## API Details

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
  "description": "...",
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

Success response:
```json
{"ok": true, "task": {"id": "565fef3d", "status": "done", ...}}
```

Error response:
```json
{"ok": false, "error": "invalid id or status"}
```

## Notes
- Dashboard server runs on port 8766 (Python process PID 45208)
- The `Content-Type: application/json` header is required
- Body uses `id` and `status` fields (not `task_id` / `new_status`)
- Valid statuses: `ready`, `running`, `blocked`, `done`
- Task log format: `[YYYY-MM-DD HH:MM] Completed TASK_ID - TASK_NAME - what was done`

## Template for Future Cron Workers

```python
import json
import subprocess

# 1. Fetch tasks
tasks_json = subprocess.check_output([
    "curl", "-s", "http://localhost:8766/data/tasks.json"
]).decode()
tasks = json.loads(tasks_json)

# 2. Find highest-priority ready task
ready = [t for t in tasks if t["status"] == "ready"]
if not ready:
    print("[SILENT]")  # No work
    exit(0)

ready.sort(key=lambda t: {"P0": 0, "P1": 1, "P2": 2}.get(t.get("priority", "P2"), 3))
task = ready[0]

# 3. Do the work (research, code, docs, etc.)
# ... work happens here ...

# 4. Mark done
subprocess.run([
    "curl", "-s", "-X", "POST",
    "http://localhost:8766/api/task/move",
    "-H", "Content-Type: application/json",
    "-d", json.dumps({"id": task["id"], "status": "done"})
])

# 5. Log
with open("dashboard_data/data/agent_log.md", "a") as f:
    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Completed {task['id']} - {task['title']} - ...\n")
```

## Related
- SKILL.md: cron-maintenance (Dashboard Task API Pattern section)
- Dashboard source: `hermes-agent/web` (FastAPI + vanilla JS frontend)