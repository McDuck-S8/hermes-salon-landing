# exfiltration-guard — Skill

## Purpose
Exfiltration Guard pattern from AI-First Business Playbook — scans all outbound content for API keys, secrets, PII before transmission. Blocks and logs.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Exfiltration Guard pattern from AI-First Business Playbook — scans all outbound content for API keys, secrets, PII before transmission
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
| `scripts/` | Helper scripts (2 files) |