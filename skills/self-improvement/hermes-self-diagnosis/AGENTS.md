# hermes-self-diagnosis — Skill

## Purpose
Complete self-diagnosis — health check, Knowledge Cube recovery, skill evolution, system monitoring

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: health, diagnosis, self-improvement, monitoring, knowledge-cube
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Complete self-diagnosis — health check, Knowledge Cube recovery, skill evolution, system monitoring
**Common patterns**: - skill-indexer
- latent-domain-detector
- skill-evolution
- dream-memory
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (22 files) |