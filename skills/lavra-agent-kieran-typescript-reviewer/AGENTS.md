# lavra-agent-kieran-typescript-reviewer — Skill

## Purpose
TypeScript code review enforcing strict conventions: no-any policy, proper type safety, modern TS 5+ patterns, import organization, testability, naming clarity. Use after TypeScript changes.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: TypeScript code review enforcing strict conventions: no-any policy, proper type safety, modern TS 5+ patterns, import organization, testability, naming clarity
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