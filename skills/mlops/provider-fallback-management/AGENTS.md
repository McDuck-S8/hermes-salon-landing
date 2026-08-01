# provider-fallback-management — Skill

## Purpose
Automatic and manual provider fallback for Hermes when the primary LLM provider hits rate limits, timeouts, or API errors. Includes switch_provider.py for manual switching, provider_guard.py for auto-

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: provider, fallback, switch, rate-limit, auto-recovery, hermes-config
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Automatic and manual provider fallback for Hermes when the primary LLM provider hits rate limits, timeouts, or API errors
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