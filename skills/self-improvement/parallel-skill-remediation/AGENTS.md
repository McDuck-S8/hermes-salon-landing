# parallel-skill-remediation — Skill

## Purpose
Batch-fix SkillSpector findings across multiple skills using parallel delegate_task subagents

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: skill-audit, security, parallel, delegate_task, remediation
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Batch-fix SkillSpector findings across multiple skills using parallel delegate_task subagents
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