# lavra-agent-kieran-python-reviewer — Skill

## Purpose
Python code review enforcing strict conventions: mandatory type hints (modern 3.10+ syntax), Pythonic patterns, proper module organization, testability, naming clarity. Use after Python changes.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Python code review enforcing strict conventions: mandatory type hints (modern 3
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