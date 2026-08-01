# Session Context Pattern

When starting a new session, save context to survive compaction.

## File Location
`cache/session_context_YYYY-MM-DD.md`

## Template
```markdown
# Session Context: YYYY-MM-DD

## What Was Built
1. [Component]: [what it does]
2. ...

## Architecture Decisions
- [Decision]: [reasoning]
- ...

## Remaining
- [Task]: [status/blocker]
- ...
```

## When to Create
- After building 3+ components in one session
- After making architectural decisions
- Before session ends (if possible)

## When to Read
- At session start (if MEMORY.md references it)
- When user asks "what did we do last time?"
- When resuming work on a partially-completed task

## Pitfalls
- **Don't create for trivial sessions** — only for 5+ tool calls or architectural changes
- **Don't let it grow > 2KB** — if too long, summarize and archive
- **Date in filename** — old contexts become historical reference, not active state
