# video-learner — Skill

## Purpose
Video processing pipeline: yt-dlp → faster-whisper → LLM concept extraction → tactical buffer. Handles YouTube, local files, v2rayN proxy fallback.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, scripts/, references/.

## Local Contracts
- **Triggers**: video processing, youtube transcript, video learning, concept extraction from video
- **Required tools**: yt-dlp, faster-whisper, curl, OpenRouter API
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Video processing pipeline for YouTube, local files, v2rayN proxy fallback.
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `scripts/` | VideoLearner class and pipeline |
| `config.yaml` | Configuration (whisper model, languages, etc.) |
| `references/` | Reference materials (API docs, etc.) |