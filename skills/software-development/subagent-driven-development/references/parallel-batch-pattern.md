# Parallel Batch Execution Pattern

## When to Use

When you have 2-3 **independent** tasks that don't share state or file locks. This is NOT for tasks that need review between them — use sequential workflow for that.

## Pattern

```python
# ALL tasks are independent — no shared files, no dependencies
delegate_task(tasks=[
    {
        "goal": "Task A: specific goal",
        "context": "All info subagent needs. No shared state with B or C.",
        "toolsets": ["terminal", "file"]
    },
    {
        "goal": "Task B: specific goal",
        "context": "All info subagent needs. Independent of A and C.",
        "toolsets": ["terminal", "file"]
    },
    {
        "goal": "Task C: specific goal",
        "context": "All info subagent needs. Independent of A and B.",
        "toolsets": ["file"]  # lighter toolset if less work needed
    }
])
# Results returned as array — process all, then proceed
```

## Real Example (Migration Session)

Three parallel tasks for Hermes installation migration:
1. **Self-evolution plugin** — update paths in plugin files (terminal + file)
2. **Knowledge Cube** — read script, import 619 experiences from state.db (terminal + file)
3. **Fler Engine** — analyze 509 sessions for atmosphere (terminal + file)

All three touched different directories and files. No conflicts. All completed in one delegate_task call.

Then two more in second batch:
4. **Salon bot + Crimea bots** — check readiness, fix configs (terminal + file)
5. **Insights integration** — update branches.yaml and MEMORY.md (file only)

## Rules

- **Max 3 concurrent** (Hermes config limit). If 4+ tasks, split into batches of 3.
- **Each subagent must be fully self-contained** — pass ALL context in the `context` field. Subagents have NO memory of your conversation.
- **Verify results after return** — subagent claims may be wrong. Check file existence, DB counts, etc.
- **Don't mix heavy + light** in same batch if the light one finishes fast and you need its result before the heavy one.
- **Toolset selection matters** — give each subagent only what it needs. `["file"]` for read-only analysis, `["terminal", "file"]` for builds/installs.

## vs Sequential Review Pattern

| Aspect | Parallel Batch | Sequential Review |
|--------|---------------|-------------------|
| Tasks | Independent | Dependent (A before B) |
| Review | After all complete | After each task |
| Speed | Fast (parallel) | Slow (serial) |
| Use case | Migration, batch ops | Code implementation |
| Risk | Higher (no mid-flight check) | Lower (catch early) |

## Anti-patterns

- **DON'T** parallelize tasks that write to the same file
- **DON'T** parallelize if task B depends on task A's output
- **DON'T** forget to pass full context — subagents are stateless
- **DON'T** trust subagent output blindly — verify with tools
