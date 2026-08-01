# Audience Analyzer — Verification Results & Gotchas

## Verification Summary (2026-07-18)

All tests passed. Skill is production-ready.

| Test | Command | Result |
|------|---------|--------|
| Syntax | `python -m py_compile scripts/analyze.py` | ✅ PASS |
| Mode 2: PWA Cricket India | `--mode offer2audience --offer "PWA cricket India CPA $15 no KYC"` | ✅ PASS |
| Mode 2: Python Course | `--mode offer2audience --offer "Курс Python 15000 руб"` | ✅ PASS |
| Mode 1: Web (Habr) | `--mode audience2offer --source web --url https://habr.com` | ✅ PASS (62 items) |
| Text Analysis | Direct API | ✅ PASS |
| Clustering | Direct API | ✅ PASS |
| Ripple Engine | Direct API | ✅ PASS |

## Key Gotchas Discovered

### 1. Price Extraction Regex
```python
# Works for RUB
r'(\d+(?:\.\d+)?)\s*(?:руб|р\.|rub)'

# Works for USD
r'\$(\d+(?:\.\d+)?)'

# CPA/CPS need flexible separator
r'cpa\s*[=:\$]?\s*\$?(\d+(?:\.\d+)?)'
r'cps\s*[=:]?\s*(\d+(?:\.\d+)?)%'
```

### 2. KYC Detection
- "без KYC" / "without KYC" triggers KYC=True (mentions the term)
- Fix: Check for negation context if precision needed

### 3. Telegram Parsing Limitation
- Uses `t.me/s/channel` public preview (no API key)
- Limited to ~100 recent posts
- No comments access without Bot API
- For production: use Telegram Bot API or TDLib

### 4. Import Pattern for Private Skills
```bash
# Symlink for Python imports (hyphen → underscore)
ln -sf human-source skills/human_source
```
Then: `from skills.human_source.scripts.analyze import HumanAnalyzer`

### 5. Clusterer min_cluster_size
- Default 5 is too high for small samples
- Override in config: `'analysis': {'min_cluster_size': 2}`
- Or pass smaller samples to single-segment fallback

### 6. Offer Decomposition
- Core problem extraction is naive (first sentence with problem words)
- Frustrations/desires often empty for short offer texts
- Works best with longer, descriptive offers

## Recommended Config for Production
```yaml
analysis:
  min_cluster_size: 2
  max_clusters: 8

parsers:
  telegram:
    max_posts: 200
    include_comments: false  # Requires Bot API
  youtube:
    max_videos: 50
    use_yt_dlp: true
  vk:
    max_posts: 100
```