# ytInitialData HTML Parsing — Working Extraction Technique (2026-07-29)

## Context
Session where youtube-transcript-api, yt-dlp, and web_extract all failed (SSL blocks, RequestBlocked, geo-restrictions). Extracted video descriptions via ytInitialData from raw HTML.

## Videos Processed
| Video ID | Title | Channel | Method |
|----------|-------|---------|--------|
| NruUz9KHwYQ | 50 Real Ways to Use Hermes Agent... | Georgy Rivera | ytInitialData via proxy |
| GkHwnQdoDpM | 10 Free Skills for Claude AI... | Georgy Rivera | ytInitialData via proxy |

## Working Pipeline

### 1. Detect Proxy (Windows/v2rayN)
```bash
# Check v2rayN process
tasklist /FI "IMAGENAME eq v2rayN.exe"

# Scan common ports
for port in 10806 10808 10809 1080 1081; do
  curl -s --connect-timeout 2 -x http://127.0.0.1:$port \
    https://www.google.com -o /dev/null -w "$port=%{http_code}\n"
done

# Verified: 127.0.0.1:10806 (HTTP+SOCKS5)
```

### 2. Download HTML via curl + proxy
```bash
curl -s --max-time 30 --proxy http://127.0.0.1:10806 \
  "https://www.youtube.com/watch?v=VIDEO_ID" > /tmp/yt_page.html
```

### 3. Extract ytInitialData JSON
```python
import re, json

with open('/tmp/yt_page.html', 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'ytInitialData\s*=\s*(\{.+?\});', content, re.DOTALL)
if m:
    data = json.loads(m.group(1))
```

### 4. Find attributedDescription
```python
raw = json.dumps(data, ensure_ascii=False)
idx = raw.find('attributedDescription')
if idx != -1:
    chunk = raw[idx:idx+20000]
    start_idx = chunk.find('"content":"')
    if start_idx != -1:
        start_idx += len('"content":"')
        # Find end of content (next JSON key)
        search_start = start_idx
        while True:
            end_idx = chunk.find('",\n', search_start)
            if end_idx == -1:
                end_idx = chunk.find('","', search_start)
            if end_idx == -1:
                break
            remainder = chunk[end_idx+1:end_idx+30].strip()
            if remainder.startswith('"') and len(remainder) > 2 and remainder[1].isalpha():
                desc = chunk[start_idx:end_idx]
                break
            search_start = end_idx + 3
        
        # Unescape
        desc = desc.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
        desc = desc.replace('\\xa0', ' ')
        desc = re.sub(r'\\u[0-9a-fA-F]{4}', lambda m: chr(int(m.group(0)[2:], 16)), desc)
        print(desc)
```

## Built-in Script
`skills/media/youtube-transcript/scripts/yt_extract_desc.py` — handles retries for SSL errors (exit 35).

Usage:
```bash
python skills/media/youtube-transcript/scripts/yt_extract_desc.py VIDEO_ID http://127.0.0.1:10806
```

## Key Insights
1. **HTML parsing works when APIs fail** — YouTube doesn't block page views, only API endpoints
2. **Proxy is mandatory** — v2rayN on 10806 worked; direct connection failed with SSLEOFError
3. **attributedDescription contains full description** — timestamps, links, repo lists, tools
4. **No rate limits on HTML** — unlike Innertube API
5. **Not a transcript** — only description, but enough for schemes/patterns/tools extraction

## Rule I Compliance
Raw description → extracted schemes/patterns/tools → saved to Knowledge Cube → **skill artifact created** (`riverapeople-youtube-schemes`).

## Related
- `scripts/yt_extract_desc.py` — production script with retries
- `scripts/clean_vtt.py` — VTT deduplication for when transcripts ARE available
- Skill: `riverapeople-youtube-schemes` — output artifact from this technique