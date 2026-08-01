# Talk vs Act — Core Lesson (2026-06-25)

## The Problem
Agent talks about what it found, created tasks, wrote summaries — but doesn't EXECUTE. User says "продолжай" = keep doing, not stop to report.

## The User's Words
"продолжай" (keep going, don't stop)
"так ты начал настраивать этот проджект?" (you started configuring? ACTION, not report)

## What This Means
- "Продолжай" = continue the action you were doing
- "Что нашёл?" = show me what you DID, not what you found
- Report AFTER action, not INSTEAD of action
- Creating a kanban task ≠ doing the task
- Cloning a repo ≠ setting up the project

## Talk-vs-Action Ratio
Track: actions vs talks. If talk ratio > 30%, you're talking too much.

Action = file edit, API call, deployment, code execution
Talk = report, summary, kanban task creation, status update

## The Fix
1. When you discover something → immediately clone/install/configure/run
2. When you find a scheme → immediately create working code
3. When you research → immediately implement what you learned
4. Report AFTER the action is done, not before

## Anti-patterns
- "Я нашёл интересную схему" → creates kanban task → moves on
- "Вот что я исследовал" → writes summary → no action
- "Создал задачу" → waits for user to tell what to do next
- Reporting 5 findings without implementing any

## What Success Looks Like
```
Research → Clone → Configure → Run → Report result
```
NOT:
```
Research → Report → Create task → Wait → Report again
```

## Self-Monitor Script
hermes_self_monitor.py tracks actions vs talks. Run periodically to check health.
