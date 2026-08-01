# youtube_pipeline.py — Unified Fallback Chain (2026-07-30)

**Location:** `scripts/youtube_pipeline.py`

The `youtube_pipeline.py` script implements a **4-stage fallback chain** that maximizes success rate on Windows with v2rayN proxy:

```
Stage 1: oembed API          (~200ms)  → title, author
Stage 2: curl + proxy + HTML (~2s)    → description, channel, views
Stage 3: yt-dlp + rescue     (~10s)   → full metadata + subtitles
Stage 4: faster-whisper      (~30s)   → audio transcription (last resort)
```

## Key Features

| Feature | Implementation |
|---------|----------------|
| Proxy support | `socks5://127.0.0.1:10806` (v2rayN) |
| Player client rotation | `tv, web_embedded, android_vr, tv_downgraded, web_creator, mweb` |
| PO Token support | Via `YT_DLP_POT_PROVIDER_URL` env var |
| IPv4 force | `--force-ipv4` for cloud servers |
| Subtitle download | Auto-captions + manual, VTT conversion |
| Windows-safe encoding | `encoding='utf-8', errors='replace'` on all subprocess calls |

## Usage

```bash
# CLI
python scripts/youtube_pipeline.py "https://youtu.be/VIDEO_ID" "en,ru"

# Python
from scripts.youtube_pipeline import YouTubePipeline
pipeline = YouTubePipeline(proxy="socks5://127.0.0.1:10806")
result = pipeline.process_video("https://youtu.be/VIDEO_ID", "en,ru")
```

## Output

```json
{
  "video_id": "ABC123",
  "title": "Video Title",
  "description": "Full description text...",
  "channel": "Channel Name",
  "views": "12345",
  "duration": 698,
  "tags": ["tag1", "tag2"],
  "subtitles": ["en", "ru"],
  "auto_captions": ["en", "ru", "es"],
  "formats_count": 26,
  "source": "yt_dlp"
}
```

## When to Use This Over Agent Reach / BrowserClaw

| Scenario | Use |
|----------|-----|
| Need fallback chain (not just fastest) | `youtube_pipeline.py` |
| Windows + v2rayN proxy | `youtube_pipeline.py` |
| Pure speed, Linux/macOS, no auth | Agent Reach (yt-dlp) |
| Need to interact (click, auth) | BrowserClaw / browser_navigate |
| Quick metadata only (200ms) | oembed API |

## Integration with KC

```python
from scripts.youtube_pipeline import YouTubePipeline
from scripts.event_evolution import on_task_complete

pipeline = YouTubePipeline()
result = pipeline.process_video(url, "en,ru")

on_task_complete(
    content=f"Extracted YouTube video: {result['title']} ({result['channel']})",
    tags=["youtube", "research", result.get('channel', 'unknown')],
    source="youtube_pipeline"
)
```

---

**Key insight:** Agent Reach replaces browser automation for DATA EXTRACTION. Use `browser_navigate` only when you need to INTERACT (click, fill forms, handle JS-heavy auth flows).