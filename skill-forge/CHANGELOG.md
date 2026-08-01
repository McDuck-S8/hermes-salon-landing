# Changelog

All notable changes to Skill Forge.

## [0.1.0] — 2026-05-04

### Added
- SQLite registry with WAL mode, FTS5 search, foreign key cascading
- Hermes skill importer — scans `~/.hermes/skills/`, detects content changes
- Quality gates: frontmatter validator (YAML + semver) + structure validator (section checks)
- CLI: `import-hermes`, `register`, `validate`, `search`, `list`, `status`, `inspect`
- Auto-reimport: `forge watch` with `--once` flag for cron jobs
- Stale cleanup: `forge prune` removes skills whose files were deleted
- JSON export: `forge export` dumps full registry with quality checks
- 89 tests, all passing (0.24s)
