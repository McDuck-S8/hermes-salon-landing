# Video Resource Extraction — JS Selectors Reference

## YouTube Description DOM Selectors

These work on standard YouTube watch pages (youtube.com/watch?v=...).

### All GitHub links (redirect-aware)
```javascript
// Catches both direct and YouTube-redirect links containing github.com
Array.from(document.querySelectorAll('a[href*="github.com"]')).map(a => a.href).join('\n')
```

### Direct (non-redirect) links only
```javascript
// YouTube wraps most links in redirects, but some may be direct
Array.from(document.querySelectorAll('#description a')).map(a => a.href).join('\n')
```

### Full description text
```javascript
// CURRENT (ytd-watch-metadata — use this first)
document.querySelector('ytd-watch-metadata')?.textContent

// LEGACY (may still work on older layouts)
document.querySelector('#description yt-formatted-string')?.innerText
|| document.querySelector('#description')?.textContent
```

### Video title
```javascript
document.querySelector('h1 yt-formatted-string')?.innerText
```

### Channel name
```javascript
document.querySelector('#owner yt-formatted-string a')?.innerText
```

### View count and publish date
```javascript
document.querySelector('#info-container span:nth-child(3)')?.innerText
```

### Count of all GitHub links on page
```javascript
document.querySelectorAll('a[href*="github.com"]').length
```

## Known Pitfalls by Selector Target

| Selector Target | Risk | Mitigation |
|-----------------|------|------------|
| `#description yt-formatted-string` | Empty on long/truncated descriptions; YouTube DOM may have moved to `ytd-watch-metadata` | Use `ytd-watch-metadata` as primary, `#description` as fallback |
| `a[href*="github.com"]` | Misses URLs that YouTube doesn't rewrite | Combine with `#description a` for completeness |
| `#info-container span:nth-child(3)` | YouTube A/B tests; selector may shift | Adjust nth-child or inspect structure first |
| `browser_snapshot()` content | LLM-summarized/truncated for long pages | Use `full=true` for complete snapshot; for descriptions, prefer JS extraction from `ytd-watch-metadata` |
| `web_extract()` on YouTube | Provider-dependent; may fail with SSL | Fall back to browser tools |
| `browser_click` on "...ещё" | Expands DOM text but A11Y tree may stay truncated | Always extract raw text via JS (`ytd-watch-metadata?.textContent`) after clicking |
| `browser_vision` on YouTube | May be blocked by security policy | Don't rely on it; use JS DOM queries instead |

## Real Example — Cloud Codes Video (jgsDu9MubJM)

The JS one-liner returned 38 hrefs from a single querySelectorAll call, covering all 19 GitHub repos mentioned in the video (each appeared twice — once in the visible section, once in the "more" section).

Output format example:
```
https://www.youtube.com/redirect?event=video_description&redir_token=TOKEN&q=https%3A%2F%2Fgithub.com%2FfreeCodeCamp%2FfreeCodeCamp&v=jgsDu9MubJM
https://www.youtube.com/redirect?event=video_description&redir_token=TOKEN&q=https%3A%2F%2Fgithub.com%2Fcodecrafters-io%2Fbuild-your-own-x&v=jgsDu9MubJM
...
```

The URL-encoded `q=` parameter contains the actual GitHub URL. To decode it server-side:
```ruby
# Ruby
URI.decode_www_form_component(uri.query[/q=([^&]+)/, 1])

# Python
from urllib.parse import unquote, urlparse, parse_qs
parsed = urlparse(redirect_url)
github_url = unquote(parse_qs(parsed.query)['q'][0])

# Manual
Copy the raw href, extract the q= parameter value, URL-decode it
(https%3A%2F%2Fgithub.com%2Fowner%2Frepo → https://github.com/owner/repo)
```

## Browser Fallback Order

When browser is unavailable (SSL error, timeout, region block):

1. `web_search(query="site:youtube.com VIDEO_ID")` — Google often caches video descriptions
2. `web_search(query="linkedin.com \"VIDEO_TITLE\"")` — LinkedIn posts sometimes republish description
3. `web_search(query="\"VIDEO_TITLE\" github")` — associated repos often indexed separately
4. `curl -s "https://noembed.com/embed?url=https://www.youtube.com/watch?v=VIDEO_ID"` — metadata only
