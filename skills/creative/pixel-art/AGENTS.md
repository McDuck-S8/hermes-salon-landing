# pixel-art — Skill Contract

## Purpose
No description provided

## Ownership
Hermes Agent — self-maintained via skill-forge. Category: general.

## Local Contracts
### Triggers
- When the task matches the skill's domain and purpose

### Required Tools
- ffmpeg
- python
- bash
- pip
- terminal

### Configuration
- Standard skill configuration via SKILL.md frontmatter

## Work Guidance
### When to Use
- - User wants retro pixel art from a source image
- |
- - User wants retro pixel art from a source image

### Common Patterns
- ```
clarify(
...```
- ```
clarify(
...```
- ```
pixel_art("in.png", "out.png", preset="snes", palette="PICO_8", block=6)
...```
- Boost contrast/color/sharpness (stronger for smaller palettes)
- Posterize to simplify tonal regions before quantization
- Downscale by `block` with `Image.NEAREST` (hard pixels, no interpolation)

### Integration Points
- -
- the
- adaptive
- User
- directory

## Verification
- - PNG is created at the output path

## Child DOX Index
- **references/** — 1 files: palettes.md
- **scripts/** — 4 files: palettes.py, pixel_art.py, pixel_art_video.py, __init__.py

---
*Generated: 2026-07-28 17:31*
*Source: SKILL.md frontmatter + content analysis*
