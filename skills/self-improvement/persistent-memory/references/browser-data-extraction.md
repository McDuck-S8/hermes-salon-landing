# Browser Data Extraction — Digital Fingerprint

## Purpose
Extract user's browsing history and bookmarks from Chromium-based browsers to build a digital fingerprint for user profiling and monetization planning.

## Browser Locations (Windows)

| Browser | History | Bookmarks |
|---------|---------|-----------|
| Chrome | %LOCALAPPDATA%/Google/Chrome/User Data/Default/History | %LOCALAPPDATA%/Google/Chrome/User Data/Default/Bookmarks |
| Edge | %LOCALAPPDATA%/Microsoft/Edge/User Data/Default/History | %LOCALAPPDATA%/Microsoft/Edge/User Data/Default/Bookmarks |
| **Comet Perplexity** | %LOCALAPPDATA%/Perplexity/Comet/User Data/Default/History | %LOCALAPPDATA%/Perplexity/Comet/User Data/Default/Bookmarks |
| Comet P2 | %LOCALAPPDATA%/Perplexity/Comet/User Data/Profile 2/History | %LOCALAPPDATA%/Perplexity/Comet/User Data/Profile 2/Bookmarks |

**CRITICAL: User uses Comet Perplexity, NOT Chrome/Firefox/Edge. Always check Comet first.**

## Extraction Steps

1. **Copy files** (never work on originals — may be locked):
   ```bash
   mkdir -p cache/digital_fingerprint
   cp "$LOCALAPPDATA/Perplexity/Comet/User Data/Profile 2/History" cache/digital_fingerprint/comet_p2_history.db
   cp "$LOCALAPPDATA/Perplexity/Comet/User Data/Profile 2/Bookmarks" cache/digital_fingerprint/comet_p2_bookmarks.json
   ```

2. **Query history** (SQLite, Chromium format):
   ```sql
   SELECT url, title, visit_count, last_visit_time FROM urls ORDER BY visit_count DESC;
   ```
   - Chrome timestamp: microseconds since 1601-01-01
   - Convert: `datetime(1601,1,1) + timedelta(microseconds=ts)`

3. **Parse bookmarks** (JSON, nested structure):
   ```python
   def extract_all(node, result, path=""):
       if node.get("type") == "url":
           result.append({"name": node["name"], "url": node["url"], "path": path})
       for child in node.get("children", []):
           extract_all(child, result, f"{path}/{node['name']}" if path else node["name"])
   ```

4. **Classify domains** into themes: AI/LLM, YouTube, GitHub, Shopping, Finance, Social, Dev, etc.

5. **Analyze**: top domains by visits, theme clusters, time trends, bookmarks without visits (gaps), tools used.

6. **Output**: DIGITAL_FINGERPRINT.md + goal_queue entries for monetization opportunities.

## Pitfalls
- Chromium locks History DB while browser is running → always copy first
- Bookmarks JSON is deeply nested with folders → recursive extraction needed
- Chrome timestamps are microseconds since 1601-01-01 (not Unix epoch)
- Profile 2 may be the main profile even if Default exists → check file sizes
- Large histories (19MB+) → use execute_code for batch processing, not terminal
