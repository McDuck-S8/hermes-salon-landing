# Goal Executor Pool Pattern

## Problem
Sequential goal execution blocks the system. With 10+ goals, new signals wait hours.

## Solution
ThreadPoolExecutor pool + pending_goals deque.

## Architecture
```
GoalPool(max_workers=2)
  ├── active_futures: {future -> goal_id}  (currently running)
  ├── pending: deque([goal, ...])           (waiting for slot)
  ├── results: {goal_id -> result_dict}     (completed)
  └── executor: ThreadPoolExecutor(max_workers)
```

## Flow
1. `submit_goal(goal)` → if active < max_workers → `_start_goal()`
2. else → `pending.append(goal)` (queue)
3. `_start_goal()` → `executor.submit(execute_goal, goal)`
4. `_on_done(future)` → remove from active → pull next from pending
5. `wait_all()` → block until all futures complete
6. `executor.shutdown(wait=True)` → clean exit

## execute_goal() — Honest Execution
```python
def execute_goal(goal):
    cmd = goal.get("action_command") or derive_action(goal)
    if not cmd:
        return {"success": False, "status": "NO_ACTION"}
    
    result = subprocess.run(cmd, shell=True, capture_output=True,
                           text=True, timeout=DEFAULT_TIMEOUT, cwd=str(HERMES))
    
    if result.returncode == 0:
        done_check = check_done_when(goal)
        if done_check["met"] or not goal.get("done_when"):
            return {"success": True, "status": "SUCCESS", "outcome": 1.0}
        else:
            return {"success": False, "status": "UNVERIFIED", "outcome": 0.5}
    else:
        return {"success": False, "status": "FAILED", "outcome": 0.0}
```

## Config (config.yaml)
```yaml
goal_executor:
  max_workers: 2
  default_timeout: 300
  pending_queue_max: 20
```

## Pitfalls
- **RuntimeError on shutdown:** callback tries to submit after executor shutdown → wrap in try/except
- **Progress ≠ 100 immediately:** only set progress=1.0 on verified success
- **Archive completed goals:** call `archive_completed_goals()` after pool completes
- **Thread safety:** use `threading.Lock()` for active_futures and pending access
