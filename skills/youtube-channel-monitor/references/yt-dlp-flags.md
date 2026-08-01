# yt-dlp Flag Reference — YouTube Channel Monitoring

## Current Production Command

```bash
yt-dlp --socket-timeout 10 --flat-playlist --dump-json --playlist-end 5 --no-warnings "<channel_url>"
```

### Flag Breakdown

| Flag | Value | Purpose |
|------|-------|---------|
| `--socket-timeout` | 10 | Fail fast on slow connections (prevents hangs) |
| `--flat-playlist` | (bool) | Extract only playlist entries, don't download video info for each |
| `--dump-json` | (bool) | Output each entry as JSON line (machine-parseable) |
| `--playlist-end` | 5 | Limit to N newest videos (1 = only latest) |
| `--no-warnings` | (bool) | Suppress stderr noise (non-fatal warnings) |

## Alternative Configurations

### Maximum Detail (for deep analysis)
```bash
yt-dlp --socket-timeout 30 --flat-playlist --dump-json --playlist-end 10 --no-warnings \
  --write-info-json --write-thumbnail --write-description "<channel_url>"
```

### Date-Filtered (only last 7 days)
```bash
yt-dlp --socket-timeout 10 --flat-playlist --dump-json --no-warnings \
  --dateafter now-7days "<channel_url>"
```

### Full Metadata (no flat playlist)
```bash
yt-dlp --socket-timeout 10 --dump-json --playlist-end 5 --no-warnings \
  --write-info-json --write-thumbnail --write-description --write-subs --sub-lang en,ru \
  --embed-subs --embed-thumbnail --embed-metadata "<channel_url>"
```

## Output Fields (flat playlist mode)

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `id` | string | `QCURb_DkMwg` | Video ID |
| `title` | string | `Video Title` | Full title |
| `url` | string | `https://youtube.com/watch?v=QCURb_DkMwg` | Watch URL |
| `duration_string` | string | `1:26:34` | Human-readable duration |
| `timestamp` | integer | `1721300000` | Unix timestamp (may be null) |
| `playlist_index` | integer | `1` | Position in playlist (1 = newest) |
| `channel` | string | `EasyTraff` | Channel name |
| `channel_id` | string | `UCxxx` | Channel ID |
| `view_count` | integer | `15000` | View count (may be null in flat mode) |

## Error Handling Patterns

### Timeout
```bash
# Increase timeout for slow channels
--socket-timeout 30
```

### Rate Limiting (429 Too Many Requests)
```bash
# Add delays and retries
--sleep-interval 5 --max-sleep-interval 15 --retries 3
```

### Geo-Blocking / Age-Restricted
```bash
# Use cookies from browser
--cookies-from-browser chrome
```

### Private/Deleted Videos
```bash
# Skip unavailable videos
--ignore-errors --no-abort-on-error
```

## Windows-Specific Notes

- Use `yt-dlp.exe` directly if in PATH, or full path: `D:\Portable_Soft\hermes\.venv\Scripts\yt-dlp.exe`
- Path separators: forward slashes work in yt-dlp args, backslashes in Windows paths
- PowerShell requires `--` before URL if URL contains `&` or `?`

## Testing Commands

```bash
# Quick test - single video from channel
yt-dlp --flat-playlist --playlist-end 1 --dump-json "https://www.youtube.com/@YOSArun/videos"

# Test with timing
time yt-dlp --socket-timeout 10 --flat-playlist --dump-json --playlist-end 5 "https://www.youtube.com/@YOSArun/videos"

# Validate JSON output
yt-dlp --flat-playlist --playlist-end 1 --dump-json "https://www.youtube.com/@YOSArun/videos" | python -m json.tool
```

## Version Pinning

```bash
# Check version
yt-dlp --version

# Update
yt-dlp -U

# Pin in requirements.txt
yt-dlp==2024.12.04
```

## Debugging Flags

```bash
# Verbose output
-v

# Print extractor info
--extractor-descriptions

# Dry run (no download, no output)
--simulate
```