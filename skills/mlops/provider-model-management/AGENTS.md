# provider-model-management — Skill

## Purpose
Central registry for LLM providers and models — model_registry.py pattern. Eliminates hardcoded provider URLs, model names, and API keys across scripts.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: providers, models, registry, architecture, llm, configuration, model-registry
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Central registry for LLM providers and models — model_registry
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (1 files) |