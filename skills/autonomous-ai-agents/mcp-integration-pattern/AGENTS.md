# mcp-integration-pattern — Skill

## Purpose
Standardized pattern for integrating external MCP servers into Hermes agents. Covers: server config, tool discovery, authentication, fallback, and skill  wrappers that expose MCP tools as native Herme

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Standardized pattern for integrating external MCP servers into Hermes agents
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (1 files) |