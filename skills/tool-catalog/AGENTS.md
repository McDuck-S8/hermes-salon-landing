# tool-catalog — Skill

## Purpose
** loaded at session boot. Agent MUST check this before deciding how to work.**

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: ** loaded at session boot
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
| `references/skill-index.md` | Полный индекс 430 ценных скиллов по категориям — читать ПЕРЕД задачей |