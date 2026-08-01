---
name: youtube-research
description: "YouTube video search AND research: keyword-based search via BrowserClaw, description extraction, link harvesting, source verification, and multi-resource research compilation."
platforms: [linux, macos, windows]
---

# YouTube Video Research

## When to Use

YouTube is your **primary information source** — not a side task or fallback. Treat it as your food supply. Every session should include YouTube mining unless the task explicitly forbids it.

Use when the user asks you to **search YouTube** for content by keyword OR when they share a specific YouTube URL for research. Also use when you need to:

- **Mine a channel systematically** — get ALL videos from a channel, not just search results
- **Extract the value model** from a video (not just the topic/scheme)
- **Study creator format** — how titles, descriptions, and funnels are structured
- **Build assets** from YouTube findings (KC entries, prototypes, blueprints)
- Apply the **two-level value extraction**: Level 1 = the business itself, Level 2 = the meta-business of documenting Level 1

- **Search YouTube** for videos on a topic, compile results with metadata (views, channel, age)
- Extract all GitHub links from a YouTube video description
- Find out what tools/projects a video references
- Verify that a video URL matches the user's description of it (creator, topic)
- Research a specific tool (OpenSpec, Stripe Minions, Claude Code workflows, etc.) across multiple sources
- Compile a structured research report from video + web sources

## Technique: BrowserClaw YouTube Search (Recommended for Search Queries)

The regular Hermes browser tools (`browser_navigate`) hit YouTube's cookie consent wall and bot detection on results pages. **BrowserClaw MCP tools** bypass this cleanly (CDP-based, no cookie intercept).

### Step 1: Create a new tab with search URL

```python
mcp__browserclaw__tabs(
    action="new",
    url="https://www.youtube.com/results?search_query=URL_ENCODED_QUERY"
)
```

### Step 2: Wait and extract results

The `mcp__browserclaw__read()` tool is more reliable than `snapshot()` for YouTube:

```python
# Wait for page to settle
mcp__browserclaw__wait(page=N)
# Extract clean text with titles, views, channels
result = mcp__browserclaw__read(page=N, format="text")
```

Returns: video title, view count, channel name, publish date, description excerpt, chapters.

### Step 3: Multi-language strategy (global coverage)

Search in both the user's language AND English:

```python
# Russian query
mcp__browserclaw__tabs(action="new", url="https://www.youtube.com/results?search_query=RU_TOPIC")
# English query for same topic
mcp__browserclaw__tabs(action="new", url="https://www.youtube.com/results?search_query=EN_TOPIC")
```

YouTube's built-in cross-language indexing means English search also returns Russian-titled videos with translated descriptions, and vice versa.

### Step 4: Compile results

Group by language, include: title (original), views, channel, age, key metadata from description excerpt. Present structured list with direct links.

## Technique: Browser-Based Description Extraction

YouTube video descriptions are NOT accessible via simple `web_extract()` — they're dynamically loaded. Use the browser tools:

### Step 1: Navigate to the video

```
browser_navigate(url="https://www.youtube.com/watch?v=VIDEO_ID")
```

### Step 2: Extract all GitHub links in one shot

The description contains redirect-tracked links. Use a JS querySelectorAll to grab them all:

```javascript
// Extract ALL hrefs containing "github.com" — catches both direct and redirect links
Array.from(document.querySelectorAll('a[href*="github.com"]')).map(a => a.href).join('\n')
```

This returns output like:
```
https://www.youtube.com/redirect?event=video_description&...&q=https%3A%2F%2Fgithub.com%2Fowner%2Frepo&v=VIDEO_ID
...
```

For a cleaner list, also extract via the page snapshot or the visible text links.

### Step 3: Extract the full description text

```javascript
// Primary: ytd-watch-metadata (current YouTube DOM as of mid-2026)
document.querySelector('ytd-watch-metadata')?.textContent

// Fallback: #description (older layout, may still work)
document.querySelector('#description yt-formatted-string')?.innerText
  || document.querySelector('#description')?.textContent
```

The `ytd-watch-metadata` selector returns the raw text of the entire metadata section including view count, description, and chapter markers. It's the most robust option.

### Step 4: Get video metadata

```javascript
// Title
document.querySelector('h1 yt-formatted-string')?.innerText

// Channel name
document.querySelector('#owner yt-formatted-string a')?.innerText

// View count + date
document.querySelector('#info-container span:nth-child(3)')?.innerText
```

## Technique: Source Verification Pattern

When the user says "this is a video by Creator X about Topic Y" but the loaded page shows something different:

1. **Don't stop** — extract all links from the given URL anyway (it may still contain useful resources)
2. **Independently search** for the correct creator/topic using `web_search(query="...")`
3. **Deliver both results**: document what the given URL actually contains, plus what you found about the requested topic

Example from practice: user gave URL to a "Cloud Codes" video when they expected "Cole Medin" content. The correct approach was to:
- Extract all 19 GitHub links from the Cloud Codes video anyway
- Find Cole Medin's actual videos and repos via web_search
- Research all three requested topics (OpenSpec, Stripe Minions, Claude Code workflows) from independently found sources
- Document everything transparently

## Technique: Multi-Source Research Pipeline

For deep-dive research on specific tools mentioned in a video:

1. **Video description** — extract all links (browser_console JS)
2. **GitHub repos** — for each found repo: name, stars, description, tech stack, how it works
3. **web_extract()** — get full README from GitHub repos that are accessible
4. **web_search()** — find blog posts, analyses, related tools for each topic
5. **Cross-reference** — compare information across sources, note conflicts

## Research Compilation Format

When writing findings to a file, use this structured format (in the user's language):

```
# [Topic] Research — OKF Bundle

## Обзор
Brief overview of what was researched.

## 1. Video Analysis
- Title, creator, URL, publish date, key metadata
- All extracted links grouped by category
- Source verification notes (if URL didn't match expectations)

## 2. Tool/Repo Deep-Dives
One section per significant tool found:
### [Tool Name]
- GitHub link, stars, forks, license, tech stack
- What it does — core functionality
- Philosophy / approach
- CLI commands or API surface
- Integration possibilities

## 3. Related Content
- Other videos, blog posts, articles found during research
- Alternative/complementary tools

## 4. Applicability
- Recommendations for integration
- Priority (immediate / medium / long-term)

## 5. Master Link Table
| Ресурс | Ссылка |
|--------|--------|

*Дата создания: [date]*
```

## Technique: Channel Mining (Systematic Channel Harvest)

When a channel produces high-value content (like Chris Koerner's The Koerner Office), mine it systematically rather than via random search.

### Step 1: Search for channel content by query

```bash
curl -sL --max-time 20 --proxy socks5://127.0.0.1:10806 \
  "https://www.youtube.com/results?search_query=QUERY+KEYWORDS" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  | python -c "
import sys, re, json
html = sys.stdin.read()
# Extract video IDs and titles from ytInitialData
m = re.search(r'ytInitialData\s*=\s*({.+?});', html)
if m:
    data = json.loads(m.group(1))
    # Navigate to video renderers
    for section in data.get('contents',{}).get('twoColumnSearchResultsRenderer',{}).get('primaryContents',{}).get('sectionListRenderer',{}).get('contents',[]):
        for item in section.get('itemSectionRenderer',{}).get('contents',[]):
            vr = item.get('videoRenderer',{})
            if vr:
                vid = vr.get('videoId','')
                title = vr.get('title',{}).get('runs',[{}])[0].get('text','')
                views = vr.get('viewCountText',{}).get('simpleText','')
                print(f'{vid}|{title}|{views}')
"
```

### Step 2: Extract descriptions for promising videos

```bash
for v in VIDEO_ID1 VIDEO_ID2 VIDEO_ID3; do
  echo "=== $v ==="
  curl -sL --max-time 15 --proxy socks5://127.0.0.1:10806 \
    -H "User-Agent: Mozilla/5.0" "https://www.youtube.com/watch?v=$v" \
    | grep -oP '<title>[^<]+' | head -1 | sed 's/<title>//'
  curl -sL --max-time 15 --proxy socks5://127.0.0.1:10806 \
    -H "User-Agent: Mozilla/5.0" "https://www.youtube.com/watch?v=$v" \
    | grep -oP '"shortDescription":"[^"]+' | head -1 | sed 's/"shortDescription":"//' | sed 's/\\n/\n/g'
  echo ""
done
```

### Step 3: Classify into facets of the model

Not "new ideas" — every video is a **facet of one model**. Ask:
- What value model does this represent?
- Who does it help? (not "target audience" — who suffers from the problem?)
- How does it connect to other videos from the same channel?
- What would a Level-2 asset look like? (a guide, blueprint, or case study documenting Level 1)

### Example classification (Chris Koerner):

| Video | Facet | Value Model |
|-------|-------|-------------|
| Directory Site | AI-generated catalog | Businesses pay for listings and leads |
| Lead Gen | Local SEO capture | Recurring $500-2000/mo from lead sales |
| Postcard Business | Physical mail service | $4-5K/run connecting businesses to homeowners |
| Credit Card Consulting | Information arbitrage | Newsletter + consulting fees |
| Boring Items Flipping | Physical product resale | Low-competition niche arbitrage |

All = facets of one model: **connect someone who needs customers to someone who needs services**.

## Technique: Studying Creator Presentation Format

Don't just extract content — study HOW the creator packages it. Chris Koerner's format:

### Title formula
`[Hook] + [Result/Claim] + [Barrier]`  
Example: "The Simplest Side Hustle You Can Start Under $100"

### Description structure
1. **Call to action** (lead with value — business plan link, discount code)
2. **Case study intro** (numbers first: "$90 → $50K in a year")
3. **Exact mechanism** (no fluff: "finds local businesses in Facebook groups, closes 95% over text")
4. **Credibility** (specific dollar figures, named sources)
5. **Funnel links** (free video → $19 product → $5/mo membership → community)

### Funnel layers (Level 1 → Level 2)
- Level 1: The business itself (Josh's postcard service)
- Level 2: The meta-business (Koerner's business plan for $19, newsletter, membership)
- Both obey the same law: create value → build asset → income as side effect

## Technique: Agent Reach — Agent Internet Access (NEW 2026-07-25)

**Agent Reach** (`https://github.com/Panniantong/Agent-Reach`) replaces browser automation for YouTube data extraction. One command installs `yt-dlp`, `opencli`, `bili`, `gh`, `feedparser`, etc.

### What it unlocks for YouTube research
| Capability | Command | Notes |
|------------|---------|-------|
| Search videos | `yt-dlp "ytsearch10:QUERY" --dump-json` | Returns title, views, channel, duration, ID, description |
| Extract subtitles | `yt-dlp --write-auto-subs --sub-langs en,ru --skip-download URL` | Auto-generated + manual subs |
| Get video metadata | `yt-dlp --dump-json URL` | Full JSON with chapters, thumbnails, heatmap |
| Extract description links | `yt-dlp --print description URL` | Clean text, no redirect tracking |

### Why Agent Reach > BrowserClaw for YouTube
- **Speed**: 5-10x faster than browser navigation
- **Reliability**: No cookie walls, no bot detection, no dynamic loading waits
- **Scriptable**: Full CLI + JSON output, easy to pipe to other tools
- **Batch**: Search 50 videos, extract all subtitles, one command
- **No headless browser overhead**: Runs as CLI, minimal resources

### Installation (for agent)
```bash
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto
# YouTube channel is zero-config (no auth needed)
```

### Usage pattern for autonomous YouTube research
```python
# 1. Search multiple queries in parallel
import subprocess, json

queries = [
    "faceless YouTube automation AI 2024",
    "Telegram bot CPA affiliate marketing 2024",
    "AI content repurposing long form to short form 2024",
    "create and sell digital products with AI 2024 no budget",
    "free traffic methods 2024 YouTube TikTok Pinterest no face",
    "affiliate marketing without followers website 2024",
    "micro saas build with AI agents 2024",
    "AI automation agency 2024 step by step",
    "ChatGPT business strategy faceless income 2026 real case study"
]

all_results = []
for q in queries:
    cmd = ['yt-dlp', f'ytsearch3:{q}', '--dump-json']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    for line in result.stdout.strip().split('\n'):
        if line:
            all_results.append(json.loads(line))

# 2. For each video: extract subtitles + description + links
for v in all_results:
    vid = v['id']
    # Subtitles
    subprocess.run(['yt-dlp', '--write-auto-subs', '--sub-langs', 'en,ru', 
                   '--skip-download', f'https://youtu.be/{vid}'], timeout=120)
    # Description + links
    desc = subprocess.run(['yt-dlp', '--print', 'description', f'https://youtu.be/{vid}'],
                          capture_output=True, text=True, timeout=30).stdout
    
# 3. Parse for: method steps, tools, costs, restricted_ok
# 4. Save to KC / research report
```

### Key insight
**Agent Reach replaces browser automation for DATA EXTRACTION.** Use `browser_navigate` only when you need to INTERACT (click, fill forms, handle JS-heavy auth flows).

## Subagent Timeout Pattern — YouTube Research (2026-07-25)

**Problem:** 9-query YouTube research via subagent timed out at 600s (10 min). BrowserClaw navigation + extraction is slow.

**Solution:** 
- Use Agent Reach (yt-dlp) instead of BrowserClaw for extraction — 5-10x faster
- If using subagents, split into 3 subagents × 3 queries each (parallel)
- Set explicit timeout per query (60s search, 120s subtitles)
- Don't ask subagent to wait for GitHub Pages deploy (1-3 min) — delegate push only, verify manually

**Pattern:**
```python
# Instead of 1 subagent × 9 queries × browser (timeout)
# Use 3 subagents × 3 queries × yt-dlp (completes in ~2 min)
```

## Technique: Curl + v2rayN Proxy — YouTube Extraction Fallback

When all browser-based approaches fail (YouTube blocked, timeout, 403, or BrowserClaw unavailable), extract video metadata via direct HTTP through the v2rayN SOCKS5 proxy.

### Single video extraction

```bash
curl -sL --max-time 15 --proxy socks5://127.0.0.1:10806 \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "https://www.youtube.com/watch?v=VIDEO_ID" \
  | python -c "
import sys, re
html = sys.stdin.read()
m = re.search(r'title\":\"([^\"]+)\"', html)
if m: print('TITLE:', m.group(1))
m = re.search(r'shortDescription\":\"([^\"]+)\"', html)
if m: print('DESC:', m.group(1)[:500])
m = re.search(r'\"author\":\"([^\"]+)\"', html)
if m: print('CHANNEL:', m.group(1))
m = re.search(r'\"viewCount\":\"([^\"]+)\"', html)
if m: print('VIEWS:', m.group(1))
"
```

Returns: title, description (first 500 chars), channel name, view count.

### oembed (quick metadata, no description)

```bash
curl -sL --proxy socks5://127.0.0.1:10806 \
  "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=VIDEO_ID&format=json"
```

### When to use

- Hermes browser tools timeout on YouTube
- web_extract returns HTTP 403
- BrowserClaw not available or also fails
- Quick check of what a video is about

## Technique: Agent Reach — Agent Internet Access (NEW 2026-07-25)

**Agent Reach** (`https://github.com/Panniantong/Agent-Reach`) replaces browser automation for YouTube data extraction. One command installs `yt-dlp`, `opencli`, `bili`, `gh`, `feedparser`, etc.

### What it unlocks for YouTube research
| Capability | Command | Notes |
|------------|---------|-------|
| Search videos | `yt-dlp "ytsearch10:QUERY" --dump-json` | Returns title, views, channel, duration, ID, description |
| Extract subtitles | `yt-dlp --write-auto-subs --sub-langs en,ru --skip-download URL` | Auto-generated + manual subs |
| Get video metadata | `yt-dlp --dump-json URL` | Full JSON with chapters, thumbnails, heatmap |
| Extract description links | `yt-dlp --print description URL` | Clean text, no redirect tracking |

### Why Agent Reach > BrowserClaw for YouTube
- **Speed**: 5-10x faster than browser navigation
- **Reliability**: No cookie walls, no bot detection, no dynamic loading waits
- **Scriptable**: Full CLI + JSON output, easy to pipe to other tools
- **Batch**: Search 50 videos, extract all subtitles, one command
- **No headless browser overhead**: Runs as CLI, minimal resources

### Installation (for agent)
```bash
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto
# YouTube channel is zero-config (no auth needed)
```

### Usage pattern for autonomous YouTube research
```python
# 1. Search multiple queries in parallel
import subprocess, json

queries = [
    "faceless YouTube automation AI 2024",
    "Telegram bot CPA affiliate marketing 2024",
    "AI content repurposing long form to short form 2024",
    "create and sell digital products with AI 2024 no budget",
    "free traffic methods 2024 YouTube TikTok Pinterest no face",
    "affiliate marketing without followers website 2024",
    "micro saas build with AI agents 2024",
    "AI automation agency 2024 step by step",
    "ChatGPT business strategy faceless income 2026 real case study"
]

all_results = []
for q in queries:
    cmd = ['yt-dlp', f'ytsearch3:{q}', '--dump-json']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    for line in result.stdout.strip().split('\n'):
        if line:
            all_results.append(json.loads(line))

# 2. For each video: extract subtitles + description + links
for v in all_results:
    vid = v['id']
    # Subtitles
    subprocess.run(['yt-dlp', '--write-auto-subs', '--sub-langs', 'en,ru', 
                   '--skip-download', f'https://youtu.be/{vid}'], timeout=120)
    # Description + links
    desc = subprocess.run(['yt-dlp', '--print', 'description', f'https://youtu.be/{vid}'],
                          capture_output=True, text=True, timeout=30).stdout
    
# 3. Parse for: method steps, tools, costs, restricted_ok
# 4. Save to KC / research report
```

### Key insight
**Agent Reach replaces browser automation for DATA EXTRACTION.** Use `browser_navigate` only when you need to INTERACT (click, fill forms, handle JS-heavy auth flows).

## Subagent Timeout Pattern — YouTube Research (2026-07-25)

**Problem:** 9-query YouTube research via subagent timed out at 600s (10 min). BrowserClaw is slow on YouTube.

**Solution:** Use Agent Reach `yt-dlp` (seconds per video) instead of BrowserClaw (minutes per video).

```python
# OLD (browser-based, timed out)
# 9 queries × 3 videos = 27 browser navigations + waits + extraction = 600s+

# NEW (Agent Reach, ~60s total)
import subprocess, json
queries = [...]  # 9 queries
for q in queries:
    result = subprocess.run(
        ['yt-dlp', f'ytsearch3:{q}', '--dump-json', 
         '--print', 'id,title,channel,view_count,description,url'],
        capture_output=True, text=True, timeout=60
    )
    for line in result.stdout.strip().split('\n'):
        if line:
            all_results.append(json.loads(line))

# Then batch extract subtitles for top videos
for v in top_videos:
    subprocess.run(['yt-dlp', '--write-auto-subs', '--sub-langs', 'en,ru',
                   '--skip-download', f'https://youtu.be/{v["id"]}'], timeout=120)
```

**Rule:** For YouTube research >5 queries, always use `yt-dlp` via Agent Reach. BrowserClaw reserved for: video page interaction (comments, chapters), visual analysis, auth-required content.

## Structured Research Output — JSON Schema (2026-07-25)

When user requests structured extraction from YouTube videos, output this JSON:

```json
{
  "query": "faceless YouTube automation AI 2024",
  "results": [
    {
      "title": "I Asked ChatGPT to Build Me a $100K Faceless Online Business",
      "url": "https://www.youtube.com/watch?v=ADUs92AXqqQ",
      "channel": "Smart Money Tactics",
      "views": 12000,
      "method_summary": "Faceless Instagram → Reels (content vault) → Stan Store digital products + affiliate → email list via lead magnet",
      "tools": ["Canva", "Stan Store", "Instagram Reels", "Content Vault (paid)"],
      "cost": "$50-100 for content vault, Stan Store free tier",
      "restricted_ok": true,
      "key_steps": [
        "Pick profitable niche via ChatGPT",
        "Buy content vault or AI-generate Reels",
        "Batch create 30 days content in Canva",
        "Post 2-3x/day with schedule",
        "Create free lead magnet (PDF)",
        "Build Stan Store with product ladder",
        "Promote affiliate + own digital products"
      ],
      "mistakes_to_avoid": ["Trying to sell 'AI' instead of solving problem", "Complex niches", "Not automating delivery"]
    }
  ]
}
```

Fields: `method_summary` (2-3 sentences, the WORKFLOW), `tools` (array), `cost` (string with $), `restricted_ok` (boolean - works from Crimea/blocked regions), `key_steps` (array of specific actions), `mistakes_to_avoid` (array).

## Related Skills

- `media/youtube-content` — YouTube transcripts → summaries, threads, blogs
- `media/youtube-transcript` — transcript extraction via youtube-transcript-api
- `self-improvement/web-knowledge-enrichment` — event-driven web enrichment

## Reference Files

- `references/chris-koerner-format.md` — Deep analysis of Chris Koerner's presentation format, funnel structure, and two-level value extraction model
- `scripts/youtube_pipeline.py` — Unified fallback chain: oembed → curl+proxy+HTML → yt-dlp+rescue → faster-whisper
- `references/youtube_pipeline.md` — Detailed documentation of the unified fallback chain, Windows proxy config, player client rotation, and integration patterns
