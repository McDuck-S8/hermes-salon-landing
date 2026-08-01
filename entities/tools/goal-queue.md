---
id: goal-queue
type: tool
namespace: knowledge/ai-core
status: canon
version: 1.0.0
owner: operator
created: 2026-06-29T00:00:00Z
summary: Priority goal queue with tier-based priority system
description: |
  Goal Queue manages all goals in Hermes with tier-based priority (1-10).
  Supports get_highest_priority_goal, create_goal, update_progress, and
  completion verification. Used by autonomous agent for first autonomous action.
depends_on:
  - goal-executor
tags:
  - goal-management
  - priority-queue
  - tier-based
confidence: 0.9
retrieval_class: hot
export_class: operator
---

# Goal Queue — Priority Goal Management

## Role
Central goal storage and priority management for Hermes autonomous operation.

## Structure
- Tier 1: System health / self-healing (priority 10)
- Tier 2: Knowledge acquisition / gap filling (priority 8-9)
- Tier 3: Revenue generation / production (priority 5-7)
- Tier 4: Maintenance / optimization (priority 1-4)

## API
- `get_highest_priority_goal()` → goal or None
- `create_goal(name, tier, priority, metadata)` → goal_id
- `update_goal_progress(goal_id, progress)` → bool
- `complete_goal(goal_id, outcome)` → bool

## Integration
- `scripts/goal_queue.py` — Implementation
- `scripts/goal_executor.py` — Consumer
- `scripts/autonomous_agent.py` — Uses for first action

## Related Entities
- [[goal-executor]] — Execution engine
- [[autonomous-agent]] — Consumer