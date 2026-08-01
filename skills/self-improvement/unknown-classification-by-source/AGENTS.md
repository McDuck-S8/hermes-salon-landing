# unknown-classification-by-source — Skill

## Purpose
Классификация unknown записей Knowledge Cube не по содержанию (regex/keywords), а по source — трассировке происхождения. Превращает 660+ unknown в 0 за один прогон.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: knowledge-cube, classification, unknown, source-trace
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Классификация unknown записей Knowledge Cube не по содержанию (regex/keywords), а по source — трассировке происхождения
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