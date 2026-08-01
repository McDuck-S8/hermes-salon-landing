# uiux-review-crew — Skill

## Purpose
Multi-agent UI/UX review crew for landing pages. Uses Browser Harness (CDP) for screenshots + HTML/CSS extraction, then OpenRouter LLMs (Cerebras/DeepSeek/Groq/Claude) for 3-agent analysis pipeline (C

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: uiux, landing-page, design-review, multi-agent, browser-automation, quality-gate, browser-harness, openrouter
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Multi-agent UI/UX review crew for landing pages
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
| `scripts/` | Helper scripts (5 files) |