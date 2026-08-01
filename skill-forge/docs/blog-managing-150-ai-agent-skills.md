# Managing 150+ AI Agent Skills at Scale — What Broke, What I Built

*By Vilius Vystartas | May 2026*

I run a lot of AI agents. Not chatbots — autonomous agents. Cron jobs that monitor my infrastructure every hour. Self-improvers that analyze past sessions and encode learnings. Delegated coders that build features while I sleep. Together they load from a library of 153 reusable skills — structured procedures that tell an agent how to do something specific, from sending iMessages to debugging SPFx builds.

The system worked fine when I had 20 skills and one agent. It started breaking when the numbers climbed.

---

## The Problem That Forced My Hand

Here's the setup: each skill lives as a `SKILL.md` file in `~/.hermes/skills/`. When an agent loads a skill and discovers it's broken, missing steps, or out of date, it records the problem in a shared `skill_gaps.jsonl` file. Later, I review the gaps and fix the skills.

This is fine when one agent writes to the file at a time.

It stops being fine when three autonomous agents — say, a 2am cron job, a self-improvement loop, and a code review agent — all try to write to the same JSONL file within the same second.

**Concurrent writes collide. Lines get truncated. Data vanishes.**

I lost track of which skills needed fixing. Agents kept loading broken skills silently because the gap reporting was unreliable. Worse, I had no search — finding "that one skill about PyPI releases" meant grepping a directory tree and hoping the frontmatter was consistent.

The flat-file approach doesn't scale past a few dozen skills. I had 153.

---

## What I Built: Skill Forge

**Skill Forge** is a SQLite-backed skill registry with quality gates, full-text search, and concurrent-safe writes. It replaces the broken JSONL pipeline with atomic transactions. It doesn't move your skills — it indexes them in place.

Think of it as `pip` for agent skills, but local-first, with validation before installation.

```
$ forge status

Skill Forge Registry Status
===========================
  Database: ~/.hermes/skill-forge/forge.db
  Total skills: 153

  By category:
    mlops: 12     devops: 8     creative: 15
    career: 3     research: 7   (uncategorized): 108

  Quality checks run: 306
  Skills with failures: 0 ✓
```

### Why SQLite?

Three reasons:

1. **WAL mode** — multiple agents can read and write simultaneously without locking each other out. Each agent gets its own connection with foreign-key enforcement. When two agents register different skills at the same time, both succeed. Atomic transactions, no corrupted state.

2. **FTS5** — full-text search over name, category, description, and body content. Finding "that skill about PyPI release classifiers" is `forge search "pypi classifier"` — instant, ranked results.

3. **Single file** — `forge.db` in `~/.hermes/skill-forge/`. No server process. No configuration. Backs up with `forge export`. Portable.

### Quality Gates That Catch Real Problems

Before Skill Forge, broken skills went undetected until an agent loaded them mid-task and hit a wall. Now every skill runs through two validation passes:

**Frontmatter validator** — catches missing YAML, absent required fields (name/description/version), and invalid semver strings. A skill with `version: "latest"` gets flagged. One with `version: "1.2.3"` passes.

**Structure validator** — checks for required sections: a description block, trigger conditions, and usage steps. A skill that's just a title and a broken shell command fails. One with proper `## Trigger`, `## Steps`, and `## Pitfalls` sections passes.

The first run on my 153 skills: 102 passed, 51 flagged. The flagged ones weren't bugs — they were real quality issues I'd been ignoring. Skills missing version numbers. Skills with no trigger conditions. Skills where the "Steps" section was one garbled paragraph.

I fixed 38 of them that afternoon. The other 13 are low-priority and tagged for later.

### CLI Commands That Match the Workflow

Ten commands, each solving a specific pain point:

```bash
forge import-hermes              # First run: scan ~/.hermes/skills/, register everything
forge register <path>            # Add a single skill
forge validate [--name <n>]      # Run quality gates on all or one skill
forge search <query>             # FTS5 over name + description + body
forge list [--category <cat>]    # Filtered listing
forge status                     # Health overview
forge inspect <name>             # Full detail + quality check history
forge prune                      # Remove stale entries (skill file deleted from disk)
forge export [-o <file>]         # JSON dump for backups or analysis
forge watch [--once] [--interval <s>]  # Auto-reimport on changes
```

The `watch` command is the cron workhorse. Drop this in a 30-minute cron job:

```bash
forge watch --once
```

It scans the skills directory, detects new/modified files (content hash, not timestamp), registers new ones, re-registers changed ones (version bump), and marks deleted skills as stale. One pass, everything synced.

### Architecture

The stack is deliberately minimal — Python 3.11, Click for the CLI, SQLite for storage, PyYAML for frontmatter parsing. No web framework, no message queue, no cloud dependency.

```
CLI (forge)                        ← Click entry point
  ├── registry (SQLite + WAL)      ← skill index + metadata
  ├── importer                     ← scan ~/.hermes/skills/ → register
  ├── validator                    ← frontmatter + structure checks
  └── FTS5 index                   ← full-text search

Storage:  ~/.hermes/skill-forge/forge.db  (single file)
Skills:   ~/.hermes/skills/                (unchanged — indexed in place)
```

Skills stay as flat `SKILL.md` files. Forge indexes them, validates them, searches them, and tracks their history — but it never moves or modifies them. Your existing automation continues working. Forge adds a layer on top.

### Tests and Quality

89 tests. Full suite runs in 0.26 seconds. Covers registry CRUD, importer (Hermes scanner + content-change detection), validators (frontmatter + structure, edge cases like empty files and missing YAML delimiters), CLI integration (prune, export, watch), and concurrent-write scenarios.

---

## What I Learned

**SQLite with WAL mode solves the concurrent-agent problem cleanly.** You don't need Postgres or Redis for this. Connection-level pragmas (`PRAGMA journal_mode=WAL`, `PRAGMA foreign_keys=ON`) and atomic transactions are enough when your write volume is hundreds per hour, not thousands per second.

**Quality gates catch real problems, not theoretical ones.** 51 of my 153 skills had issues I didn't know about — missing versions, malformed frontmatter, empty sections. Agents were loading these skills silently. The validator turned invisible problems into visible ones.

**Content-aware sync matters.** My first import skipped files that already existed in the registry by path. This meant I missed skills that had been modified but not renamed. Switching to content-hash comparison caught 12 modified skills on the next import.

---

## Get It

- **Repo:** [github.com/vystartasv/skill-forge](https://github.com/vystartasv/skill-forge)
- **License:** MIT
- **Stack:** Python 3.11+, Click, SQLite + FTS5, PyYAML

```bash
git clone https://github.com/vystartasv/skill-forge
cd skill-forge
pip install -e ".[dev]"
forge import-hermes
forge status
```

If you're running autonomous AI agents with persistent skill libraries — or if you're building agent infrastructure and wondering how to manage the growing pile of procedures — I'd love feedback on the schema design and quality gate approach.
