# token-compression — Skill

## Purpose
Compress LLM tool outputs (JSON, code, logs) to save 50-88% tokens. Zero-dependency Python. Use when tool outputs are large, token costs matter, or context window is tight.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: cost-optimization, tokens, compression, llm, zero-dependency
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Compress LLM tool outputs (JSON, code, logs) to save 50-88% tokens
**Common patterns**: - action-over-documentation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (1 files) |