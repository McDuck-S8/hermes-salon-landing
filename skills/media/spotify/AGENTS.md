# spotify — Skill Contract

## Purpose
No description provided

## Ownership
Hermes Agent — self-maintained via skill-forge. Category: general.

## Local Contracts
### Triggers
- When to use this
- use/skip without preflight. Only inspect state when

### Required Tools
- Standard Hermes toolset (read_file, write_file, search_files, terminal, web_search, skill_view, skill_manage)

### Configuration
- Standard skill configuration via SKILL.md frontmatter

## Work Guidance
### When to Use
- this skill

### Common Patterns
- `spotify_playlists list` to find the playlist ID by name
- Get the track URI (from currently playing, or search)
- `spotify_playlists add_items` with the playlist_id and URIs
- `spotify_playback` — play, pause, next, previous, seek, set_repeat, set_shuffle, set_volume, get_state, get_currently_pl
- `spotify_devices` — list, transfer
- `spotify_queue` — get, add

### Integration Points
- the
- this
- full
- r-guide
- r

## Verification
- Load skill and verify it responds to trigger conditions
- Run skill's example/test commands from SKILL.md
- Check skill output matches expected format

## Child DOX Index
- No child directories found (references/, templates/, scripts/)

---
*Generated: 2026-07-28 17:31*
*Source: SKILL.md frontmatter + content analysis*
