# lavra-agent-agent-native-reviewer — Skill

## Purpose
Reviews code for agent-native compliance - ensuring user actions have agent equivalents and agents see what users see. Checks action parity, context parity, and shared workspace design.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Reviews code for agent-native compliance - ensuring user actions have agent equivalents and agents see what users see
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