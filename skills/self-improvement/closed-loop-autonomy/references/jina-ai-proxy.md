# jina.ai Proxy for Blocked APIs

## Problem
HN Firebase API, GitHub trending, and other APIs are blocked on Russian IPs (185.x.x.x) without VPN/SOCKS proxy.

## Solution
jina.ai summarizer acts as a proxy: `r.jina.ai/http://<target-url>`

## Working Examples (2026-06-29)
```bash
# HN top stories (returns JSON array of IDs)
curl -s --connect-timeout 10 "https://r.jina.ai/http://hacker-news.firebaseio.com/v0/topstories.json"

# HN story detail (returns markdown with title, URL, score)
curl -s --connect-timeout 10 "https://r.jina.ai/http://hacker-news.firebaseio.com/v0/item/48717287.json"

# GitHub trending (returns markdown page)
curl -s --connect-timeout 10 "https://r.jina.ai/https://github.com/trending"
```

## Python Implementation
```python
def http_get(url, timeout=15):
    """GET with timeout. Returns parsed JSON or None."""
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "Hermes/1.0"})
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None

# HN via jina.ai
data = http_get("https://r.jina.ai/http://hacker-news.firebaseio.com/v0/topstories.json")
# Returns: [48717287, 48717758, ...] (JSON array of story IDs)
```

## Limitations
- Rate limiting: ~10 requests/minute
- HN stories: fetch 1 at a time (not batch)
- Timeout: 15s recommended (30s for slow sources)
- Response format: JSON for API endpoints, markdown for web pages

## Sources Working via jina.ai
- HN Firebase API (stories, comments)
- RSS feeds (Ars Technica, The Hacker News)
- GitHub trending page

## Sources NOT Working (even via jina.ai)
- Some RSS feeds with complex XML
- Sites requiring authentication
- WebSocket endpoints

## Pitfall
- Don't use limit > 3 for HN — jina.ai rate-limits batch requests
- Parse markdown responses carefully — they're not JSON
- Always set timeout=15s minimum — jina.ai can be slow
