---
name: hermes-web-access
description: |
  Web access tools for Hermes autonomous research via Agent Reach capability layer.
  Provides YouTube search/transcript, web search/read, GitHub read, RSS fetch.
  Uses Agent Reach capability layer for backend auto-routing and health checks.
version: 1.0.0
category: integration
tags:
  - web-access
  - youtube
  - search
  - github
  - rss
  - agent-reach
---

# Hermes Web Access

## Purpose

Web access tools for Hermes autonomous research via Agent Reach capability layer.
Provides: YouTube search/transcript, web search/read, GitHub read, RSS fetch.
Uses Agent Reach capability layer for backend auto-routing and health checks.

## Integration

### As Crystal Module

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

### As Standalone Module

```python
from scripts.hermes_web_access import HermesWebAccess

hwa = HermesWebAccess()

# YouTube
videos = hwa.youtube_search("faceless YouTube automation AI 2024", max_results=5)
transcript = hwa.youtube_transcript("https://youtube.com/watch?v=...")

# Web
results = hwa.web_search("CPA arbitrage case study 2024", max_results=10)
content = hwa.web_read("https://github.com/Panniantong/Agent-Reach")

# GitHub
repos = hwa.github_search("AI agent framework", limit=5)

# RSS
entries = hwa.rss_fetch("https://github.com/trending/python?feed=atom")
```

## Backend Tools (Auto-Routed by Agent Reach)

| Capability | Primary Tool | Fallback |
|------------|-------------|----------|
| YouTube Search/Transcript | yt-dlp | — |
| Web Search | Exa (mcporter) | DuckDuckGo API |
| Web Read | Jina AI Reader (r.jina.ai) | — |
| GitHub | gh CLI | — |
| RSS | feedparser | — |

## Proxy Configuration

All external requests use SOCKS5 proxy at `socks5://127.0.0.1:10806`.
See `scripts/hermes_web_access.py` for implementation.

## Health Check

## Network Constraints

All external HTTPS requests on this machine must go through SOCKS5 proxy at `127.0.0.1:10806`. See `references/network-constraints.md` for per-tool configuration.

```python
from scripts.crystal.omh_integration import ensure_agent_reach
ensure_agent_reach()  # Installs and verifies Agent Reach
```