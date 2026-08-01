# Multi-Agent Delegation Pattern — Parallel Task Execution

## When to Use delegate_task (vs other tools)

| Scenario | Tool | Reason |
|----------|------|--------|
| 3+ independent research/subtasks | `delegate_task` (batch) | True parallelism, isolated contexts, no context pollution |
| Sequential dependent steps | `execute_code` | Single process, shared state, faster for linear work |
| Single tool call | Direct tool | No overhead |
| Long-running (>5 min) / must survive session end | `cronjob` | Durable, survives restarts |
| Need user interaction | Direct (not delegate) | Subagents can't use `clarify` |

---

## Batch Delegation Pattern (from this session)

```python
# GOOD: 3 independent agents in parallel
delegate_task(tasks=[
    {"goal": "Research channel marketplaces...", "role": "leaf"},
    {"goal": "Analyze Pinterest formats...", "role": "leaf"},
    {"goal": "Build Fal.ai pipeline...", "role": "leaf"},
])

# BAD: Sequential when independent
delegate_task(goal="Task 1")  # wait...
delegate_task(goal="Task 2")  # wait...
delegate_task(goal="Task 3")  # wait...
```

**Key insight from session:** All 3 agents timed out at 600s because they hit slow API calls. Next time: set shorter timeouts or use `execute_code` with `timeout` for web-heavy tasks.

---

## Context Injection Template

Each subagent gets **only** what you pass in `context`. Be specific:

```python
context = """
Project: Hermes Autonomous Income System
Current state: 4 Telegram channels ready, Pinterest in dry-run, 5 bots extracted
Constraints: Windows, Python 3.11, V2RayN proxy (direct HTTP to api.telegram.org TIMEOUTS)
Available: python-telegram-bot, Fal.ai (paid), Bing/Leonardo (free), You.com API key in .env
Task: Research Fragment.com, Telemetr.io, P2P for selling TG channels $5+ crypto
Output: D:/Portable_Soft/hermes/reports/channel_marketplaces.md
"""
```

---

## Subagent Output Handling

- Returns as **single consolidated message** when ALL complete
- Each subagent result has: `goal`, `status`, `summary`, `output_file`
- Subagent summaries are **self-reported** — verify critical outputs yourself (read file, check URL)

---

## Orchestrator Pattern (for complex workflows)

```python
# Spawn orchestrator that spawns workers
delegate_task(
    goal="Coordinate: 1) Research markets, 2) Build pipeline, 3) Test deploy",
    role="orchestrator",  # can call delegate_task internally
    context="..."
)
```

**Max depth for this user:** 2 levels (orchestrator → workers)

---

## Pitfalls Learned

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| No timeout on web-heavy tasks | 600s timeout, 20+ API calls stuck | Use `execute_code` with explicit timeout for web calls |
| Vague context | Agent researches wrong thing | Include: project state, constraints, exact output path |
| Too many concurrent | Rate limits / resource exhaustion | Max 3 for this user (config: `delegation.max_concurrent_children=3`) |
| Assuming subagent success | "Uploaded successfully" but file missing | Verify: read file, check URL, stat path |
| Nested orchestrators too deep | Max depth exceeded | Max 2 levels for this user |