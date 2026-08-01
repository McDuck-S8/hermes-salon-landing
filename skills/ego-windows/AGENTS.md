# ego-windows — Skill

## Purpose
Windows analog of ego-lite: parallel browser Spaces, JS tool API for agents, Chrome profile inheritance.
Uses existing Hermes stack: BrowserClaw MCP (localhost:9010), BrowserOS MCP (localhost:9003), 


## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: browser, automation, parallel, spaces, agent, cdp, playwright
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Windows analog of ego-lite: parallel browser Spaces, JS tool API for agents, Chrome profile inheritance
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
| `scripts/` | Helper scripts (4 files) |