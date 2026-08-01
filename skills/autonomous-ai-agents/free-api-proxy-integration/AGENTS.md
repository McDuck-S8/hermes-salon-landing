# free-api-proxy-integration — Skill

## Purpose
Integrate free browser-based API proxies (Qwen, DeepSeek, etc.) into Hermes as custom_providers. Covers repo discovery, installation, browser auth, Hermes config, and troubleshooting.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Integrate free browser-based API proxies (Qwen, DeepSeek, etc
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (6 files) |
| `templates/` | Templates (1 files) |