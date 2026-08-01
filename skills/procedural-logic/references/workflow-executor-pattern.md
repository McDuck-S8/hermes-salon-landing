# Workflow Executor Pattern — Native n8n Replacement

## Overview
Replaces n8n with pure Python workflow execution. Built per user directive: "n8n — вычёркиваем. Ты сам — оркестратор."

## Architecture
```
goal_queue.json (source of truth)
    ↓
workflow_executor.py (engine)
    ↓
EXECUTORS registry (step type → function)
    ↓
script | terminal | kc_upsert | kc_search | goal_create | goal_update | wait
    ↓
Self-healing: failure → corrective goal in goal_queue
```

## Goal Queue Format
```json
{
  "goals": [
    {
      "id": "g-xxx",
      "title": "Workflow Name",
      "status": "active",
      "related_actions": ["workflow"],
      "workflow": {
        "id": "wf-xxx",
        "name": "Workflow Name",
        "steps": [
          {"name": "step1", "type": "script", "script_name": "script.py", "args": ["--arg"]},
          {"name": "step2", "type": "terminal", "command": "echo hello"},
          {"name": "step3", "type": "kc_upsert", "content": "findings", "tags": "tag", "category": "cat"}
        ]
      }
    }
  ]
}
```

## Step Types
| Type | Parameters | Description |
|------|------------|-------------|
| `script` | `script_name`, `args` | Run Python script from `scripts/` |
| `terminal` | `command` | Run shell command |
| `kc_upsert` | `content`, `tags`, `source`, `category`, `importance` | Write to Knowledge Cube |
| `kc_search` | `query`, `limit` | Search Knowledge Cube |
| `goal_create` | goal fields | Create new goal |
| `goal_update` | `goal_id`, `updates` | Update existing goal |
| `wait` | `seconds` | Sleep |

## Self-Healing
On step failure:
1. Log failure
2. Create corrective goal in `goal_queue.json`:
   - `id`: `corrective-{workflow_id}-{step_num}`
   - `description`: includes original step JSON + error
   - `done_when`: ["Step executes successfully", "Workflow completes"]
3. Stop workflow (unless `continue_on_error: true`)

## Built-in Workflows
```bash
python workflow_executor.py list           # List all
python workflow_executor.py builtin daily_maintenance
python workflow_executor.py builtin revenue_test_cycle
python workflow_executor.py builtin research_to_kc
python workflow_executor.py goal g-xxx     # Run workflow from goal
python workflow_executor.py run            # Run all active goal-based workflows
```

## Integration with Daemon
`event_daemon.py` beat() can trigger workflows:
- Sensor detects event → push to `goal_queue` with `"related_actions": ["workflow"]`
- Next daemon beat picks up and executes
- Event-driven, not cron-based

## Files
- `scripts/workflow_executor.py` — Engine (13KB)
- `cache/goal_queue.json` — Source of truth
- `cache/workflow.log` — Execution log
- `cache/workflow_state.json` — Stats (executed, failed, last_run)

## n8n Taboo
n8n = ABSOLUTE TABOO (5 confirmations: 2026-06-21, 2026-06-22×2, 2026-06-25, 2026-06-28)
- Never mention, suggest, or show n8n
- Native stack: Python + SQLite + MCP + LiteLLM proxy = $5-10/mo
- Daemon workflows replace drag-and-drop

## Quality Criteria (Эталон качества)
- [ ] Zero external dependencies (stdlib only)
- [ ] Self-healing on failure (corrective goal created)
- [ ] Event-driven capable (not cron)
- [ ] All step types working (script, terminal, kc_*, goal_*, wait)
- [ ] Corrective goals include original step JSON for reproducibility
- [ ] Built-in workflows execute without errors
- [ ] Logs show clear success/failure per step