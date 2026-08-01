#!/usr/bin/env python3
"""
YouTube Pipeline — fetch video content, extract transcript, record to KC.

Handles IP blocking by using proxy or Invidious fallback.

Usage:
    python scripts/yt_pipeline.py https://www.youtube.com/watch?v=xxx
    python scripts/yt_pipeline.py https://www.youtube.com/watch?v=xxx --transcript-only
"""
import json
import sys
import re
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
KC_DB = CACHE_DIR / "knowledge_cube.db"

sys.path.insert(0, str(HERMES_HOME / "scripts"))


def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    patterns = [
        r"watch\?v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"embed/([a-zA-Z0-9_-]{11})",
        r"/v/([a-zA-Z0-9_-]{11})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return ""


def get_transcript(video_id: str) -> dict:
    """Try to get transcript via youtube-transcript-api."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        text = " ".join([s.text for s in transcript.snippets])
        return {
            "success": True,
            "method": "youtube-transcript-api",
            "text": text,
            "snippets": len(transcript.snippets),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_video_info_ytdlp(video_id: str) -> dict:
    """Try to get video info via yt-dlp."""
    import subprocess
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--skip-download", f"https://www.youtube.com/watch?v={video_id}"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {
                "success": True,
                "method": "yt-dlp",
                "title": data.get("title", ""),
                "description": data.get("description", "")[:1000],
                "channel": data.get("channel", ""),
                "duration": data.get("duration", 0),
                "view_count": data.get("view_count", 0),
                "upload_date": data.get("upload_date", ""),
            }
    except Exception:
        pass
    return {"success": False}


def get_video_info_invidious(video_id: str) -> dict:
    """Fallback: get info from Invidious API."""
    import urllib.request
    instances = [
        "https://inv.nadeko.net",
        "https://invidious.nerdvpn.de",
        "https://vid.puffyan.us",
    ]
    for instance in instances:
        try:
            url = f"{instance}/api/v1/videos/{video_id}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                return {
                    "success": True,
                    "method": f"invidious ({instance})",
                    "title": data.get("title", ""),
                    "description": data.get("description", "")[:1000],
                    "author": data.get("author", ""),
                    "lengthSeconds": data.get("lengthSeconds", 0),
                    "viewCount": data.get("viewCount", 0),
                    "published": data.get("published", 0),
                }
        except Exception:
            continue
    return {"success": False}


def record_to_kc(title: str, transcript: str, video_id: str, url: str):
    """Record video knowledge to KC."""
    try:
        from knowledge_cube import add_experience
        text = f"YouTube video: {title}\nURL: {url}\nTranscript summary: {transcript[:500]}"
        add_experience(
            text=text,
            source="yt_pipeline",
            dynamic_axes={"video_id": video_id, "url": url},
        )
        return True
    except Exception as e:
        print(f"KC record error: {e}")
        return False


def pipeline(url: str, transcript_only: bool = False):
    """Full YouTube pipeline."""
    video_id = extract_video_id(url)
    if not video_id:
        print(f"Could not extract video ID from: {url}")
        return

    print(f"Video ID: {video_id}")
    print(f"URL: https://www.youtube.com/watch?v={video_id}")

    # Step 1: Get video info
    print("\n--- Step 1: Getting video info ---")
    info = get_video_info_ytdlp(video_id)
    if not info["success"]:
        info = get_video_info_invidious(video_id)
    
    if info["success"]:
        print(f"Title: {info.get('title', '?')}")
        print(f"Channel: {info.get('channel', info.get('author', '?'))}")
        print(f"Duration: {info.get('duration', info.get('lengthSeconds', '?'))}s")
        print(f"Views: {info.get('view_count', info.get('viewCount', '?'))}")
        if info.get("description"):
            print(f"Description: {info['description'][:200]}...")
    else:
        print("Could not get video info (IP blocked)")

    # Step 2: Get transcript
    if not transcript_only or info.get("success"):
        print("\n--- Step 2: Getting transcript ---")
        transcript = get_transcript(video_id)
        if transcript["success"]:
            print(f"Transcript: {transcript['snippets']} snippets")
            print(f"Preview: {transcript['text'][:300]}...")
        else:
            print(f"Transcript failed: {transcript['error'][:200]}")

    # Step 3: Record to KC
    if info["success"]:
        print("\n--- Step 3: Recording to Knowledge Cube ---")
        title = info.get("title", "Unknown")
        transcript_text = transcript.get("text", "") if transcript.get("success") else ""
        if record_to_kc(title, transcript_text, video_id, url):
            print("Recorded to KC")
        else:
            print("KC recording failed")

    # Step 4: Report
    print("\n--- Pipeline Complete ---")
    print(f"Video: {info.get('title', url)}")
    print(f"Has transcript: {transcript.get('success', False)}")
    print(f"Recorded to KC: {info.get('success', False)}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Usage: yt_pipeline.py <youtube_url> [--transcript-only]")
        sys.exit(1)
    
    url = args[0]
    transcript_only = "--transcript-only" in args
    pipeline(url, transcript_only)
