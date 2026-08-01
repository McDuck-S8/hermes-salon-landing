# crystal-capability-layer-integration — Skill

## Purpose
Integrate external capability layers (Agent Reach, Oh My Hermes) into Crystal autonomous loop for internet access, multi-agent orchestration, and verified execution

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: crystal, agent-reach, oh-my-hermes, capability-layer, autonomous-loop, web-access, multi-agent
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Integrate external capability layers (Agent Reach, Oh My Hermes) into Crystal autonomous loop for internet access, multi-agent orchestration, and verified execution
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (2 files) |