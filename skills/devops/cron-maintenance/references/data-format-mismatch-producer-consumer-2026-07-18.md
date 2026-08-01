# Data Format Mismatch Between Producer/Consumer Cron Scripts

**Date:** 2026-07-18
**Session:** Fixed `daily_digest.py` AttributeError from `rss_monitor.py` format change

## Problem

`daily_digest.py` (consumer) crashed with:
```
AttributeError: 'list' object has no attribute 'get'
  File "scripts/daily_digest.py", line 78, in get_rss
    cat = cm.get(fd.get("topic", "?"), f"📄 {fd.get('topic','?')}")
```

Root cause: **Producer script (`rss_monitor.py`) changed its output format**, but consumer script (`daily_digest.py`) wasn't updated to handle the new format.

### Old Format (expected by consumer)
```json
{
  "feeds": {
    "partnerkin": {
      "topic": "cpa-news",
      "entries": [...]
    }
  }
}
```

### New Format (produced by rss_monitor.py)
```json
{
  "feeds": {
    "partnerkin": [...]  // List of entries directly, no wrapper dict
  }
}
```

## Root Cause

`rss_monitor.py` saves cache as:
```python
cache_data = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "feeds": feed_results,  # feed_results = {feed_id: list[entries]}
}
```

But `daily_digest.py` expected each feed to be a dict with `topic` and `entries` keys.

## Fix Applied

Updated `get_rss()` in `daily_digest.py` to:
1. Handle both formats (list of entries OR dict with `entries` key)
2. Map feed IDs to topics via explicit `topic_map` since the topic is no longer in the feed data

```python
topic_map = {
    "partnerkin": "cpa-news",
    "affiliatefix": "cpa-news",
    "openai_blog": "ai",
    "anthropic_rsshub": "ai",
    "hackernews": "tech",
}
topic = topic_map.get(fid, "?")
cat = cm.get(topic, f"📄 {topic}")
for e in fd if isinstance(fd, list) else fd.get("entries", []):
    # process entry
```

## Prevention Pattern

**When producer and consumer are separate cron scripts:**

1. **Version the cache format** — add a `version` field to cache data
2. **Consumer handles multiple versions** — check `version` or detect format by structure
3. **Shared schema definition** — define expected format in a shared module or JSON schema
4. **Test consumer against producer output** — run consumer after producer in cron order

## Detection Checklist

When a cron consumer fails with attribute/key errors on producer data:

- [ ] Check producer's `save_cache()` / output format
- [ ] Compare with consumer's expected format
- [ ] Look for recent changes to producer script
- [ ] Add defensive coding in consumer (type checks, `.get()` with defaults)

## Related

- `references/cron-cleanup-2026-06-28.md` — general cron maintenance
- `references/broken-cron-repair-2026-07-12.md` — fixing failing cron scripts