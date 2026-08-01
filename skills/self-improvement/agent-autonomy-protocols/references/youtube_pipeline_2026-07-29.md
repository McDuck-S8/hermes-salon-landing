# YouTube Pipeline — 2026-07-29 Session Notes

## Current Status

### Working Videos (oembed only)
| Video ID | Title | Channel | Source |
|----------|-------|---------|--------|
| o1DsUPdSj1s | 35 Self-hosted Github Projects... | Github Awesome | oembed |
| L9vDhq_W3Tk | Как выбрать место для бизнеса с Gemini... | Иван Берегуля | oembed |
| 8m-YA7jphM0 | Flowise: AI Креативное Агентство 🚀 | Anthony Vdovitchenko | oembed |
| qiDalcMeBFk | How to Use Multi-Agent Workflows in Claude Code | The Code City | oembed |

### Blocked Videos (YouTube 429 / timeout)
| Video ID | Issue | Tried |
|----------|-------|-------|
| XvCvKawtJAk | HTTP 429, timeout | oembed, HTML proxy, yt-dlp + proxy |
| 3Qc49WnQnSg | HTTP 429, timeout | oembed, HTML proxy, yt-dlp + proxy |

---

## Root Cause

**YouTube rate limiting** — even through v2rayN SOCKS5 proxy (127.0.0.1:10806), YouTube returns HTTP 429 (Too Many Requests) and connection timeouts. The proxy IP is likely shared/flagged.

---

## Fallback Chain Status

```
1. oembed API          → 429 for some videos, works for others
2. curl + v2rayN proxy → HTML parsing fails (no data returned)
3. yt-dlp + proxy      → 429 / timeout (30s)
4. subtitles download  → works (separate endpoint, less restricted)
```

**Pipeline doesn't crash** — gracefully degrades to minimal cache (video_id + url).

---

## Solutions to Implement

### 1. Cookie Authentication (Priority)
```python
# Export cookies from browser, use with yt-dlp
yt-dlp --cookies-from-browser chrome --dump-json URL
```
**Why:** Authenticated requests have higher quotas, bypass some bot detection.

### 2. Invidious / Piped Instances (Priority)
```python
# Alternative frontends with no rate limiting
INVIDIOUS_INSTANCES = [
    "https://yewtu.be",
    "https://invidious.snopyta.org", 
    "https://invidious.nerdvpn.de",
    "https://y.com.sb"
]
PIPED_INSTANCES = [
    "https://piped.video",
    "https://piped.kavin.rocks"
]
```
**Why:** No API keys, no rate limits, returns JSON directly.

### 3. Proxy Rotation
```python
PROXY_POOL = [
    "socks5://127.0.0.1:10806",  # v2rayN
    "socks5://127.0.0.1:10807",  # alt v2rayN
    "http://127.0.0.1:8080",     # alt proxy
]
# Rotate on 429/timeout
```

### 4. Rate Limiting & Backoff
```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=5, max=30))
def fetch_with_backoff(url, proxy=None):
    ...
```

### 5. Local Audio + faster-whisper (for transcripts)
- Download audio only (smaller, less restricted)
- Transcribe locally with faster-whisper (no API calls)
- Already implemented in `video_learner.py`

---

## Implementation Plan

1. **Update `youtube_pipeline.py`** — add Invidious/Piped as Step 1.5 (before HTML proxy)
2. **Add cookie support** — `--cookies-from-browser chrome` flag
3. **Add proxy rotation** — cycle through pool on 429
4. **Add rate limiting** — min 5s between requests to same domain
4. **Cache Invidious instance health** — prefer working instances

---

## Design Learner Impact

**Not critical for current phase:**
- 4 videos successfully cached with titles/channels
- Concepts from oembed titles already in tactical buffer
- Design reference collector uses external sources (Awwwards, Behance, GitHub) not YouTube
- Manual curation always an option

**But valuable for scale:**
- YouTube is rich source for UI/UX tutorials, design critiques, component walkthroughs
- Fixing pipeline unlocks continuous learning from design channels

---

## Quick Test Commands

```bash
# Test Invidious
curl "https://yewtu.be/api/v1/videos/XvCvKawtJAk"

# Test Piped
curl "https://piped.video/api/v1/videos/XvCvKawtJAk"

# Test yt-dlp with cookies
yt-dlp --cookies-from-browser chrome --dump-json "https://youtube.com/watch?v=XvCvKawtJAk"
```