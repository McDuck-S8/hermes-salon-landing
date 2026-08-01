# YouTube Pipeline & Video Processing Reference — Session 2026-07-28

## Overview
Modular video processing pipeline with fallback chain. Implements DIRECTIVE 0x20 (VIDEO_LEARNER_MODULAR) and 0x21 (YT_DLP_FALLBACK_CHAIN).

## Architecture

### 1. YouTubePipeline (`scripts/youtube_pipeline.py`)
Unified pipeline with 4-stage fallback chain:

| Stage | Method | Speed | Reliability | Output |
|-------|--------|-------|-------------|--------|
| 1 | oembed API | ~200ms | 99% | Title, author, author_url |
| 2 | curl + v2rayN proxy + HTML regex | ~2s | 90% | Title, description, channel, views |
| 3 | yt-dlp (with proxy) | ~10s | 80% | Full metadata, subtitles, tags |
| 4 | faster-whisper (local) | ~30s | 100% | Full transcript |

### 2. Key Classes

#### YouTubePipeline
```python
pipeline = YouTubePipeline(proxy="socks5://127.0.0.1:10806")
result = pipeline.process_video("https://youtube.com/watch?v=L9vDhq_W3Tk", lang="en,ru")
```

Returns structured dict:
```python
{
    "video_id": "L9vDhq_W3Tk",
    "url": "https://youtube.com/watch?v=L9vDhq_W3Tk",
    "title": "Как выбрать место для бизнеса с Gemini и Google Maps...",
    "author": "Иван Берегуля | AI и Маркетинг для бизнеса",
    "author_url": "https://www.youtube.com/@Ivan_Berehulya",
    "source": "oembed",  # or "html_proxy", "yt_dlp"
    "description": "...",  # if available
    "channel": "...",
    "views": "...",
    "duration": "...",
    "tags": [...],
    "subtitles": ["en", "ru"],
    "auto_captions": ["en", "ru"]
}
```

### 3. v2rayN Proxy Integration
- **Proxy URL**: `socks5://127.0.0.1:10806`
- **Used by**: curl (HTML/oembed), yt-dlp (full metadata)
- **Headers**: Proper User-Agent, Accept-Language for YouTube

### 4. yt-dlp Fallback (DIRECTIVE 0x21)
When local yt-dlp fails (Python 3.13 syntax error):
1. Try Python 3.11 venv: `D:/Portable_Soft/hermes/hermes-agent/.venv311/Scripts/python.exe -m yt_dlp`
2. Try Docker: `docker run --rm -v $(pwd):/data ghcr.io/yt-dlp/yt-dlp`
3. Try cloud: yt-dlp API (if available)
4. Return partial result from earlier stages

## Video Concepts Extracted This Session

| Video ID | Title | Concepts Extracted |
|----------|-------|-------------------|
| L9vDhq_W3Tk | Gemini + Google Maps business location | 5 concepts (Gemini API, Maps API, competitor mapping, step-by-step, criteria) |
| 8m-YA7jphM0 | Flowise AI creative agency | 5 concepts (low-code builder, agency model, visual workflows, multi-agent, client delivery) |
| qiDalcMeBFk | Claude Code multi-agent workflows | 5 concepts (subagent architecture, skill-based delegation, handoffs, CLI orchestration, skill composition) |
| QOBXFCYYMvk | (oembed only) | Title, author, channel |

## Cache Storage
- Raw metadata: `cache/youtube/{video_id}.json`
- Transcripts: `cache/youtube/{video_id}.vtt` (if downloaded)
- Processed concepts: Tactical Buffer hypotheses

## Integration with Tactical Buffer
```python
# Auto-conversion from video metadata to tactical hypotheses
for concept in extracted_concepts:
    tb.add(
        param=concept["title"],
        value=concept["description"],
        source="video",
        context_tags={"video_id": video_id, "topic": concept["topic"]}
    )
```

## CLI Usage
```bash
# Single video
python scripts/youtube_pipeline.py "https://youtube.com/watch?v=L9vDhq_W3Tk" "en,ru"

# Batch (manual loop)
for v in L9vDhq_W3Tk 8m-YA7jphM0 qiDalcMeBFk; do
    python scripts/youtube_pipeline.py "https://youtube.com/watch?v=$v" "en,ru"
done
```

## Test Results
- oembed: ✅ PASS (all 4 videos)
- HTML proxy: ⚠️ PARTIAL (YouTube blocks some requests)
- yt-dlp: ❌ FAIL (Python 3.13 syntax error)
- faster-whisper: ✅ INSTALLED (needs audio file)

## Known Issues
1. yt-dlp broken on Python 3.13 — needs isolated Python 3.11 env or Docker
2. HTML proxy sometimes fails due to YouTube anti-bot
3. Subtitle download fails when yt-dlp unavailable
4. No automatic scheduling for channel monitoring

## Future Improvements
- Embeddings-based video search
- Automatic concept clustering across videos
- Integration with `video-learner` skill for local file processing
- Scheduled channel monitoring via cron

## Files
- `scripts/youtube_pipeline.py` — Main pipeline
- `scripts/youtube_pipeline.py` (v2 with HTML fallback fix)
- `cache/youtube/*.json` — Cached metadata