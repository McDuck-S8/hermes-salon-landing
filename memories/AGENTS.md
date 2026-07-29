# AGENTS.md — memories/

## Purpose

Persistent memory storage for the Hermes agent system. Contains the agent's long-term memory and user profile that persist across sessions.

## Ownership

Core module — read/write by autonomous agent, self-improvement loop, and manual edits.

## Files

| File | Purpose | Lock |
|---|---|---|
| `MEMORY.md` | System architecture, cron loop, known issues, session history | `.lock` file present |
| `USER.md` | User preferences, communication style, project context | `.lock` file present |

## Local Contracts

- **Lock files**: `.lock` files exist alongside both `.md` files. Respect lock state before writing.
- **Format**: Markdown with structured sections (headers, tables, bullet lists).
- **Encoding**: UTF-8. Cyrillic content is normal.
- **Size**: Keep MEMORY.md under 200 lines. Archive old session history if it grows too large.

## Work Guidance

- Read `MEMORY.md` before any autonomous session to load current system state.
- Write to `MEMORY.md` after significant system changes (new modules, cron jobs, architecture shifts).
- Write to `USER.md` when the user explicitly corrects preferences or provides new context.
- Do NOT auto-generate content here — every entry must come from real events or user input.
- Use `scripts/hermes_hooks.py` for automated memory updates (preferred over manual edits).

## Verification

- After editing, verify both files are valid Markdown (no broken headers, tables render correctly).
- Check that `.lock` files are not stale (remove orphan locks).

## Child DOX Index

No subdirectories — flat structure.
