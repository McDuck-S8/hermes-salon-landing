# Video Generation Pipeline — Content-Locking-CPA (TikTok/Shorts/Reels)

## Purpose
Generate 5+ vertical videos (9:16) per day for content locking CPA campaigns. Themes: gaming cheats, software cracks, coupons, premium account generators.

## Pipeline Architecture

```
Input: Topic list (["Free V-Bucks", "Free Robux", "Free GTA Money", "Netflix Generator", "Spotify Premium"])
         ↓
1. SCRIPT GENERATION (DeepSeek/Groq)
   - Hook (0-3s): "Want free V-Bucks without human verification?"
   - Demo (3-10s): Screen recording / animation of "generator"
   - CTA (10-15s): "Link in bio → Complete offer → Get codes"
         ↓
2. STOCK FOOTAGE (Pexels/Pixabay API)
   - Search: "gaming", "mobile gaming", "excited person", "phone screen"
   - Filter: vertical (9:16), free, no attribution required
   - Download: 5-10 clips per video
         ↓
3. VOICEOVER (ElevenLabs TTS)
   - Voice: Energetic male/female, English (Tier-1) or Russian (RU)
   - Model: eleven_multilingual_v2
   - Output: MP3 per script line
         ↓
4. COMPOSITION (FFmpeg)
   - Concatenate stock clips to match voiceover duration
   - Overlay: Dynamic text (hook, steps, CTA)
   - Add: Watermark (brand), progress bar, sound effects
   - Output: MP4, H.264, 1080x1920, 30fps, <15s
         ↓
5. METADATA GENERATION
   - Title: "How to Get FREE V-Bucks in 2024 (Actually Works)"
   - Description: Template with UTM tracking link
   - Hashtags: #vbucks #fortnite #freegaming #gaminghacks
   - Thumbnail: Auto-generated from first frame + text overlay
         ↓
6. DISTRIBUTION
   - Upload queue: TikTok API / YouTube Shorts API / Instagram Graph API
   - Schedule: Staggered throughout day
   - Tracking: UTM parameters per platform/account
```

## A/B Test Variant Support (Added 2026-07-07)

**Per research/ab_test_content_locking_plan.md**, the pipeline must generate content for **3 landing page variants**:

| Variant | Locker Mechanism | UTM Content | Video CTA Alignment |
|---------|------------------|-------------|---------------------|
| A (Control) | Neutral: "Unlock Content" | `control_neutral` | Generic CTA |
| B (FOMO) | Timer + Scarcity: "15 min left", "Only 3 spots" | `fomo_timer` | Urgency in hook |
| C (Social Proof) | Live counter + avatars + reviews | `social_live` | Social validation in hook |

**Pipeline modification needed:**
- `generate_content_locking_videos.py` → accepts `variant` parameter (A/B/C)
- Script generator → variant-specific hooks (urgency vs social proof vs neutral)
- Metadata generator → variant-specific UTM tags
- CPAGrip locker creation → 3 separate lockers with different designs

## Script Template (per topic, per variant)

```json
{
  "topic": "Free V-Bucks",
  "variant": "B",
  "hook_variants": {
    "A": ["Want free V-Bucks without human verification?", "Stop buying V-Bucks! Get 13,500 FREE", "Fortnite players HATE this free V-Bucks trick"],
    "B": ["ONLY 3 SPOTS LEFT for free V-Bucks!", "TIMER: 15:00 — Free V-Bucks expires soon!", "HURRY: Free V-Bucks offer ends in 15 minutes!"],
    "C": ["1,247 players got FREE V-Bucks today!", "Join 1,247+ who unlocked V-Bucks!", "See why 1,247 gamers trust this V-Bucks method"]
  },
  "demo_script": "Go to the link in bio, enter your username, complete one quick offer, and the V-Bucks appear in your account instantly.",
  "cta": "Link in bio → Tap 'Get Free V-Bucks' → Complete offer → Enjoy!",
  "duration_sec": 15,
  "platform_cta": {
    "tiktok": "Link in bio 👆",
    "youtube_shorts": "Link in description 👇",
    "instagram_reels": "Link in bio 🔗"
  }
}
```

## FFmpeg Composition Command Template

```bash
# Concatenate clips to match audio duration
ffmpeg -f concat -safe 0 -i clips.txt -i voiceover.mp3 \
  -filter_complex "
    [0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v];
    [v]drawtext=text='WANT FREE V-BUCKS?':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=100:enable='between(t,0,3)'[v1];
    [v1]drawtext=text='LINK IN BIO → GET CODES':fontsize=50:fontcolor=yellow:x=(w-text_w)/2:y=1600:enable='between(t,10,15)'[v2];
    [v2]drawbox=x=0:y=0:w=1080:h=1920:color=black@0.3:t=fill[v3]
  " \
  -map "[v3]" -map 1:a -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k \
  -shortest -movflags +faststart output.mp4
```

## API Requirements

| Service | API Key Needed | Free Tier | Rate Limit |
|---|---|---|---|
| DeepSeek | ✅ | Yes | 60/min |
| Groq | ✅ | Yes | 30/min |
| ElevenLabs | ✅ | 10k chars/mo | — |
| Pexels | ✅ | 200/hour | 200/hr |
| Pixabay | ✅ | 5000/day | 5000/day |
| TikTok API | ⚠️ Business account | — | — |
| YouTube API | ✅ | 10k units/day | 10k/day |
| Instagram Graph | ✅ Business account | — | 200/hr |

## Anti-Ban Measures (Critical for Content Locking)

1. **Account separation**: 5 accounts per platform, different proxies, different browser fingerprints
2. **Content variation**: Different hooks, clips, voiceovers per account
3. **Posting schedule**: Stagger 2-4 hours between same-topic posts
4. **No direct links in video**: CTA → bio/linktree only
5. **Watermark rotation**: Subtle brand mark, change position per video
6. **Engagement warmup**: Like/comment on niche content before posting own

## UTM Tracking Template

```
https://carrd.co/locker?utm_source={platform}&utm_medium=organic&utm_campaign=content_locking&utm_content={topic}&utm_term={account_id}
```

Example:
```
https://carrd.co/locker?utm_source=tiktok&utm_medium=organic&utm_campaign=content_locking&utm_content=free_vbucks&utm_term=acc_003
```

**For A/B test**: `utm_content` must include variant: `free_vbucks_fomo`, `free_vbucks_social`, `free_vbucks_control`

## Kill Switches

```env
HERMES_VIDEO_GEN_ENABLED=true
HERMES_VIDEO_GEN_DAILY_LIMIT=50
HERMES_VIDEO_GEN_COST_LIMIT_USD=5.00
```

## Integration Points

- **content-pipeline CREATE stage** → calls this pipeline
- **arbitrage-execution** → uses output for Content-Locking-CPA test
- **auto_poster.py** → needs TikTok/Shorts/Reels adapters for upload
- **ARBITRAGE_LOG.md** → tracks video count, views, clicks, revenue

## File Structure

```
scripts/
├── generate_content_locking_videos.py    # Main orchestrator (variant-aware)
├── video_script_generator.py             # DeepSeek → scripts (variant hooks)
├── stock_fetcher.py                      # Pexels/Pixabay → clips
├── voiceover_generator.py                # ElevenLabs → audio
├── ffmpeg_composer.py                    # Clips + audio + text → MP4
├── metadata_generator.py                 # Titles, descriptions, tags (variant UTM)
└── upload_adapters/
    ├── tiktok_uploader.py
    ├── youtube_shorts_uploader.py
    └── instagram_reels_uploader.py
```

## Reference

See `../arbitrage-execution/references/content-locking-cpa-test-2026-07-06.md` for full test context, blocker map, and math targets.
See `../arbitrage-execution/references/ab-test-content-locking-fomo-social-proof-2026-07-07.md` for A/B test research, statistical design, and success criteria.