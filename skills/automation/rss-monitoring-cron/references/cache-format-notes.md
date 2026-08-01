# Cache Format Notes (rss_monitor.py)

## Format Evolution

**Old format (pre-2026-07-18):**
```json
{
  "timestamp": "2026-07-17T19:26:30.681655+00:00",
  "feeds": {
    "partnerkin": {
      "url": "https://partnerkin.com/rss",
      "topic": "cpa-news",
      "entries": [ ... ]
    }
  }
}
```

**New format (current):**
```json
{
  "timestamp": "2026-07-18T...",
  "feeds": {
    "partnerkin": [ ... ],
    "affiliatefix": [ ... ]
  }
}
```

## Handling in Code

The `load_cache()` function in `scripts/rss_monitor.py` handles both formats:

```python
for feed_data in old_cache.get("feeds", {}).values():
    if isinstance(feed_data, dict) and "entries" in feed_data:
        entries = feed_data["entries"]
    elif isinstance(feed_data, list):
        entries = feed_data
    else:
        continue
    for e in entries:
        if isinstance(e, dict):
            old_urls.add(e.get("url", ""))
```

## Script Status (2026-07-18)

- **Script created**: `D:/Portable_Soft/hermes/scripts/rss_monitor.py`
- **Dependencies**: `feedparser`, `beautifulsoup4`, `lxml`, `requests` (install via `uv pip install ...`)
- **Verified**: Syntax OK, imports resolve, digest generation works, notable detection works
- **Environmental blocker**: SSL EOF / timeout on all 5 feeds (network/proxy issue, not code)

## Notable Articles from Last Successful Run (2026-07-17)

Total: 53 entries, 32 notable across 5 feeds.

See session output for full breakdown by feed.