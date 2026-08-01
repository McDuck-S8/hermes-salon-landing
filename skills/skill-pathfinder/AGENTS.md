# skill-pathfinder — Skill

## Purpose
Поисковик Пути — самоориентация в пространстве навыков. Строит граф зависимостей навыков, оценивает уровень освоения, находит точку входа (самый слабый × самый востребованный), выстраивает маршрут обу

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: skill-mapping, learning-path, dependency-graph, best-practices, self-assessment
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Поисковик Пути — самоориентация в пространстве навыков
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `scripts/` | Helper scripts (1 files) |