# api-integration — Skill

## Purpose
Pattern for integrating external API/SDK services into Hermes as usable scripts/tools. Covers: install SDK, configure credentials, explore API structure, create wrapper with error handling, test endpo

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: api, integration, sdk, hermes-tool, service-wrapper
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Pattern for integrating external API/SDK services into Hermes as usable scripts/tools
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (3 files) |
| `templates/` | Templates (1 files) |