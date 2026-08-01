# structured-context-compressor — Skill

## Purpose
Compress a long agent conversation into a nine-part continuation summary that preserves request, files, errors, user messages, current work, and the next aligned step.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Compress a long agent conversation into a nine-part continuation summary that preserves request, files, errors, user messages, current work, and the next aligned step
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (2 files) |
| `scripts/` | Helper scripts (1 files) |