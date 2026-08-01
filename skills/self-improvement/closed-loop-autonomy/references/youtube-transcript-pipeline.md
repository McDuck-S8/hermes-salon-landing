# YouTube Transcript Pipeline (2026-07-27)

## Problem
YouTube videos in the faceless/automation/CPA niche mostly disable auto-captions.
`yt-dlp --write-auto-subs` returns nothing. `youtube-transcript-api` without proxy
is blocked by sanctions routing (Crimea).

## Solution
`youtube-transcript-api` through v2rayN SOCKS5/HTTP proxy.

## Pipeline

```bash
# Set proxy
export http_proxy=http://127.0.0.1:10806
export https_proxy=http://127.0.0.1:10806
export HTTP_PROXY=http://127.0.0.1:10806
export HTTPS_PROXY=http://127.0.0.1:10806

# Search for videos
yt-dlp --proxy http://127.0.0.1:10806 --flat-playlist --dump-json \
  "ytsearch10:faceless YouTube channel automation AI 2026"

# Check for transcripts (Python)
python3 << 'EOF'
from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
t = api.fetch("VIDEO_ID")          # FetchedTranscript object
segs = list(t)                      # list of FetchedTranscriptSnippet
print(f"Language: {t.language_code}, Generated: {t.is_generated}, Segments: {len(segs)}")
for s in segs[:3]:
    print(f"  {s.text[:60]}  @{s.start:.1f}s")
EOF
```

## Results (2026-07-27)
- Batch 1 (54 videos, broad niche): 16/54 with transcripts (~30%)
- Batch 2 (90 videos, faceless niche): 0/90 with transcripts (~0%)
- Total: 16 transcripts saved as JSON in `cache/youtube_learning/*.json`

## Rate Limits
- `api.fetch()` takes 1-3s per video through proxy
- Batch of 5 at a time: ~15s
- No explicit rate limiting observed (2026-07-27)

## Known Issues
- Videos without ANY language captions → raises exception (catch and skip)
- Videos deleted/unavailable → raises "The video is no longer available"
- Language: always request English first, fallback to auto
- YouTube API through proxy is ~2x slower than direct

## Workaround for 0% cases
When `youtube-transcript-api` returns 0 results (faceless niche):
1. Download audio: `yt-dlp --proxy <proxy> -x --audio-format mp3 -o <path> <url>`
2. Install faster-whisper: `pip install faster-whisper`
3. Transcribe: `faster_whisper.WhisperModel("base") → model.transcribe(audio_path)`
4. Note: ~20MB/10min video, ~30s transcription time on CPU

See: `cache/youtube_learning/FACELESS_YOUTUBE_SOP.md` for the extracted knowledge.
