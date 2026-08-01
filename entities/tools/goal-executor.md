---
id: goal-executor
type: tool
namespace: knowledge/ai-core
status: canon
version: 1.0.0
owner: operator
created: 2026-06-29T00:00:00Z
summary: Executes goals from goal queue with progress tracking
description: |
  Goal Executor takes goals from the goal queue and executes them. Supports
  autonomous execution, progress tracking, and verification. Integrates with
  autonomous agent for the "autonomous first action" at boot.
depends_on:
  - goal-queue
  - autonomous-agent
tags:
  - goal-execution
  - progress-tracking
  - verification
confidence: 0.9
retrieval_class: hot
export_class: operator
---

# Goal Executor — Goal Execution Engine

## Role
Executes goals from the goal queue with full lifecycle management.

## Flow
1. Receive goal from autonomous agent or manual trigger
2. Execute goal steps (via delegate_task, scripts, or direct action)
3. Track progress (0-100%)
4. Verify outcome (not just output)
5. Mark complete or blocked

## Integration
- `scripts/goal_executor.py` — Main executor
- `scripts/goal_queue.py` — Goal storage
- `scripts/autonomous_agent.py` — Consumer

## Related Entities
- [[goal-queue]] — Goal storage
- [[autonomous-agent]] — Executive runtime