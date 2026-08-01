# Skill Forge — Architecture

> **Registry + Quality Gates for Agent Skills. Built by agents, for agents.**

## Problem

The current skill ecosystem is a flat directory (`~/.hermes/skills/`) with JSONL-based gap tracking. As autonomous agents proliferate (cron jobs, delegated agents, self-improvers), three problems emerge:

1. **Concurrency** — multiple agents writing to `skill_gaps.jsonl` simultaneously cause data loss
2. **Quality** — no automated validation of skill format, required sections, or references
3. **Discovery** — no searchable index, dependency tracking, or versioning

## Solution

A CLI-first SQLite-backed skill registry with:

- **Atomic writes** — SQLite transactions handle concurrent agents safely
- **Quality gates** — validate frontmatter, check required sections, link references
- **Versioning** — skills have versions, changelog, and audit history
- **Search** — full-text search across all skills
- **Publish/install** — agents can publish new skills and install existing ones

## Architecture

```
CLI (`forge`)                        ← entry point
  ├── registry (SQLite)              ← skill index + metadata
  ├── validator (quality gates)      ← frontmatter, structure, linting
  ├── indexer (FTS5)                 ← full-text search
  └── importer (Hermes→Forge)        ← migrate existing skills

Storage: ~/.hermes/skill-forge/forge.db
Skills: flat files in ~/.hermes/skills/ (unchanged — Forge indexes them)
```

## Database Schema

```sql
-- Core skills table
CREATE TABLE skills (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    category TEXT,
    version TEXT,
    path TEXT NOT NULL,           -- absolute path to SKILL.md
    installed_at TEXT,
    updated_at TEXT,
    status TEXT DEFAULT 'active'  -- active|deprecated|broken
);

-- Quality check results
CREATE TABLE quality_checks (
    id INTEGER PRIMARY KEY,
    skill_id INTEGER REFERENCES skills(id),
    check_name TEXT,              -- frontmatter|structure|links|deps
    passed INTEGER,
    details TEXT,
    checked_at TEXT
);

-- Skill versions (tracking changes)
CREATE TABLE versions (
    id INTEGER PRIMARY KEY,
    skill_id INTEGER REFERENCES skills(id),
    version TEXT,
    changelog TEXT,
    published_at TEXT
);

-- Dependencies between skills
CREATE TABLE dependencies (
    skill_id INTEGER REFERENCES skills(id),
    depends_on_name TEXT,          -- skill name (not ID — circular-safe)
    type TEXT DEFAULT 'reference'  -- reference|script|template|model
);

-- Full-text search
CREATE VIRTUAL TABLE skills_fts USING fts5(
    name, category, description, body
);
```

## CLI Commands

```
forge publish <path>              Register a skill in the registry
forge install <name>              Symlink/install a skill
forge search <query>              Full-text search
forge validate [<name>]           Run quality gates (all or specific)
forge list [--category <cat>]     List registered skills
forge status                      Registry health overview
forge import-hermes               Migrate existing Hermes skills
```

## Quality Gates

1. **Frontmatter** — required YAML: name, description, version
2. **Structure** — has ## sections: Trigger, Steps/Usage
3. **Links** — all file references resolve
4. **Dependencies** — referenced tools exist in PATH
5. **Lint** — markdown validity, no broken links

## MVP Scope

- [x] SQLite schema + registry CRUD
- [x] Import script for existing Hermes skills (149 imported)
- [x] `forge validate` — frontmatter + structure checks
- [x] `forge search` — FTS5 search
- [x] `forge list` — categorized listing
- [x] `forge status` — health overview
- [x] `forge inspect` — skill detail view
- [x] `forge prune` — remove stale skills
- [x] `forge export` — JSON dump
- [x] `forge watch` — auto-reimport (with --once for cron)
- [x] CLI with Click

## Post-MVP (shipped in v0.1.0)

These were planned as "next phase" but shipped in the initial release:

- [x] `forge prune` — removes skills whose files no longer exist
- [x] `forge export` — full JSON export with quality checks
- [x] `forge watch --once` — cron-friendly auto-reimport
