# Skill Forge — Implementation Plan

## Execution Order (dependency-aware)

```
Phase 1: CLI scaffold           (task 30) — package structure, Click entry point
Phase 2: SQLite schema + CRUD   (task 28) — forge.db, Registry class
Phase 3: Hermes importer        (task 29) — scan ~/.hermes/skills/
Phase 4: Quality gates          (task 31+32) — frontmatter + structure validators
Phase 5: Search + Display       (task 33+34) — FTS5, list, status
```

Each phase: plan → write code → write tests → run tests → commit.

## File Structure

```
src/skill_forge/
├── __init__.py          # Package init, __version__ = "0.1.0"
├── cli.py               # Click CLI entry point
├── registry.py          # SQLite schema + CRUD operations
├── importer.py          # Scan + import Hermes skills
├── validator.py         # Quality gate functions
├── search.py            # FTS5 search
└── display.py           # List/status formatting

tests/
├── __init__.py
├── test_registry.py     # Schema creation, CRUD, concurrent writes
├── test_importer.py     # Import with real skill files
├── test_validator.py    # Frontmatter, structure, link checks
├── test_search.py       # FTS5 queries
├── test_cli.py          # Integration tests via Click's CliRunner
└── conftest.py          # temp db fixture

pyproject.toml           # Build config
README.md
```

## Phase 1: CLI Scaffold

**pyproject.toml:**
```toml
[project.scripts]
forge = "skill_forge.cli:main"
```

**cli.py:**
- `@click.group()` root
- Subcommands: import-hermes, validate, search, list, status
- Each subcommand delegates to the appropriate module
- `--db-path` option for custom database location (default: ~/.hermes/skill-forge/forge.db)

## Phase 2: Registry

**registry.py — `Registry` class:**
- `__init__(db_path)` — creates tables if not exist, enables WAL mode
- `add_skill(name, category, version, path, body, description="")` → skill_id
- `get_skill(name)` → dict or None
- `get_skill_by_id(id)` → dict
- `list_skills(category=None, status=None)` → list[dict]
- `update_skill_status(name, status)` → bool
- `record_quality_check(skill_id, check_name, passed, details)` → id
- `get_latest_checks(skill_id)` → list[dict]
- `update_fts(skill_id, name, category, description, body)` — FTS5 maintenance
- `register_skill(path)` — convenience: parse SKILL.md, add to registry (used by `forge register`)

**CLI additions:**
- `forge register <path>` — register a single skill file (Phase 2)
- `forge inspect <name>` — show full details for one skill (Phase 5)

**Schema** (from architecture doc, plus FTS5 triggers):
```sql
CREATE TABLE IF NOT EXISTS skills (...);
CREATE TABLE IF NOT EXISTS quality_checks (...);
CREATE TABLE IF NOT EXISTS versions (...);
CREATE TABLE IF NOT EXISTS dependencies (...);
CREATE VIRTUAL TABLE IF NOT EXISTS skills_fts USING fts5(...);
```

Add triggers to keep FTS in sync on INSERT/UPDATE/DELETE.

## Phase 3: Importer

**importer.py:**
- `import_hermes_skills(registry, skills_dir="~/.hermes/skills")` → (imported, skipped, failed)
- Scan `skills_dir` for `*/SKILL.md` files
- Parse YAML frontmatter (delimited by `---`)
- Extract: name, description, version, category
- Read full body for FTS indexing
- Register in database, record version
- Skip duplicates (same name + path)
- Report: X imported, Y skipped, Z failed

## Phase 4: Quality Gates

**validator.py:**
- `validate_frontmatter(skill_path)` → (passed, details)
  - YAML parse succeeds
  - Required fields: name, description, version
  - Version matches semver pattern
- `validate_structure(skill_path)` → (passed, details)  
  - Has ## sections
  - Required: one of "Trigger" or "Usage" or "Steps"
  - Check for empty sections
- `validate_skill(skill_path)` → list of check results
- `validate_all(registry)` → aggregate report

## Phase 5: Search + Display

**search.py:**
- `search_skills(registry, query)` → list of matching skills
- Uses FTS5 MATCH with ranking

**display.py:**
- `format_list(skills)` → table output
- `format_status(registry)` → health overview
  - Count by status
  - Count by category
  - Skills failing quality gates
  - Recently updated

## Testing Strategy

- **Unit tests:** Each module tested with in-memory SQLite
- **Integration tests:** CLI commands via Click's CliRunner
- **Fixtures:** conftest.py with temp database factory
- **No real ~/.hermes/skills/** — use temp directory with test skill files
- **Target:** 50+ tests, < 5s runtime

## Edge Cases

1. Empty skills directory → graceful "0 imported"
2. Corrupt YAML frontmatter → skip, report failure
3. Skill without SKILL.md → skip directory
4. Duplicate imports → skip, report
5. Concurrent writes → SQLite handles (WAL mode)
6. Very large skill body → FTS5 handles up to 1GB
7. Database doesn't exist → auto-create on first use
