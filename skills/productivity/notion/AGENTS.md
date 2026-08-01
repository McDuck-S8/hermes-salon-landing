# notion — Skill

## Purpose
Notion API + ntn CLI: pages, databases, markdown, Workers. Talk to Notion two ways — ntn CLI (preferred on macOS/Linux) or HTTP + curl (cross-platform, default on Windows). Same integration token works for both.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: Notion API tasks (pages, databases, markdown, Workers, file uploads), Notion integration setup, ntn CLI usage
- **Tags**: Notion, Productivity, Notes, Database, API, CLI, Workers
- **Required Tools**: standard Hermes tools (terminal, read_file, write_file, search_files, web_search, web_extract)
- **Config**: config.yaml in skill dir (optional); NOTION_API_KEY env var required
- **Prerequisites**: NOTION_API_KEY in `${HERMES_HOME:-~/.hermes}/.env`; target pages/databases shared with the integration

## Work Guidance
**When to use**: Any Notion interaction — reading/writing pages, querying databases, searching, file uploads, creating Workers (syncs, webhooks, agent tools).

**Common patterns**:
- **Read page as markdown** (agent-friendly): `ntn api v1/pages/{id}/markdown` or `curl /markdown` endpoint
- **Create page from markdown**: Single `ntn api v1/pages` call with `markdown` body param, or curl POST with markdown field
- **Query database**: `ntn api v1/data_sources/{id}/query` (API 2025-09-03 uses data_sources, not databases)
- **File uploads**: `ntn files create < file` (one-liner) vs 3-step HTTP flow
- **Workers** (Business/Enterprise): `ntn workers new`, edit `src/index.ts`, `ntn workers deploy` — syncs, tools, webhooks

**Decision tree (Path A vs B)**:
- macOS/Linux + ntn installed → Path A (ntn CLI)
- Windows or no ntn → Path B (curl with `Notion-Version: 2025-09-03`)
- Always share target pages with the integration first (404 otherwise)

**Anti-patterns**:
- Using without reading SKILL.md first
- Forgetting `Notion-Version: 2025-09-03` header on HTTP calls
- Not sharing pages/databases with the integration
- Using `database_id` for queries (use `data_source_id` in API 2025-09-03)
- Embedding tokens in command output (use `-s` with curl, env vars)

## Verification
- Load SKILL.md and validate frontmatter (name, version, tags, env_vars)
- Check references/ directory exists
- Verify NOTION_API_KEY is configured in Hermes env
- Test with `ntn api v1/users` or `curl /v1/users` to confirm auth
- No test scripts in scripts/ directory currently

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Notion API reference docs, ntn CLI reference, Workers docs |
| `scripts/` | (none currently) |
| `templates/` | (none currently) |
| `config.yaml` | Optional skill config |