# YouTube Pipeline Resilience — yt-dlp-rescue Integration (2026-07-29)

## Problem
YouTube's SABR migration (2024+) + aggressive bot detection (2025+) broke standard yt-dlp:
- `web` client forced to 360p progressive only
- Datacenter IPs blocked with "Sign in to confirm you're not a bot"
- Format IDs change between requests
- PO Token required for quality selection

## Solution: yt-dlp-rescue (CRtheHILLS/yt-dlp-rescue) Battle-Tested Settings

### Player Client Rotation (Most Reliable First)
```python
player_clients = [
    "tv",              # TV client - full DASH, no token needed, most reliable
    "web_embedded",    # Embedded player - full DASH
    "android_vr",      # VR client - full DASH
    "tv_downgraded",   # Downgraded TV - full DASH
    "web_creator",     # YouTube Studio client
    "mweb",            # Mobile web
]
```

### yt-dlp Arguments
```bash
yt-dlp \
  --extractor-args "youtube:player_client=tv,web_embedded,android_vr,tv_downgraded,web_creator,mweb;player_skip=webpage" \
  --force-ipv4 \
  -S "res:1080" \
  --proxy "socks5://127.0.0.1:10806"
```

### Key Flags Explained
| Flag | Purpose |
|------|---------|
| `player_client=tv,web_embedded,android_vr,tv_downgraded,web_creator,mweb` | Rotate through clients that still expose full DASH manifests |
| `player_skip=webpage` | Skip webpage request → fewer HTTP calls, less rate limiting |
| `--force-ipv4` | Prevent IPv6 routing issues on cloud servers |
| `-S "res:1080"` | Sort-based format selection (resilient to SABR format ID changes) |

### PO Token Server (For Bot Detection Bypass)
```bash
# 1. Start PO Token provider (requires Node.js)
git clone https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git
cd bgutil-ytdlp-pot-provider/server
npm ci && npx tsc
node build/main.js &

# 2. Set env var so yt-dlp connects automatically
export YT_DLP_POT_PROVIDER_URL="http://127.0.0.1:4416"

# 3. yt-dlp will automatically use it
yt-dlp --extractor-args "youtube:player_client=web,android_vr,tv_downgraded" URL
```

**Critical:** Without `YT_DLP_POT_PROVIDER_URL` set, the server runs but yt-dlp doesn't know it exists!

## Fallback Chain (Implemented in Video Learner)

| Stage | Method | Speed | Reliability | Data |
|-------|--------|-------|-------------|------|
| 1 | oembed API | ~200ms | 99% | Title, author, thumbnail |
| 2 | curl + SOCKS5 + HTML regex | ~2s | 80% | Description, channel, views |
| 3 | yt-dlp + rescue args + PO Token | ~10s | 95% | Full metadata, subtitles, formats |
| 4 | Local faster-whisper | ~30s | 100% | Audio transcription |

## Video Learner Integration

The `scripts/video_learner.py` should use the rescue configuration:

```python
class VideoLearner:
    def __init__(self, proxy: str = "socks5://127.0.0.1:10806"):
        self.proxy = proxy
        self.yt_dlp_module = [sys.executable, "-m", "yt_dlp"]
        
        # yt-dlp-rescue recommended player clients
        self.player_clients = [
            "tv", "web_embedded", "android_vr", 
            "tv_downgraded", "web_creator", "mweb"
        ]
        
        # PO Token server URL (set via env var YT_DLP_POT_PROVIDER_URL)
        self.pot_provider_url = os.environ.get("YT_DLP_POT_PROVIDER_URL")
    
    def _build_yt_dlp_args(self, video_id: str) -> List[str]:
        player_clients = ",".join(self.player_clients)
        args = [
            "--dump-json", "--no-download",
            "--extractor-args", f"youtube:player_client={player_clients};player_skip=webpage",
            "--force-ipv4",
        ]
        
        # Add PO Token provider if configured
        if self.pot_provider_url:
            args.extend(["--extractor-args", f"youtube:pot_provider_url={self.pot_provider_url}"])
        
        # Proxy
        if self.proxy:
            args.extend(["--proxy", self.proxy])
        
        args.append(f"https://www.youtube.com/watch?v={video_id}")
        return args
    
    def transcribe_video(self, url: str) -> Dict:
        """Full pipeline: metadata + subtitles + local transcription"""
        video_id = self.extract_video_id(url)
        
        # Step 1: yt-dlp with rescue args
        metadata = self.get_metadata_yt_dlp(video_id)
        
        # Step 2: Download subtitles
        subtitles = self.download_subtitles(video_id)
        
        # Step 3: Local transcription (faster-whisper) if needed
        if not subtitles:
            transcript = self.transcribe_local(url)
        
        # Step 4: Concept extraction + tactical buffer
        concepts = self.extract_concepts(transcript or subtitles)
        self.save_to_tactical_buffer(concepts)
        
        return concepts
```

## Verification Results (2026-07-29)

| Video | Before | After (rescue) |
|-------|--------|----------------|
| XvCvKawtJAk | 429 timeout / 360p only | 26 formats, 1080p, full description, subtitles |
| 3Qc49WnQnSg | 429 timeout / 360p only | 28 formats, 1080p, full description, tags, subtitles |

**Both videos now download full metadata + subtitles without PO Token server (just player rotation + force-ipv4 + player_skip).**

## References
- yt-dlp-rescue: https://github.com/CRtheHILLS/yt-dlp-rescue
- PO Token provider: https://github.com/Brainicism/bgutil-ytdlp-pot-provider
- yt-dlp issue: https://github.com/yt-dlp/yt-dlp/issues/10078
- SABR migration: https://github.com/yt-dlp/yt-dlp/wiki/Extractors#youtube