# goal_queue.py Fix — Bool Return Guard

## Problem
`goal_executor.execute_goal(goal)` returns a `bool` (True/False), but `goal_queue.py` calls `result.get("outcome", 0)` on it, causing `AttributeError: 'bool' object has no attribute 'get'`.

## Fix (goal_queue.py line ~415)
```python
from goal_executor import execute_goal
result = execute_goal(goal)

# Handle bool returns (simple pass/fail)
if isinstance(result, bool):
    result = {"success": result, "outcome": 1.0 if result else 0.0,
              "evidence": "executed" if result else "failed"}
```

## Pattern
When calling functions that may return different types (bool vs dict), always guard:
```python
if isinstance(result, bool):
    result = {"success": result, "outcome": 1.0 if result else 0.0}
```

## Context
Autonomous Agent selects a goal → calls `_action_pursue_goal()` → calls `execute_goal()` → returns bool → crash.
The goal execution pipeline needs type-safe handoffs between components.
