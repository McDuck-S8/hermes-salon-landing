# closed-loop-autonomy — Skill

## Purpose
Принцип замкнутого контура: каждый producer имеет consumer, каждый сигнал ведёт к действию. Никаких мёртвых дыр в пайплайне.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Принцип замкнутого контура: каждый producer имеет consumer, каждый сигнал ведёт к действию
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (21 files) |