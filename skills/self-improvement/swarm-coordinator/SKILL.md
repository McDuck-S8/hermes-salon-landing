---
name: swarm-coordinator
description: Coordinate multiple agents by splitting work into research, synthesis, implementation, and verification, assigning ownership, and keeping the coordinator focused on integration rather than raw exploration.
---

# Swarm Coordinator

Use this skill when a task is large enough that one coordinator and several bounded workers are more reliable than one monolithic agent loop.

## Use It For

- broad codebase exploration
- cross-file bug hunts
- parallel review or research passes
- tasks that benefit from explicit synthesis before implementation

## Avoid It For

- trivial edits
- urgent blocking steps that are faster to do locally
- delegation with no ownership boundaries

## Quick Start

Generate a task-board skeleton:

```bash
python3 {baseDir}/scripts/task_board.py --goal "Investigate flaky CI failure" --worker research --worker implementation --worker verification
```

Then use the coordinator prompt in [references/prompt-template.md](./references/prompt-template.md).

## Core Rule

The coordinator should own planning, routing, and synthesis. Workers should own bounded execution.

## Orchestration Pattern (2026-06-28)

When the coordinator needs to execute work (not just route to workers), follow this pattern:

### 1. Todo List for Tracking
```python
todo([
    {"id": "orch-1", "content": "Create generator template", "status": "in_progress"},
    {"id": "orch-2", "content": "Run generator on 5 niches", "status": "pending"},
    {"id": "orch-3", "content": "Verify each site visually", "status": "pending"},
])
```

### 2. execute_code for File Creation (NOT subagents)
Subagents on free models timeout (600s) on complex file creation. Use execute_code instead:
```python
from hermes_tools import write_file
# One execute_code call per site (3 files: html + css + js)
# Total: 5 calls × 3 files = 15 files in ~60 seconds
write_file("demos/salon/index.html", "...")
write_file("demos/salon/css/style.css", "...")
write_file("demos/salon/js/main.js", "...")
```

### 3. Subagents Only for Analysis/Research
Subagents work well for:
- Research and analysis
- Code review
- Bug investigation
- NOT for batch file creation (they timeout)

### 4. Verify After Creation
```bash
# Check files exist and have content
for d in salon auto clinic bakery funeral; do
    echo "=== $d ===" && wc -c demos/$d/index.html demos/$d/css/style.css demos/$d/js/main.js
done
```

### 5. Report + Continue
After completing a task, IMMEDIATELY start the next one. Don't wait for praise.
```
# WRONG: "Готово. 5 сайтов создано." *waits*
# RIGHT: "Готово. Следующая задача: ..."
```

### Why This Pattern Works
- execute_code: 60s for 15 files (reliable, no timeout)
- Subagents: 600s+ and timeout (unreliable for file creation)
- Todo list: tracks progress, prevents "what should I do next?"
- Verification: catches errors before user sees them
- Report + continue: autonomous operation, no praise-seeking

## Supporting Files

- Prompt template: [references/prompt-template.md](./references/prompt-template.md)
- Source notes: [references/source-notes.md](./references/source-notes.md)
- Helper script: `python3 {baseDir}/scripts/task_board.py ...`
