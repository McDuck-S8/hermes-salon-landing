#!/usr/bin/env python3
"""YouTube channel monitor — проверяет новые видео через yt-dlp.

Использует --flat-playlist + --socket-timeout 5 чтобы не виснуть.
Результат: cache/youtube_watch/latest.json + report.
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

CACHE_DIR = Path("D:/Portable_Soft/hermes/cache/youtube_watch")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CHANNELS = [
    {"id": "easy_traff",      "url": "https://www.youtube.com/@YOSArun/videos",    "topic": "cpa-arbitrage"},
    {"id": "partnerkin",      "url": "https://www.youtube.com/@partnerkin/videos",     "topic": "cpa-affiliate"},
]

def fetch_channel(channel):
    """Get latest 5 videos from a YouTube channel with descriptions."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--socket-timeout", "10", "--flat-playlist",
             "--dump-json", "--playlist-end", "5",
             "--no-warnings", channel["url"]],
            capture_output=True, text=True, timeout=90
        )
        if result.returncode != 0:
            return {"error": result.stderr.strip()[:200], "videos": []}
        
        videos = []
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                desc = data.get("description", "") or ""
                videos.append({
                    "id": data.get("id"),
                    "title": data.get("title"),
                    "url": f"https://youtube.com/watch?v={data.get('id')}",
                    "duration": data.get("duration_string"),
                    "uploaded": data.get("timestamp"),
                    "playlist_index": data.get("playlist_index"),
                    "description": desc[:2000],  # first 2000 chars
                    "tags": data.get("tags", []),
                })
            except json.JSONDecodeError:
                continue
        return {"videos": videos}
    except subprocess.TimeoutExpired:
        return {"error": "timeout (30s)", "videos": []}
    except FileNotFoundError:
        return {"error": "yt-dlp not found", "videos": []}

def main():
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "channels": {}
    }
    
    for ch in CHANNELS:
        print(f"[youtube_watch] Checking {ch['id']}...", flush=True)
        result = fetch_channel(ch)
        report["channels"][ch["id"]] = {
            "url": ch["url"],
            "topic": ch["topic"],
            **result
        }
        if "error" in result:
            print(f"  ERROR: {result['error']}")
        else:
            print(f"  OK: {len(result['videos'])} videos")
    
    # Save
    report_path = CACHE_DIR / "latest.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    
    # Generate summary
    total = sum(1 for c in report["channels"].values() if "error" not in c)
    errors = sum(1 for c in report["channels"].values() if "error" in c)
    videos = sum(len(c.get("videos", [])) for c in report["channels"].values())
    
    print(f"\nDone: {total}/{len(CHANNELS)} channels OK, {errors} errors, {videos} total videos")

if __name__ == "__main__":
    main()
