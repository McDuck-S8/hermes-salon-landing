# multi-agent-orchestration — Skill

## Purpose
Multi-agent orchestration pattern for Hermes: Manager + specialized Workers with task queue, workflows, and honest validation.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: multi-agent, orchestration, worker-pattern, fleet-management, task-queue, workflow-engine
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Multi-agent orchestration pattern for Hermes: Manager + specialized Workers with task queue, workflows, and honest validation
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (3 files) |