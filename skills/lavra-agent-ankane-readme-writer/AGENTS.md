# lavra-agent-ankane-readme-writer — Skill

## Purpose
Creates or updates README files following Ankane-style template for Ruby gems. Enforces imperative voice, sentences under 15 words, proper section ordering, and single-purpose code fences.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Creates or updates README files following Ankane-style template for Ruby gems
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