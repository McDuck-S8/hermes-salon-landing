# Getting Started — Skill Forge

> **Import, validate, and search 149 agent skills in under a second.**

## Install

```bash
git clone https://github.com/vystartasv/skill-forge
cd skill-forge
pip install -e ".[dev]"
```

## Quick Start

```bash
# Import your existing Hermes skills
forge import-hermes

# See what you have
forge status
forge list --category devops

# Search for a skill
forge search "PyPI release"

# Validate quality
forge validate

# Inspect a specific skill
forge inspect python-pypi-release

# Export for backup
forge export -o skills-backup.json
```

## Automated Import (Cron)

Run on a schedule to keep the registry in sync:

```bash
# One-shot import (for cron)
forge watch --once

# Or continuously watch for changes (every 5 min)
forge watch --interval 300
```

Hermes cron job setup:
```
hermes cron create "0 */6 * * *" "Run 'forge watch --once' to sync skill registry"
```

## Maintenance

```bash
# Remove skills whose files were deleted
forge prune
```

## Commands

| Command | Does |
|---------|------|
| `forge import-hermes` | Scan `~/.hermes/skills/`, register all skills |
| `forge register <path>` | Register one SKILL.md |
| `forge validate` | Quality gates (frontmatter + structure) |
| `forge search <q>` | Full-text search |
| `forge list` | List by category/status |
| `forge status` | Health overview |
| `forge inspect <n>` | Full detail + latest checks |
| `forge prune` | Remove stale entries |
| `forge export` | JSON dump |
| `forge watch` | Auto-reimport |

## Architecture

SQLite + WAL (concurrent-safe), FTS5 (full-text), Click (CLI).  
Skills stay in `~/.hermes/skills/` — Forge indexes them, never moves them.  
Database: `~/.hermes/skill-forge/forge.db`
