---
name: dream-memory
description: Consolidate recent logs, sessions, and existing memory files into durable topic memories, normalize dates, prune stale entries, and keep MEMORY.md short enough for prompt use.
---

# Dream Memory

Use this skill when you want a deliberate memory-consolidation pass instead of storing more raw notes.

This bundle is intentionally portable. It borrows the workflow shape from Claude Code's dream system, but it does not depend on Claude Code internals.

## Use It For

- nightly or manual memory cleanup
- merging overlapping memory notes
- normalizing relative dates into absolute dates
- pruning stale or contradicted memories
- keeping `MEMORY.md` small and index-like

## Avoid It For

- saving a single new memory from the current turn
- persisting code facts that should be re-read from source
- replacing plans, task boards, or issue trackers

## When to Run

- After context compaction
- After 5+ consecutive completed tasks
- Daily via cron (0 3 * * *)
- When memory tree has stale entries (>7 days without update)
- **When MEMORY.md has < 20 lines** — CRITICAL: agent starts blind

## Quick Start

Inspect a memory directory before running the consolidation prompt:

```bash
python3 {baseDir}/scripts/dream_memory.py --memory-root /path/to/memory --transcripts-dir /path/to/transcripts
```

Then use the portable prompt in [references/prompt-template.md](./references/prompt-template.md).

## Workflow

1. Inspect `MEMORY.md`, topic files, and recent logs or transcripts.
2. Identify durable facts worth keeping.
3. Merge into topic files instead of creating near-duplicates.
4. Remove stale or contradicted memory.
5. Rewrite `MEMORY.md` as a concise index.

## Pitfalls

- **Lavra JSONL != Dream Markdown**: Lavra memory tree (`data/lavra-memory/`) stores knowledge as `knowledge.jsonl`, NOT Markdown files. dream-memory script expects `MEMORY.md` + `*.md` topic files. These are separate systems — do NOT point dream-memory at the Lavra directory. Solution: create a dedicated `data/dream-memory/` tree with proper Markdown structure.
- **Topic files go in root**: The script scans `memory_root/*.md` — topic files must be directly in the memory root, not in a `topics/` subdirectory. If topic_files comes back empty but you put files in `topics/`, move them up.
- **MEMORY.md is an index**: Keep it under 200 lines / 25KB. It should reference topic files, not dump content.

## Rules

- `MEMORY.md` is an index, not a content dump.
- Prefer topic merges over new file creation.
- Convert relative dates to absolute dates.
- Do not store code-state facts that can drift.

## Supporting Files

- Prompt template: [references/prompt-template.md](./references/prompt-template.md)
- Source notes: [references/source-notes.md](./references/source-notes.md)
- Auto-trigger setup: [references/auto-trigger-setup.md](./references/auto-trigger-setup.md)
- Helper script: `python3 {baseDir}/scripts/dream_memory.py ...`
