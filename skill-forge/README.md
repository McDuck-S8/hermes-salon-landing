# Skill Forge

[![Tests](https://img.shields.io/badge/tests-89%20passed-brightgreen)]()
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Agent skill registry with quality gates. Import, validate, search, and manage 149+ Hermes skills.**

## Why

The current system — flat files in `~/.hermes/skills/` and a shared `skill_gaps.jsonl` — breaks when multiple autonomous agents write concurrently. Skill Forge replaces JSONL collision with SQLite atomicity:

- **Concurrent-safe** — WAL mode, multiple agents can register/check simultaneously
- **Quality gates** — validate YAML frontmatter, required sections, and semver before skills go live
- **FTS5 search** — find skills by name, category, description, or body content
- **Auto-import** — `forge watch --once` keeps the registry synced (perfect for cron)
- **Export** — JSON dump for backups, analysis, or migration

## Quick Start

```bash
git clone https://github.com/vystartasv/skill-forge
cd skill-forge
pip install -e ".[dev]"
forge import-hermes    # registers all your Hermes skills
forge status           # see what you have
```

## Features

- **10 CLI commands:** import-hermes, register, validate, search, list, status, inspect, prune, export, watch
- **SQLite + FTS5:** atomic transactions, full-text search, cascade deletes
- **Quality gates:** frontmatter (required YAML + semver) + structure (section presence)
- **Content-aware sync:** detects changes, skips unchanged, records version history
- **Live:** 149 imported skills, 89 tests, 0.24s suite

## Commands

```
forge import-hermes              Scan ~/.hermes/skills/, register all
forge register <path>            Register a single SKILL.md
forge validate [--name <n>]      Quality gates (frontmatter + structure)
forge search <query>             Full-text search
forge list [--category <cat>]    Filtered listing
forge status                     Health overview
forge inspect <name>             Full detail + quality checks
forge prune                      Remove stale entries
forge export [-o <file>]         JSON dump
forge watch [--once] [--interval <s>]  Auto-reimport
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [Implementation Plan](docs/implementation-plan.md)
- [Changelog](CHANGELOG.md)

## License

MIT — see [LICENSE](LICENSE)
