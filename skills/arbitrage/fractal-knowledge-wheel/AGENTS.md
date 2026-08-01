# fractal-knowledge-wheel — Skill

## Purpose
Рекурсивное исследование знаний: Режим 1 — Анализ (ключ → аспекты → пробелы → задачи). Режим 2 — Синтез (разрозненные находки → новые ключи/связки). Режим 3 — Круги Эйлера (пересечения аспектов → золо

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: arbitrage, knowledge-management, synthesis, analysis, okf, euler-circles, balance-wheel
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Рекурсивное исследование знаний: Режим 1 — Анализ (ключ → аспекты → пробелы → задачи)
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (9 files) |
| `scripts/` | Helper scripts (3 files) |