# Resourcefulness Correction — 2026-07-24

## User's frustration
> "я тебе каналов и ботов накидал... а ты всё токенами не нажрёшься!!!!"

Translation: "I gave you channels and bots... and you still can't get enough tokens!!!"

## What happened
Agent had access to:
- 4 Telegram channels with content
- @max_brain_chef_bot for posting
- `telegram_poster.py` script
- Pollinations.ai for free image generation
- `content-pipeline` for research/create/publish
- 331 skills

Instead of using these, agent reported:
- "Telegram API doesn't work (timeout from Crimea)"
- "xAI video has no credits"
- "BrowserOS is down"

## Lesson
The user already provided infrastructure. Lead with what CAN be done, not with what's missing.

## Correct approach
1. "I have 4 Telegram channels, Pollinations for free images, HTML post templates, content-pipeline."
2. "Telegram API is unreachable from Crimea — here's an alternative: 5 ready posts for manual copy-paste."
3. Deliver concrete work (post files, architecture model, content plan) — not a list of blockers.

## Applied to SKILL.md
Added "RESOURCEFULNESS RULE" section: never lead with blockers, always pair with working alternative.
