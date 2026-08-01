# YT-DLP Docker Setup for Video Learner

## Docker Image

```bash
# Build custom yt-dlp image with all dependencies
docker build -t yt-dlp:latest - <<'EOF'
FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir yt-dlp
ENTRYPOINT ["yt-dlp"]
EOF
```

## Quick Start

```bash
# Pull or build
docker build -t yt-dlp:latest .

# Test
docker run --rm yt-dlp:latest --version

# Download audio only (for faster-whisper)
docker run --rm -v $(pwd)/downloads:/downloads \
  -e ALL_PROXY=socks5://127.0.0.1:10806 \
  yt-dlp:latest \
  -f bestaudio --extract-audio --audio-format mp3 \
  -o "/downloads/%(id)s.%(ext)s" \
  "https://www.youtube.com/watch?v=VIDEO_ID"

# Get metadata
docker run --rm -e ALL_PROXY=socks5://127.0.0.1:10806 \
  yt-dlp:latest --dump-json "https://youtu.be/VIDEO_ID"

# Get subtitles
docker run --rm -v $(pwd)/subs:/subs \
  -e ALL_PROXY=socks5://127.0.0.1:10806 \
  yt-dlp:latest \
  --write-auto-subs --sub-langs en,ru --skip-download \
  -o "/subs/%(id)s.%(ext)s" \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Docker Compose (Optional)

```yaml
# docker-compose.yml
version: '3.8'
services:
  yt-dlp:
    image: yt-dlp:latest
    build: .
    environment:
      - ALL_PROXY=socks5://127.0.0.1:10806
    volumes:
      - ./downloads:/downloads
      - ./subs:/subs
    entrypoint: []
    command: sleep infinity  # Keep running for multiple commands
```

## Python Integration

```python
import subprocess
import json
from pathlib import Path

class YtDlpAdapter:
    def __init__(self, proxy: str = "socks5://127.0.0.1:10806"):
        self.proxy = proxy
        self.image = "yt-dlp:latest"
    
    def get_metadata(self, url: str) -> dict:
        cmd = [
            "docker", "run", "--rm",
            "-e", f"ALL_PROXY={self.proxy}",
            "yt-dlp:latest",
            "--dump-json", "--no-download", url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp failed: {result.stderr}")
        return json.loads(result.stdout)
    
    def download_audio(self, url: str, output_dir: Path) -> Path:
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{output_dir}:/downloads",
            "-e", f"ALL_PROXY={self.proxy}",
            "yt-dlp:latest",
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "192K",
            "-o", "/downloads/%(id)s.%(ext)s",
            url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"Download failed: {result.stderr}")
        
        for f in output_dir.glob("*.mp3"):
            return f
        raise FileNotFoundError("No audio file found")

    def get_subtitles(self, url: str, langs: list = ["en", "ru"], output_dir: Path) -> dict:
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{output_dir}:/subs",
            "-e", f"ALL_PROXY={self.proxy}",
            "yt-dlp:latest",
            "--write-auto-subs",
            "--sub-langs", ",".join(langs),
            "--skip-download",
            "-o", "/subs/%(id)s.%(ext)s",
            url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(f"Subtitle extraction failed: {result.stderr}")
        
        # Return paths to subtitle files
        subs = {}
        for f in output_dir.glob("*.vtt"):
            lang = f.stem.split(".")[-1]
            subs[lang] = f.read_text()
        return subs
```

## Fallback Chain (per DIRECTIVE 0x0C)

```python
async def extract_video_content(url: str) -> dict:
    """Try multiple methods in order"""
    
    # 1. Try yt-dlp with proxy (fast, reliable)
    try:
        adapter = YtDlpAdapter()
        return await adapter.extract_full(url)
    except Exception as e:
        logger.warning(f"yt-dlp failed: {e}")
    
    # 2. Fallback: curl + v2rayN proxy + oembed (metadata only)
    try:
        meta = await fetch_oembed(url)
        desc = await fetch_description_curl(url)
        return {"metadata": meta, "description": desc}
    except Exception as e:
        logger.warning(f"curl+oembed failed: {e}")
    
    # 3. Fallback: curl + proxy + HTML regex parsing
    try:
        return await extract_html_regex(url)
    except Exception as e:
        logger.warning(f"HTML parsing failed: {e}")
    
    # 4. Last resort: yt-dlp in isolated Python 3.11 venv or Docker
    try:
        return await extract_via_docker_venv(url)
    except Exception as e:
        logger.error(f"All methods failed: {e}")
        raise
```

## Proxy Configuration (v2rayN)

```bash
# v2rayN SOCKS5 port (default)
ALL_PROXY=socks5://127.0.0.1:10806
HTTPS_PROXY=socks5://127.0.0.1:10806
HTTP_PROXY=socks5://127.0.0.1:10806
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check v2rayN running, port 10806 |
| 403 Forbidden | Rotate proxy, check YouTube IP |
| Subtitle extraction failed | Video has no auto-captions |
| Docker permission denied | `sudo usermod -aG docker $USER` |
| Timeout | Increase timeout, check proxy latency |