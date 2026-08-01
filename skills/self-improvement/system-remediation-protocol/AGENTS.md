# system-remediation-protocol — Skill

## Purpose
Full system health restoration + parallel skill security remediation protocol. Runs Chain Heartbeat recovery, then deploys parallel subagents for SkillSpector findings across all categories.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: system-health, chain-heartbeat, skill-remediation, parallel-execution, security-audit
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Full system health restoration + parallel skill security remediation protocol
**Common patterns**: - chain-heartbeat
- skill-evolution
- skill-indexer
- self-improvement
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (1 files) |