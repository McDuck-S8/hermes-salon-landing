---
name: agent-reach
description: |
  Capability layer giving Hermes Agent internet access: YouTube transcripts, web search/read, GitHub, Twitter/X, Reddit, Bilibili, RSS, Exa semantic search. Auto-updates backends when platforms change.
version: 1.0.0
category: autonomous-ai-agents
tags:
  - web-access
  - youtube
  - search
  - github
  - social-media
  - rss
  - capability-layer
---

# Agent Reach — Internet Capability Layer for Hermes

## Purpose

Agent Reach is a **capability layer** (not a tool wrapper) that gives Hermes Agent reliable, auto-maintained access to the internet. It handles:
- Tool selection/installation/update for each platform
- Backend routing with fallbacks (when YouTube blocks yt-dlp, switches to bili-cli)
- Authentication management (cookies, tokens, browser sessions)
- Health checks (`agent-reach doctor`)

After installation, Hermes can directly use upstream tools: `yt-dlp`, `gh`, `twitter`, `opencli`, `mcporter`, `bili`, `rdt`, `feedparser`.

## Supported Platforms

| Platform | Zero-config | Needs Auth | Backend Chain |
|----------|-------------|------------|---------------|
| Web (read any URL) | ✅ | — | Jina Reader |
| YouTube (subtitles + search) | ✅ | — | yt-dlp |
| GitHub (repos, issues, search) | ✅ (public) | Private repos | gh CLI |
| RSS/Atom feeds | ✅ | — | feedparser |
| Exa semantic search | — | Auto (MCP) | mcporter → Exa |
| V2EX | ✅ | — | Native |
| Bilibili | ✅ (search/details) | Subtitles | bili-cli → OpenCLI |
| Twitter/X | Single tweet | Search/timeline | twitter-cli → OpenCLI |
| Reddit | — | Search/read | OpenCLI (desktop) / rdt-cli |
| Facebook | — | Search/pages/groups | OpenCLI (Chrome session) |
| Instagram | — | User search/posts | OpenCLI (Chrome session) |
| 小红书 | — | Search/read | OpenCLI (Chrome session) / xiaohongshu-mcp |
| LinkedIn | Jina Reader (public) | Profile/jobs | linkedin-scraper-mcp |
| 小宇宙播客 | — | Transcription | Groq Whisper (free) |

## Installation

```bash
# One-liner for Hermes Agent
hermes skills install agent-reach

# Or manual (if hermes CLI doesn't have the skill yet)
git clone https://github.com/Panniantong/Agent-Reach ~/.hermes/skills/agent-reach
cd ~/.hermes/skills/agent-reach
pip install -e .
agent-reach install --env=auto
```

## Usage from Hermes

Once installed, Agent Reach registers a skill that Hermes can load. In your prompts:

```
# Search YouTube
"Find top 3 videos on 'faceless YouTube automation AI 2024' and extract their methods"

# Read a webpage
"Read https://github.com/Panniantong/Agent-Reach and summarize the architecture"

# Search web
"Search for 'CPA arbitrage case study 2024 real numbers' using Exa"

# GitHub repo analysis
"Analyze https://github.com/witt3rd/oh-my-hermes for skill patterns"
```

The skill teaches Hermes which upstream tool to call for each capability.

### Programmatic Usage (Crystal Integration)

For autonomous use in Crystal loops, use the convenience functions in `scripts/crystal/omh_integration.py`:

```python
from scripts.crystal.omh_integration import (
    crystal_web_search,
    crystal_youtube_search,
    crystal_youtube_transcript,
    crystal_github_search,
    crystal_web_read,
    crystal_rss_fetch,
)

# YouTube research
videos = crystal_youtube_search("faceless YouTube automation AI 2024", max_results=5)
for v in videos:
    transcript = crystal_youtube_transcript(v["url"])
    # Feed to Knowledge Cube

# Web research
results = crystal_web_search("CPA arbitrage case study 2024 real numbers", max_results=10)

# GitHub research
repos = crystal_github_search("AI agent framework", limit=5)

# Webpage reading
content = crystal_web_read("https://github.com/Panniantong/Agent-Reach")
```

### Pipeline Integration (Chain Heartbeat)

Agent Reach channels are registered as heartbeat modules:

```python
from scripts.chain_heartbeat import beat

# In research pipeline
beat("agent_reach_youtube")
beat("agent_reach_web")
beat("agent_reach_github")
beat("agent_reach_rss")
```

## Upstream Tools (Direct Calls)

After `agent-reach install`, these are available in shell:

```bash
# YouTube
yt-dlp --dump-json "https://youtube.com/watch?v=..."
yt-dlp "ytsearch5:query" --flat-playlist --print "%(title)s|%(url)s|%(channel)s|%(view_count)s"

# Web
curl -s "https://r.jina.ai/https://example.com"

# GitHub
gh repo view owner/repo --json description,stargazerCount
gh search repos "query" --limit 5 --json name,description,url

# Exa Search (via mcporter)
mcporter call 'exa.web_search_exa({"query": "...", "max_results": 10})'

# RSS
python3 -c "import feedparser; f=feedparser.parse('URL'); print(f.entries[0].summary)"

# Twitter (needs TWITTER_AUTH_TOKEN, TWITTER_CT0 env vars)
twitter search "query" -n 10

# Bilibili
bili search "query" --type video
opencli bilibili subtitle BVxxx

# Reddit (needs OpenCLI with Chrome logged in)
opencli reddit search "query" -f yaml
```

## Configuration

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `TWITTER_AUTH_TOKEN`, `TWITTER_CT0` | Twitter API cookies |
| `GROQ_API_KEY` | 小宇宙 podcast transcription (free at console.groq.com) |
| `HTTP_PROXY` / `HTTPS_PROXY` | For restricted networks (e.g., `socks5://127.0.0.1:10806`) |

### Cookie Management

```bash
# Twitter
agent-reach configure twitter-cookies "auth_token=xxx; ct0=yyy"

# 小红书
agent-reach configure xhs-cookies "a1=xxx; web_session=yyy"

# Snowball (雪球)
agent-reach configure --from-browser chrome --platform xueqiu
```

## Health Check

```bash
agent-reach doctor
# Shows each channel status, active backend, latency

agent-reach watch
# Silent if healthy, reports issues + update suggestions
```

Add to cron for daily monitoring:
```bash
# Daily at 6 AM
0 6 * * * agent-reach watch
```

## Integration with Hermes Architecture

### Crystal Research Phase
```python
# In crystal/research.py or similar
from hermes_web_access import HermesWebAccess
web = HermesWebAccess()
videos = web.youtube_search("faceless YouTube automation 2024", max_results=5)
for v in videos:
    transcript = web.youtube_transcript(v["url"])
    # Feed to Knowledge Cube
```

### Autonomous Loop (Chain Heartbeat)
```python
# In autonomous_agent.py or proactive_executor.py
from agent_reach_integration import AgentReach
reach = AgentReach()

# Daily research trigger
if event == "new_suggestions_ready" or days_since_last_research > 1:
    results = reach.youtube_search("CPA arbitrage case study 2024", max=3)
    for r in results:
        transcript = reach.youtube_transcript(r["url"])
        # Process, extract patterns, write to KC
```

### Self-Improvement Pipeline
```python
# In self_improvement_loop.py
# When generating suggestions, use live web data
suggestions = reach.web_search("Hermes Agent autonomous AI latest patterns 2024")
# Feed into suggestion generation
```

## Network Constraints

All external HTTPS requests on this machine must go through SOCKS5 proxy at `127.0.0.1:10806`. See `references/network-constraints.md` for per-tool configuration.

## References

- [Agent Reach GitHub](https://github.com/Panniantong/Agent-Reach)
- [Installation Guide](https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md)
- [Update Guide](https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md)
- [Oh My Hermes](https://github.com/witt3rd/oh-my-hermes) — complementary multi-agent skills

## Quick Reference Card

| Task | Command Pattern |
|------|-----------------|
| YouTube search | `yt-dlp "ytsearchN:query" --flat-playlist --print "%(title)s|%(url)s|%(channel)s|%(view_count)s"` |
| YouTube transcript | `yt-dlp --write-auto-subs --sub-langs en,ru --skip-download --print description URL` |
| Web read | `curl -s "https://r.jina.ai/URL"` |
| GitHub search | `gh search repos "query" --limit N --json name,description,url` |
| Exa search | `mcporter call 'exa.web_search_exa({"query": "..."})'` |
| RSS fetch | `curl -s "RSS_URL" | feedparser` |
| Twitter search | `export TWITTER_AUTH_TOKEN=... TWITTER_CT0=... && twitter search "query" -n 10` |
| Bilibili search | `bili search "query" --type video` |
| Podcast transcribe | `bash ~/.agent-reach/tools/xiaoyuzhou/transcribe.sh URL` (needs GROQ_API_KEY) |