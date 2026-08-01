# curl Fallback for Web Research

When web_search/web_extract fail (SSL errors, proxy issues, network timeouts), use curl via terminal.

## Hacker News

```bash
# Get top stories with titles and scores
curl -s "https://news.ycombinator.com/" | grep -oP '<span class="titleline"><a href="[^"]*">[^<]*</a>' | head -20

# Get scores
curl -s "https://news.ycombinator.com/" | grep -oP '<span class="score"[^>]*>[^<]*</span>' | head -20
```

## GitHub Trending

```bash
# Extract trending repo names
curl -s "https://github.com/trending" | grep -oP 'href="/[^"]+/[^"]*"' | grep -v 'stargazers\|forks\|sponsors' | head -20

# Get repo details via API
curl -s "https://api.github.com/repos/owner/repo" | grep -oP '"description":"[^"]*"|"stargazers_count":[0-9]+'
```

## Product Hunt

```bash
# Basic page fetch (no API key needed)
curl -s "https://www.producthunt.com/" | grep -oP '<a[^>]*href="/posts/[^"]*"[^>]*>[^<]*</a>' | head -20
```

## Generic Site Scraping

```bash
# Extract all links
curl -s "https://example.com" | grep -oP 'href="[^"]*"' | head -30

# Extract text content (strip HTML)
curl -s "https://example.com" | sed 's/<[^>]*>//g' | grep -v '^\s*$' | head -50
```

## Notes

- curl works through most proxies that block browser-based tools
- No API keys needed for HN, GitHub trending
- GitHub API has rate limits (60 req/hour unauthenticated)
- For complex pages, combine with python -c for HTML parsing
