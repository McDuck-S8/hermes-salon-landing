# heartmula — Skill Contract

## Purpose
No description provided

## Ownership
Hermes Agent — self-maintained via skill-forge. Category: general.

## Local Contracts
### Triggers
- When the task matches the skill's domain and purpose

### Required Tools
- uv
- bash
- pip
- git
- python

### Configuration
- Standard skill configuration via SKILL.md frontmatter

## Work Guidance
### When to Use
- - User wants to generate music/songs from text descriptions
- - User wants to generate music/songs from text descriptions
- ### Basic Generation

### Common Patterns
- ```
cd ~/  # or desired directory
...```
- ```
uv venv --python 3.10 .venv
...```
- ```
# Upgrade datasets (old version incompatible with current pyarrow)
...```
- **Do NOT use bf16 for HeartCodec** — degrades audio quality. Use fp32 (default).
- **Tags may be ignored** — known issue (#90). Lyrics tend to dominate; experiment with tag ordering.
- **Triton not available on macOS** — Linux/CUDA only for GPU acceleration.

### Integration Points
- models
- User
- true
- ed
- bracketed

## Verification
- GPU is being used, look for "CUDA memory" lines in the output (e.g. "CUDA memory before unloading: 6.20 GB")

## Child DOX Index
- No child directories found (references/, templates/, scripts/)

---
*Generated: 2026-07-28 17:31*
*Source: SKILL.md frontmatter + content analysis*
