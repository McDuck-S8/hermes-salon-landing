# DOX (AGENTS.md) Tree Initialization

## When to Use
- Setting up a new project with DOX framework
- Adding DOX to an existing codebase that lacks AGENTS.md hierarchy
- Rebuilding a stale DOX tree after major restructuring

## What is DOX
DOX is a self-documenting AGENTS.md hierarchy (from [agent0ai/dox](https://github.com/agent0ai/dox)). AGENTS.md files serve as binding work contracts for their subtrees — the agent reads them before editing any file.

## Parallel Scanning Workflow

For large codebases (20+ directories), parallelize the scan with `delegate_task`:

### Step 1: Get directory tree
```bash
find <project-root> -maxdepth 2 -type d ! -path '*/.git/*' ! -path '*node_modules*' ! -path '*__pycache__*' | sort
```

### Step 2: Parallel scan in 3 batches
Split directories into 3 groups and send each to a subagent:

```
delegate_task(tasks=[
  {goal: "Scan agent/, hermes_cli/ — list key files, identify purpose, note subdirs", toolsets: ["terminal", "file"]},
  {goal: "Scan tools/, gateway/, cron/, plugins/ — list key files, identify purpose", toolsets: ["terminal", "file"]},
  {goal: "Scan providers/, tests/, scripts/, apps/, acp_adapter/ — list key files", toolsets: ["terminal", "file"]}
])
```

Each subagent returns a concise directory summary. Use these to populate child AGENTS.md files.

### Step 3: Write files
Use `execute_code` to batch-write all AGENTS.md files in one call:

```python
from hermes_tools import write_file
write_file("project/AGENTS.md", root_content)
write_file("project/agent/AGENTS.md", agent_content)
# ... etc
```

### Step 4: Verify
```bash
find <project-root> -name "AGENTS.md" | sort
```

## DOX File Template

Every child AGENTS.md follows this structure:

```markdown
# <dir>/ — <Short Purpose>

## Purpose
One paragraph: what this directory does.

## Ownership
Who/what owns this code.

## Local Contracts
- Entry points, key files, APIs

## Work Guidance
- Architecture notes, patterns, conventions

## Verification
- How to test this directory

## Child DOX Index
| Dir | Purpose |
|-----|---------|
| `subdir/` | What it does |
```

## Pitfalls
- **Don't create AGENTS.md for tiny directories** (2-3 files) — describe them in the parent's Child DOX Index instead
- **Don't duplicate rules** across many files — broad rules go in the parent, concrete details in the child
- **Don't document diary entries** — AGENTS.md records stable contracts, not "what we did today"
- **Root AGENTS.md must have the Child DOX Index** — this is how the agent knows which child to read before editing a file
