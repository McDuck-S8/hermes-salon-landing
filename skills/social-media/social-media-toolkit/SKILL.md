---
name: social-media-toolkit
description: "Unified social media toolkit for Hermes: telegram-channel-poster + telegram-digest + tiktok-account-farm + voice-interface + content-pipeline + youtube-channel-monitor. One skill to load, all social engines at hand."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [social-media, telegram, tiktok, youtube, content, voice, automation, posting]
    related_skills: [telegram-channel-poster, telegram-digest, tiktok-account-farm, voice-interface, content-pipeline, youtube-channel-monitor, content-quality-pipeline, browser-automation, cpa-browser-scraper]
  skill_updated: "2026-07-24"
  created_by: "auto_patch_g007"
  component_skills:
    - telegram-channel-poster
    - telegram-digest
    - tiktok-account-farm
    - voice-interface
    - content-pipeline
    - youtube-channel-monitor
    - content-quality-pipeline
---

# Social Media Toolkit — Unified Interface

**One skill to load. All social media engines. Zero context switching.**

This meta-skill wraps all core social media automation skills into a single loadable unit with a unified workflow interface.

## Quick Start

```python
# Load once, get all 7 engines
from hermes_tools import skill_view
skill_view("social-media/social-media-toolkit")

# Now you have:
# - telegram-channel-poster (beautiful formatted messages with inline buttons)
# - telegram-digest (daily digests from channels → HTML/Markdown)
# - tiktok-account-farm (full stack: creation, warming, posting, analytics)
# - voice-interface (VAD + STT + TTS stack)
# - content-pipeline (arbitrage: research → create → publish)
# - youtube-channel-monitor (yt-dlp cron: new videos, metadata)
# - content-quality-pipeline (class-level quality gate)
```

## Component Skills Map

| Skill | Purpose | Best For |
|-------|---------|----------|
| **telegram-channel-poster** | Post formatted messages with inline buttons to Telegram | Channel posts, notifications, CTAs |
| **telegram-digest** | Collect messages from channels → daily digest | Monitoring, summarization, reporting |
| **tiktok-account-farm** | Full stack: creation, warming, posting, analytics | TikTok automation at scale |
| **voice-interface** | VAD (WebRTC) + STT (faster-whisper) + TTS (edge) | Voice bots, voice notes, accessibility |
| **content-pipeline** | Arbitrage: research → create → publish | CPA/arbitrage content production |
| **youtube-channel-monitor** | yt-dlp cron: new videos, metadata, transcripts | Competitive intel, trend tracking |
| **content-quality-pipeline** | Class-level quality gate for social content | Pre-publish validation |

## Unified Social Media Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. RECON (youtube-channel-monitor + content-pipeline)           │
│    • Monitor competitor channels, trends, new videos            │
│    • Research phase for arbitrage content                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. CREATE (content-pipeline + tiktok-account-farm + voice)      │
│                                                                  │
│    Research → Script (cpa-video-script-generator)               │
│         → Video (cpa-video-pipeline: avatar + voice + edit)     │
│         → Voice notes (voice-interface: TTS)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. QUALITY GATE (content-quality-pipeline)                      │
│    • Pre-publish validation                                      │
│    • Anti-slop check                                             │
│    • Format compliance                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. PUBLISH & MONITOR                                             │
│                                                                  │
│    TikTok → tiktok-account-farm (warm → post → analytics)       │
│    Telegram → telegram-channel-poster (inline buttons, rich)    │
│    Digest → telegram-digest (daily summary to owner)            │
│    YouTube → youtube-channel-monitor (track performance)        │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Commands Reference

### Telegram Channel Poster
```python
# Post with inline buttons
telegram-channel-poster post \
  --chat-id "-100123456789" \
  --text "🚀 New offer!\n\nPayout: $50\nGeo: IN\nVertical: Gaming" \
  --buttons '{"Join": "https://t.me/channel", "Details": "https://offer.com"}' \
  --parse-mode HTML
```

### Telegram Digest
```bash
# Daily digest from channels
telegram-digest collect \
  --channels "@channel1 @channel2" \
  --since 24h \
  --output digest.html

# Send to owner
telegram-digest send --chat-id "123456789" --file digest.html
```

### TikTok Account Farm
```bash
# Create accounts
tiktok-account-farm create --count 10 --proxy-file proxies.txt

# Warm accounts (simulate human behavior)
tiktok-account-farm warm --accounts-file accounts.json --days 7

# Post content
tiktok-account-farm post --account @username --video video.mp4 --caption "Hook here!"

# Analytics
tiktok-account-farm analytics --account @username --days 30
```

### Voice Interface
```python
# VAD + STT + TTS pipeline
from skills.automation.voice_interface import VoiceInterface

vi = VoiceInterface()
# Record → VAD → STT
text = vi.listen_and_transcribe()
# TTS → play/save
vi.speak(text, voice="en-US-AriaNeural", save_path="reply.mp3")
```

### Content Pipeline (Arbitrage)
```python
from skills.automation.content_pipeline import ContentPipeline

pipeline = ContentPipeline()
# Research
offers = pipeline.research_offers(geo="IN", vertical="gaming")
# Create
scripts = pipeline.generate_scripts(offers, format="shorts")
videos = pipeline.produce_videos(scripts, avatar="ai", voice="en-US-AriaNeural")
# Publish
results = pipeline.publish(videos, platforms=["tiktok", "reels", "shorts"])
```

### YouTube Channel Monitor
```bash
# Setup monitoring
youtube-channel-monitor add --channel "UCxxxxxxxx" --name "Competitor X"

# Run check (cron: daily)
youtube-channel-monitor check --since 24h

# Get transcripts
youtube-channel-monitor transcripts --channel "UCxxxxxxxx" --since 7d
```

### Content Quality Pipeline
```python
from skills.automation.content_quality_pipeline import ContentQualityPipeline

qp = ContentQualityPipeline()
result = qp.validate(content, platform="tiktok", format="shorts")
# result: {"passed": true, "score": 0.92, "issues": [], "suggestions": [...]}
```

## Integration with Knowledge Cube

```python
from scripts.event_evolution import on_task_complete

on_task_complete(
    content="Social media cycle complete: youtube-monitor (5 new vids) → content-pipeline (3 scripts) → tiktok-farm (posted 3) → telegram-poster (announced). Digests sent.",
    tags=["social-media", "tiktok", "telegram", "youtube", "content-pipeline", "success"],
    source="agent"
)
```

## Anti-Patterns (from 52 social-media entries, 2 failures = 4% failure rate)

| Anti-Pattern | Guard |
|--------------|-------|
| Kill TikTok campaign on day 3 | **tiktok-farm**: 5-day learning rule, auto-pause only if Spend > $100 & 0 conversions |
| Auto-pause on ROI < 0% | **content-pipeline**: 6-hour learning window, algorithm needs time |
| No localization for UK/DE | **cpa-video-pipeline**: mandatory geo-localization (slang, currency, humor) |
| Cash flow ignored | **finance-core**: track cash flow daily, not just ROI |
| Single creative per ad set | **tiktok-farm**: Dynamic Creative with 10 variants, AI picks winner |

## Verification Checklist

After using this toolkit:
- [ ] Correct engine chosen per decision matrix
- [ ] YouTube monitor checked for new videos
- [ ] Content pipeline produced scripts/videos
- [ ] Quality pipeline passed (content-quality-pipeline)
- [ ] TikTok farm posted content + analytics captured
- [ ] Telegram channel posted with inline buttons
- [ ] Digest generated and sent
- [ ] Voice interface tested (VAD+STT+TTS)
- [ ] KC entry created with tags

---

**Origin:** g-007 Unlock: social-media (52 entries, 37 successes, 2 failures)
**Created:** 2026-07-24 via auto_patch_g007
**Source:** Knowledge Cube domain `social-media` + all 7 component skills