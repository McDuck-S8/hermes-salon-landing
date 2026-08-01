# cpa-video-pipeline — Skill

## Purpose
Use when orchestrating full video generation pipeline for CPA — script generation → stock footage (Pexels/Pixabay) → voiceover (ElevenLabs) → FFmpeg composition → metadata/UTM → upload adapters

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Use when orchestrating full video generation pipeline for CPA — script generation → stock footage (Pexels/Pixabay) → voiceover (ElevenLabs) → FFmpeg composition → metadata/UTM → upload adapters
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (5 files) |