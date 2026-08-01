---
name: codebase-inspection
description: "Inspect codebases w/ pygount: LOC, languages, ratios."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [LOC, Code Analysis, pygount, Codebase, Metrics, Repository]
  skill_updated: "2026-07-24"
  stale_since: "2026-06-03"
  stale_days: 37
  very_stale: false
  updated_by: "auto_patch_g009"
    related_skills: [github-repo-management]
prerequisites:
  commands: [pygount]
---

# Codebase Inspection with pygount

Analyze repositories for lines of code, language breakdown, file counts, and code-vs-comment ratios using `pygount`.

## When to Use

- User asks for LOC (lines of code) count
- User wants a language breakdown of a repo
- User asks about codebase size or composition
- User wants code-vs-comment ratios
- General "how big is this repo" questions

## Prerequisites

```bash
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
```

## 1. Basic Summary (Most Common)

Get a full language breakdown with file counts, code lines, and comment lines:

```bash
cd /path/to/repo
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

**IMPORTANT:** Always use `--folders-to-skip` to exclude dependency/build directories, otherwise pygount will crawl them and take a very long time or hang.

## 2. Common Folder Exclusions

Adjust based on the project type:

```bash
# Python projects
--folders-to-skip=".git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache"

# JavaScript/TypeScript projects
--folders-to-skip=".git,node_modules,dist,build,.next,.cache,.turbo,coverage"

# General catch-all
--folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,vendor,third_party"
```

## 3. Filter by Specific Language

```bash
# Only count Python files
pygount --suffix=py --format=summary .

# Only count Python and YAML
pygount --suffix=py,yaml,yml --format=summary .
```

## 4. Detailed File-by-File Output

```bash
# Default format shows per-file breakdown
pygount --folders-to-skip=".git,node_modules,venv" .

# Sort by code lines (pipe through sort)
pygount --folders-to-skip=".git,node_modules,venv" . | sort -t$'\t' -k1 -nr | head -20
```

## 5. Output Formats

```bash
# Summary table (default recommendation)
pygount --format=summary .

# JSON output for programmatic use
pygount --format=json .

# Pipe-friendly: Language, file count, code, docs, empty, string
pygount --format=summary . 2>/dev/null
```

## 6. Interpreting Results

The summary table columns:
- **Language** — detected programming language
- **Files** — number of files of that language
- **Code** — lines of actual code (executable/declarative)
- **Comment** — lines that are comments or documentation
- **%** — percentage of total

Special pseudo-languages:
- `__empty__` — empty files
- `__binary__` — binary files (images, compiled, etc.)
- `__generated__` — auto-generated files (detected heuristically)
- `__duplicate__` — files with identical content
- `__unknown__` — unrecognized file types

## Stub / Placeholder Scanning

Find Python files that are stubs (placeholder modules that could distort system behavior):

```python
# scripts/_scan_stubs.py — scan scripts/ and plugins/ for stubs
import os

ROOT = "D:/Portable_Soft/hermes"  # adjust
DIRS_TO_SCAN = ['scripts', 'plugins']

stubs = []
for subdir in DIRS_TO_SCAN:
    base = os.path.join(ROOT, subdir)
    for dirpath, _, filenames in os.walk(base):
        if '__pycache__' in dirpath or '_archive' in dirpath:
            continue
        for f in filenames:
            if not f.endswith('.py'):
                continue
            path = os.path.join(dirpath, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                content = fh.read()
            lines = content.split('\n')
            non_empty = [l for l in lines if l.strip()]
            stripped = [l.strip() for l in non_empty
                        if not l.strip().startswith('#')
                        and not l.strip().startswith('"""')
                        and not l.strip().startswith("'''")]
            is_stub = False
            if len(non_empty) <= 2:
                is_stub = True
            elif all(l in ('pass',) or l.startswith('import ') or l.startswith('from ') for l in stripped):
                if len(stripped) <= 5:
                    is_stub = True
            if is_stub:
                stubs.append(path)
```

**What IS a stub:** file with only imports, `pass`, `return None`, or a single `raise NotImplementedError` — no real logic.

**What is NOT a stub:** empty `__init__.py` (normal Python package marker), files with comments/docstrings but no code (still valid), files with 10+ lines of real logic.

**Pitfall:** `__init__.py` files that are empty are NOT stubs — they are package markers. Flagging them wastes time. Only flag `__init__.py` if it contains imports of symbols that don't exist.

## Pitfalls

1. **Always exclude .git, node_modules, venv** — without `--folders-to-skip`, pygount will crawl everything and may take minutes or hang on large dependency trees.
2. **Markdown shows 0 code lines** — pygount classifies all Markdown content as comments, not code. This is expected behavior.
3. **JSON files show low code counts** — pygount may count JSON lines conservatively. For accurate JSON line counts, use `wc -l` directly.
4. **Large monorepos** — for very large repos, consider using `--suffix` to target specific languages rather than scanning everything.
