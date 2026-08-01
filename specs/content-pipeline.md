# Spec: Content Pipeline Skill

## Requirements
- End-to-end content factory: Scripts → Videos → Publish → Track → Optimize
- 35 videos/week: 10 TikTok, 10 Shorts, 5 Reels, 10 reserve
- A/B test hooks, thumbnails, CTAs
- Kill losers Day 2, scale winners

## Acceptance Criteria
- [ ] generate_scripts.py outputs 35 valid scripts with hook/proof/CTA structure
- [ ] Scripts include UTM parameters for tracking
- [ ] Video creation template compatible with CapCut Pro
- [ ] Publishing workflow supports multi-account (Dolphin Anty)
- [ ] Analytics: views, CTR, completion rate, conversion to lock

## Technical Details
- Topics: Gaming coupons (V-Bucks, Robux, GTA$), Streaming (Netflix, Spotify)
- Hooks: 8 templates, rotated and A/B tested
- Voices: 3 male, 2 female (ElevenLabs)
- Platforms: TikTok (priority), YouTube Shorts, Instagram Reels

## Dependencies
- agent-browser (web research for trending topics)
- forge-dynamic-tools (video editing automation)
- finance-core (ROI tracking per content piece)