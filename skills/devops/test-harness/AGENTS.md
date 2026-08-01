# test-harness — Skill

## Purpose
Test Harness pattern from AI-First Business Playbook — SPEC → TESTS → GENERATE → VALIDATE → LOOP → DELIVER. Every fix/feature passes through this cycle.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Test Harness pattern from AI-First Business Playbook — SPEC → TESTS → GENERATE → VALIDATE → LOOP → DELIVER
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (8 files) |
| `templates/` | Templates (1 files) |
| `scripts/` | Helper scripts (1 files) |