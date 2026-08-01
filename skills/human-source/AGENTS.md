# human-source — Skill

## Purpose
Human Source — Человек как Начало. Изучает человека (цифровой отпечаток, фрустрации, грехи, нормы), строит карту ценностей (ландшафт), генерирует ключи из этой карты, бросает их в воду (ripple-engine)

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: human-analysis, values-mapping, ripple-engine, key-generation, psychological-profiling
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Human Source — Человек как Начало
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
| `scripts/` | Helper scripts (3 files) |