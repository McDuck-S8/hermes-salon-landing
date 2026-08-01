# pokemon-player — Skill

## Purpose
Play Pokemon via headless emulator + RAM reads.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: gaming, pokemon, emulator, pyboy, gameplay, gameboy
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Play Pokemon via headless emulator + RAM reads
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| (no child directories) | |