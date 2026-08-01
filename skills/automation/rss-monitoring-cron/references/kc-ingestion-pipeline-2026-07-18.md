# RSS/YouTube → Knowledge Cube Ingestion Pipeline

**Problem identified 2026-07-18:** RSS monitor (`rss_monitor.py`) and YouTube watch (`youtube_watch.py`) fetch external content and cache to JSON, but **results never enter Knowledge Cube**. This is why external knowledge ratio is stuck at 14% (44/307 KC entries).

## Current Architecture

```
RSS Monitor (cron 4h)  ──→ cache/rss_monitor/latest.json
YouTube Watch (cron 6h) ──→ cache/youtube_watch/latest.json
                              │
                              ▼
                    [MISSING: KC Ingestion]
                              │
                              ▼
                    Knowledge Cube (kc_entries + experiences)
```

## Required Pipeline Components

### 1. RSS → KC Ingestion (add to `cube_feeder.py`)

```python
def read_rss_monitor_cache():
    """Read cache/rss_monitor/latest.json, convert to KC entries."""
    cache_path = CACHE_DIR / "rss_monitor" / "latest.json"
    if not cache_path.exists():
        return []
    
    data = json.loads(cache_path.read_text(encoding="utf-8"))
    entries = []
    
    for feed_id, articles in data.get("feeds", {}).items():
        for article in articles:
            # Skip if no tags (not notable)
            if not article.get("tags"):
                continue
            
            text = f"[{article['topic'].upper()}] {article['title']}. {article.get('summary', '')}"
            if article.get("tags"):
                text += f" Tags: {', '.join(article['tags'])}"
            
            entries.append({
                "text": text[:800],
                "tools": [],
                "source": f"rss_{feed_id}",
                "tags": ["source:rss", f"topic:{article['topic']}"] + article.get("tags", []),
            })
    
    return entries
```

### 2. YouTube → KC Ingestion (add to `cube_feeder.py`)

```python
def read_youtube_watch_cache():
    """Read cache/youtube_watch/latest.json, convert to KC entries."""
    cache_path = CACHE_DIR / "youtube_watch" / "latest.json"
    if not cache_path.exists():
        return []
    
    data = json.loads(cache_path.read_text(encoding="utf-8"))
    entries = []
    
    for channel_id, channel_data in data.get("channels", {}).items():
        for video in channel_data.get("videos", []):
            text = f"[YOUTUBE:{channel_data['topic']}] {video['title']}. {video.get('url', '')}"
            entries.append({
                "text": text[:800],
                "tools": [],
                "source": f"youtube_{channel_id}",
                "tags": ["source:youtube", f"topic:{channel_data['topic']}"],
            })
    
    return entries
```

### 3. Wire into `cube_feeder.py` sources

```python
# In sources dict (around line 542)
sources = {
    "lavra": read_lavra_knowledge,
    "cache": lambda: (
        read_cache_decisions() + read_cache_suggestions() + 
        read_cache_dimension_proposals() + read_cache_observer_analyses()
    ),
    "logs": read_error_logs,
    "scripts": extract_knowledge_patterns,
    "outcomes": read_cache_outcomes,
    "rss": read_rss_monitor_cache,        # NEW
    "youtube": read_youtube_watch_cache,  # NEW
}
```

### 4. Cron Job Updates

**Option A:** Add to existing `cube-feeder` cron (runs every 6h)
```json
{
  "name": "cube-feeder",
  "script": "scripts/cube_feeder.py",
  "schedule": { "kind": "cron", "expr": "0 */6 * * *" }
}
```
Just add "rss" and "youtube" to the default `--source all` run.

**Option B:** Dedicated cron for freshness (runs 30min after RSS/YouTube)
```json
{
  "name": "kc-ingest-external",
  "script": "scripts/cube_feeder.py --source rss --source youtube",
  "schedule": { "kind": "interval", "minutes": 150 }  # after RSS (240) + YouTube (360)
}
```

## Expected Impact

| Source | Entries/run | Runs/day | Entries/day | KC entries/week |
|--------|-------------|----------|-------------|-----------------|
| RSS (5 feeds) | ~30 notable | 6 | ~180 | ~1,260 |
| YouTube (2 channels) | ~10 | 4 | ~40 | ~280 |
| **Total external** | | | **~220** | **~1,540** |

Current external: **44 total** → With pipeline: **~1,500/week** → **30%+ ratio achieved in 2 weeks**.

## Reddit & GitHub Sources (Next Phase)

Add to `rss_monitor.py` FEEDS or new `reddit_monitor.py`:

```python
REDDIT_FEEDS = [
    {"id": "affiliatemarketing", "url": "https://www.reddit.com/r/affiliatemarketing/.rss", "topic": "cpa"},
    {"id": "passive_income", "url": "https://www.reddit.com/r/passive_income/.rss", "topic": "cpa"},
    {"id": "crypto", "url": "https://www.reddit.com/r/crypto/.rss", "topic": "crypto"},
]

GITHUB_TRENDING = [
    {"id": "ai-automation", "url": "https://github.com/trending/python?since=daily", "topic": "automation"},
    {"id": "ml-ops", "url": "https://github.com/trending/python?since=weekly&q=ml", "topic": "mlops"},
]
```

## Verification Checklist

- [ ] Add `read_rss_monitor_cache()` to `cube_feeder.py`
- [ ] Add `read_youtube_watch_cache()` to `cube_feeder.py`
- [ ] Add "rss" and "youtube" to sources dict
- [ ] Test: `python scripts/cube_feeder.py --source rss --source youtube`
- [ ] Verify new KC entries have `source: rss_partnerkin` etc.
- [ ] Update `cube-feeder` cron or add `kc-ingest-external` cron
- [ ] Monitor: external KC entries grow from 44 → 100+ in week 1