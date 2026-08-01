---
name: file-toolkit
description: "Unified file operations toolkit for Hermes: file-todos + file_ops patterns + read_file/write_file/patch/search_files best practices. One skill to load, all file engines at hand."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [file_ops, file_todos, read_write_patch, search, markdown, yaml, organization]
    related_skills: [file-todos, file_ops, terminal-patterns, command-patterns]
  skill_updated: "2026-07-24"
  created_by: "auto_patch_g007"
  component_skills:
    - file-todos
    - file_ops
---

# File Toolkit — Unified Interface

**One skill to load. All file operations engines. Zero context switching.**

This meta-skill wraps core file operation skills into a single loadable unit with a unified workflow.

## Quick Start

```python
# Load once, get all file engines
from hermes_tools import skill_view
skill_view("file_ops/file-toolkit")

# Now you have:
# - file-todos (markdown todos in todos/ directory)
# - file_ops patterns (read_file, write_file, patch, search_files)
# - Terminal patterns (for when you MUST use terminal)
# - Command patterns (for recurring command patterns)
```

## Component Skills Map

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| **file-todos** | Markdown todos in `todos/` with YAML frontmatter | Project tracking, development tasks, agent-human collaboration |
| **file_ops patterns** | read_file/write_file/patch/search_files best practices | ALL file operations — NEVER use terminal for these |

## Unified File Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. PLAN (file-todos)                                            │
│    • Create todos/todo-<feature>.md with YAML frontmatter       │
│    • Structure: id, content, status (pending/in_progress/done)  │
│    • One in_progress at a time, mark done immediately           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. READ (read_file) — ALWAYS FIRST                              │
│    • read_file(path, offset, limit) — NOT cat/head/tail         │
│    • Line numbers, pagination, auto-extract .ipynb/.docx/.xlsx  │
│    • Cannot read images/binary — use vision_analyze for images  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. SEARCH (search_files) — NOT grep/rg/find/ls                  │
│    • target='content': regex inside files (target='files' for names)│
│    • file_glob: '*.py' to filter                                │
│    • output_mode: 'content' (default) / 'files_only' / 'count'  │
│    • context lines for grep mode                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. EDIT (patch) — NOT sed/awk/echo                              │
│    • mode='replace': unique old_string → new_string             │
│    • mode='patch': V4A multi-file patches                       │
│    • Auto-runs syntax checks on .py/.json/.yaml/.toml           │
│    • ONLY NEW errors surfaced (pre-existing filtered)           │
│    • Include context lines for uniqueness                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. WRITE (write_file) — ONLY for NEW files                      │
│    • Creates parent dirs automatically                          │
│    • OVERWRITES entire file — use patch for edits               │
│    • Auto-syntax checks on linted languages                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. TRACK (file-todos)                                           │
│    • Update todo status: pending → in_progress → completed      │
│    • merge=false (replace) or merge=true (update by id)         │
│    • One in_progress at a time                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Commands Reference

### File Todos
```python
# Create/update todos
todo(todos=[
    {"id": "t1", "content": "Implement feature X", "status": "pending"},
    {"id": "t2", "content": "Write tests", "status": "pending"}
])

# Update single todo
todo(merge=True, todos=[{"id": "t1", "status": "in_progress"}])

# Mark complete
todo(merge=True, todos=[{"id": "t1", "status": "completed"}])
```

### Read File (PREFERRED)
```python
read_file("path/to/file.py", offset=1, limit=100)
# Returns: {"content": "1|line1\n2|line2...", "total_lines": N}
```

### Search Files (PREFERRED)
```python
# Content search
search_files(pattern="def my_function", file_glob="*.py", path="src/")

# File name search
search_files(pattern="*config*", target="files", path=".")

# With context
search_files(pattern="error", context=3, file_glob="*.log")
```

### Patch File (PREFERRED)
```python
patch(
    path="file.py",
    old_string="def foo():\n    return 1",
    new_string="def foo():\n    return 2"
)

# For multi-file
patch(mode="patch", patch="*** Begin Patch\n*** Update File: a.py\n@@\n-old\n+new\n*** End Patch")
```

### Write File (NEW FILES ONLY)
```python
write_file("new_file.py", "print('hello')")
```

## Anti-Patterns (from 105 file_ops entries, 68 failures = 65% failure rate)

| Anti-Pattern | Guard |
|--------------|-------|
| `cat file.txt` | **read_file** — line numbers, pagination, auto-extract |
| `grep -r "pattern"` | **search_files** — regex, context, filtering |
| `sed -i 's/x/y/g'` | **patch** — syntax checks, context uniqueness |
| `echo "content" > file` | **write_file** — creates dirs, syntax checks |
| `ls -la` | **search_files(target="files")** — sorted by mtime |
| `find . -name "*.py"` | **search_files(pattern="*.py", target="files")** |
| Multiple terminal calls for one edit | **patch** — atomic, verified |

## File Todo Format (todos/todo-<feature>.md)

```yaml
---
title: "Feature X Implementation"
created: "2026-07-24T10:00:00Z"
project: "hermes"
tags: [feature, backend, api]
---

# Feature X Implementation

## Tasks
- [ ] t1: Design API schema
- [ ] t2: Implement endpoint
- [ ] t3: Write tests
- [ ] t4: Update docs
```

## Integration with Knowledge Cube

```python
from scripts.event_evolution import on_task_complete

on_task_complete(
    content="File ops complete: created todo, read 5 files, patched 3, all tests pass.",
    tags=["file_ops", "file_todos", "patch", "success"],
    source="agent"
)
```

## Reference files

- `references/system-file-search.md` — es.exe для системного поиска файлов на Windows (вместо search_files)

## Verification Checklist

After using this toolkit:
- [ ] File todo created for the work
- [ ] All reads via `read_file` (not terminal)
- [ ] All searches via `search_files` (not grep)
- [ ] All edits via `patch` (not sed/awk)
- [ ] All new files via `write_file` (not echo/cat)
- [ ] Todo updated after each step
- [ ] KC entry created with tags

---

**Origin:** g-007 Unlock: file_ops (105 entries, 68 failures)
**Created:** 2026-07-24 via auto_patch_g007
**Source:** Knowledge Cube domain `file_ops` + `file-todos` skill