# New Video Detection Algorithm

## Overview

The YouTube channel monitor uses a **snapshot comparison** approach to detect new videos. Each run produces a `latest.json` cache file containing the current top 5 videos per channel. New videos are detected by comparing the current snapshot against the previous snapshot.

## Algorithm

### Data Structure

```json
{
  "timestamp": "2026-07-18T07:43:32.506021+00:00",
  "channels": {
    "easy_traff": {
      "url": "https://www.youtube.com/@YOSArun/videos",
      "topic": "cpa-arbitrage",
      "videos": [
        {"id": "QCURb_DkMwg", "title": "...", "url": "...", "duration": "...", "uploaded": null, "playlist_index": 1},
        ...
      ]
    }
  }
}
```

### Detection Logic (Python)

```python
def detect_new_videos(previous: dict, current: dict) -> list[dict]:
    """Compare snapshots and return newly detected videos."""
    new_videos = []
    
    for channel_id, ch_data in current.get("channels", {}).items():
        prev_videos = previous.get("channels", {}).get(channel_id, {}).get("videos", [])
        curr_videos = ch_data.get("videos", [])
        
        # Build set of known video IDs
        known_ids = {v["id"] for v in prev_videos}
        
        # Videos in current but not in previous = new
        for video in curr_videos:
            if video["id"] not in known_ids:
                new_videos.append({
                    "channel": channel_id,
                    "topic": ch_data.get("topic"),
                    **video
                })
    
    return new_videos
```

### Key Assumptions

1. **Playlist order = recency**: YouTube's `/videos` playlist returns newest first (playlist_index 1 = latest)
2. **Flat playlist mode**: We only get top 5 videos per run, so we can only detect new videos within that window
3. **Video IDs are stable**: YouTube video IDs never change, making them perfect deduplication keys
4. **Null timestamps handled**: Some videos return `null` for `timestamp` — we rely on `playlist_index` for ordering

## Edge Cases

| Scenario | Behavior | Mitigation |
|----------|----------|------------|
| Channel uploads 6+ videos between runs | Only detects top 5; older new videos missed | Decrease interval or increase `--playlist-end` |
| Video deleted after detection | Still appears in "new" list (ID was new at detection time) | Acceptable false positive; video unavailable on click |
| Private → Public transition | Detected as new when it goes public | Correct behavior |
| Channel handle change | Channel ID stays same; URL redirect works | Use channel ID in config for stability |
| YouTube returns reordered playlist | May cause false "new" detections | Rare; YouTube playlist order is stable |

## Enhanced Detection (Future)

### Option A: Increase Window
```python
# Fetch more videos to widen detection window
"--playlist-end", "20"  # instead of 5
```
Trade-off: More API calls, longer runtime, larger cache.

### Option B: Persistent Video Registry
Maintain a separate `known_videos.json` with all ever-seen video IDs:
```json
{
  "easy_traff": ["QCURb_DkMwg", "O9wid4e3ATs", ...],
  "partnerkin": ["ZQx4ZDX97Cs", "p99YGrK4JCc", ...]
}
```
New video = ID not in registry. Registry grows unbounded (needs periodic cleanup).

### Option C: Timestamp-Based
If timestamps become reliable:
```python
last_run = previous["timestamp"]
new_videos = [v for v in curr_videos if v.get("timestamp") and v["timestamp"] > last_run]
```
Requires fixing null timestamp issue.

## Current Implementation Status

- **Implemented**: Snapshot comparison in `scripts/youtube_watch.py` (manual comparison via cron output)
- **Not yet implemented**: Automated new-video-only reporting in cron job output
- **Cache location**: `D:/Portable_Soft/hermes/cache/youtube_watch/latest.json`
- **Previous snapshots**: Not retained (overwritten each run) — add rotation if history needed

## Reporting Format

When new videos detected, cron output should include:

```
=== NEW VIDEOS DETECTED ===

📺 @YOSArun (easy_traff)
  1. [NEW] Лимасол глазами аффилиатов... (1:26:34) — https://youtu.be/QCURb_DkMwg

📺 @partnerkin
  1. [NEW] Арбитражники палят доходы... (2:41:38) — https://youtu.be/ZQx4ZDX97Cs

Total: 2 new videos since last check (2026-07-18 04:42 UTC)
```

## Testing Detection Logic

```python
# Test with two cache snapshots
import json

with open("cache/youtube_watch/latest.json") as f:
    current = json.load(f)

# Simulate previous (remove first video from each channel)
previous = json.loads(json.dumps(current))
for ch in previous["channels"].values():
    if ch.get("videos"):
        ch["videos"] = ch["videos"][1:]

new = detect_new_videos(previous, current)
print(f"Detected {len(new)} new videos")
for v in new:
    print(f"  {v['channel']}: {v['title'][:50]}...")
```