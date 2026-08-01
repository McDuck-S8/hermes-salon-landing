# Full System Review Workflow

## Pattern (from 2026-06-30 session)

User asked: "запуск проверки на всю систему для этого есть ревьювер"

### Correct Flow

1. Create an epic bead summarizing the system to review:
   ```bash
   bd create "System Review: {scope}" --type epic -d "{what to review}"
   ```

2. Run lavra-eng-review on the epic:
   ```
   /lavra-eng-review {epic_id}
   ```
   This dispatches 4 parallel reviewers (architecture, simplicity, security, performance)
   and creates child beads for each finding.

3. After review completes, run lavra-work on the epic:
   ```
   /lavra-work {epic_id}
   ```
   This auto-routes to fix all child beads.

### Incorrect Flow (what happened)

- Agent dispatched generic delegate_task subagents as "reviewers"
- Agent manually created 14 beads with `bd create`
- Agent manually fixed 6 issues via subagents
- User: "не надо бидс от тебя!!!!"

### Key Lesson

The Lavra skills (lavra-eng-review, lavra-brainstorm) have their own bead creation
and decomposition logic. Do NOT bypass them by manually creating beads.

## What lavra-eng-review does

- Takes an epic bead ID
- Reads epic + all child beads
- Dispatches 4 parallel review agents:
  1. architecture-strategist
  2. code-simplicity-reviewer
  3. security-sentinel
  4. performance-oracle
- Synthesizes findings into categorized report
- Logs key findings as knowledge comments
- Presents TODOs for deferrable items

## What lavra-brainstorm does

- Takes a spec or feature description
- Creates a decomposition plan
- Creates child beads with dependencies
- Chains beads with `bd dep add`

## For full system reviews without an existing epic

1. Create epic: `bd create "System Review: {area}" --type epic -d "{scope}"`
2. Run: `/lavra-eng-review {epic_id}`
3. Run: `/lavra-work {epic_id}`

Do NOT:
- Dispatch ad-hoc reviewer subagents
- Manually create individual beads for each finding
- Fix issues directly instead of through lavra-work
