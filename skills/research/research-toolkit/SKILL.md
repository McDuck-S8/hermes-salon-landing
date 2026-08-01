---
name: research-toolkit
description: "Unified research toolkit for Hermes: arxiv + blogwatcher + llm-wiki + polymarket + notebooklm-py + lavra-patterns + research-paper-writing. One skill to load, 7 engines at hand."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [research, arxiv, blogwatcher, llm-wiki, polymarket, notebooklm, lavra, papers]
    related_skills: [arxiv, blogwatcher, llm-wiki, polymarket, notebooklm-py, lavra-patterns, research-paper-writing, trend-scout, trendshift-monitor]
  skill_updated: "2026-07-24"
  created_by: "auto_patch_g007"
  component_skills:
    - arxiv
    - blogwatcher
    - llm-wiki
    - polymarket
    - notebooklm-py
    - lavra-patterns
    - research-paper-writing
---

# Research Toolkit — Unified Interface

**One skill to load. 7 research engines. Zero context switching.**

This meta-skill wraps all core research skills into a single loadable unit with a unified workflow interface.

## Quick Start

```python
# Load once, get all 7 tools
from hermes_tools import skill_view
skill_view("research/research-toolkit")

# Now you have:
# - arxiv (search arXiv papers by keyword, author, category)
# - blogwatcher (RSS/Atom feed monitoring via blogwatcher-cli)
# - llm-wiki (Karpathy's LLM Wiki: interlinked markdown KB)
# - polymarket (query Polymarket: markets, prices, orderbooks)
# - notebooklm-py (Google NotebookLM unofficial Python API)
# - lavra-patterns (Lavra/OpenClaude patterns for skills/KC/multi-agent)
# - research-paper-writing (academic paper structure + LaTeX/MD export)
```

## Component Skills Map

| Skill | Purpose | Best For |
|-------|---------|----------|
| **arxiv** | Search arXiv papers by keyword, author, category, ID | Academic literature, ML/AI papers, citations |
| **blogwatcher** | Monitor RSS/Atom feeds (CPA, AI, tech blogs) | Trend scouting, competitor intelligence |
| **llm-wiki** | Build/query interlinked markdown knowledge base | Personal wiki, concept maps, retrieval |
| **polymarket** | Query prediction markets: prices, orderbooks, history | Signal extraction, probability calibration |
| **notebooklm-py** | Unofficial NotebookLM API: sources, queries, audio | Document synthesis, podcast generation |
| **lavra-patterns** | Lavra/OpenClaude patterns: skills, KC, multi-agent | Skill creation, knowledge capture, orchestration |
| **research-paper-writing** | Academic paper structure, LaTeX/MD export | Formal reports, whitepapers, submissions |

## Unified Research Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. DISCOVER (arxiv + blogwatcher + polymarket)                  │
│    • arxiv: "transformer efficiency" → 50 papers                │
│    • blogwatcher: CPA/AI feeds → new posts daily                │
│    • polymarket: "AI regulation 2026" → probability signals     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. ORGANIZE (llm-wiki + notebooklm-py)                          │
│    • llm-wiki: Create interlinked nodes for concepts            │
│    • notebooklm-py: Upload PDFs → query + generate podcast      │
│    • Tag: #domain #priority #status                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. EXTRACT PATTERNS (lavra-patterns)                            │
│    • Skill creation patterns                                    │
│    • Knowledge Cube capture patterns                            │
│    • Multi-agent orchestration patterns                         │
│    • Self-improvement loop patterns                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. SYNTHESIZE (research-paper-writing)                          │
│    • Structure: Abstract → Intro → Method → Results → Discussion│
│    • Export: LaTeX (arXiv), Markdown (Obsidian), PDF            │
│    • Citations: BibTeX from arxiv + manual                      │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Commands Reference

### arXiv Search
```python
# Search by keyword
arxiv_search("transformer attention mechanism", max_results=20)

# By author
arxiv_search("author:vaswani", max_results=10)

# By category
arxiv_search("cat:cs.LG", max_results=30)

# Specific paper
arxiv_search("2301.08727")  # arXiv ID
```

### Blogwatcher (RSS Monitoring)
```bash
# Add feeds
blogwatcher add "https://blog.openai.com/rss.xml" --tags ai,research
blogwatcher add "https://partnerkin.com/feed/" --tags cpa,arbitrage

# Fetch new
blogwatcher fetch --since 24h

# Export for processing
blogwatcher export --format json --output new_posts.json
```

### LLM Wiki (Personal Knowledge Base)
```bash
# Create wiki
llm-wiki init ~/my-wiki

# Add linked notes
llm-wiki add "Transformer Architecture" --links "Attention,Embedding,Positional Encoding"

# Query
llm-wiki query "How does attention work?"

# Export graph
llm-wiki export --format graphml
```

### Polymarket (Prediction Markets)
```python
# Query markets
polymarket_markets(query="AI", limit=10)

# Get prices
polymarket_prices("0x1234...", interval="1h")

# Orderbook depth
polymarket_orderbook("0x1234...")
```

### NotebookLM (Document Synthesis)
```python
# Upload sources
notebooklm.upload_sources(["paper1.pdf", "paper2.pdf"])

# Query
notebooklm.query("What are the key findings across sources?")

# Generate podcast
notebooklm.generate_audio("podcast", duration=120)
```

### Lavra Patterns (Skill/KC/Multi-agent)
```markdown
# Key pattern categories:
- skill-creation: SKILL.md format, validation, testing
- knowledge-capture: on_task_complete, on_error, on_user_correction
- multi-agent: delegate_task, advisor-orchestrator-worker, subagent-driven-development
- self-improvement: suggestion generation, evaluation, patching
```

### Research Paper Writing
```python
# Structure
paper = ResearchPaper(
    title="Efficient Transformers for CPA Optimization",
    authors=["Hermes Agent"],
    abstract="...",
    sections=[
        Section("Introduction", "..."),
        Section("Related Work", "..."),
        Section("Methodology", "..."),
        Section("Experiments", "..."),
        Section("Conclusion", "...")
    ]
)

# Export
paper.to_latex("paper.tex")
paper.to_markdown("paper.md")
paper.to_bibtex("refs.bib")
```

## Integration with Knowledge Cube

```python
from scripts.event_evolution import on_task_complete

on_task_complete(
    content="Research complete: arxiv (15 papers) → llm-wiki (12 nodes) → polymarket (3 signals) → research-paper-writing (draft v0.1). Topic: transformer efficiency for real-time bidding.",
    tags=["research", "arxiv", "llm-wiki", "polymarket", "paper", "success"],
    source="agent"
)
```

## Anti-Patterns (from 125 research entries, 36 failures = 29% failure rate)

| Anti-Pattern | Guard |
|--------------|-------|
| Papers collected, never read | **notebooklm-py**: force synthesis via query/audio |
| RSS feeds unchecked for weeks | **blogwatcher**: cron fetch + alert on new |
| Concepts isolated, not linked | **llm-wiki**: mandatory interlinking on add |
| Market signals ignored | **polymarket**: weekly probability calibration |
| Patterns not captured | **lavra-patterns**: mandatory after each project |
| Drafts never finalized | **research-paper-writing**: structure → export pipeline |

## Search Engine Fallback Chain

When the default web_search provider fails, use this fallback sequence:

| Failure | Fallback | Notes |
|---------|----------|-------|
| `web_search()` returns 432 (Tavily) | Try `web_extract_plus(provider="parallel")` or `web_extract_plus(provider="you")` | Parallel provider auto-routes through multiple backends |
| `web_extract()` returns 432 (Tavily) | Try `web_extract_plus(provider="firecrawl")` or `web_extract_plus(provider="linkup")` | These use different extraction engines |
| All search providers down | Use `browser_navigate()` for known URLs | Reserve for extracting specific pages, not discovery |
| Browser not available | Check local cache files first before attempting external calls | Offers, costs, and trends may be cached in `cache/` |

**Pattern discovered 2026-07-25:** When all search providers fail (Tavily 432, Brave silent error), `web_extract_plus(provider="parallel")` still routed through `you` provider and returned Binance affiliate page content. Keep this as a last-resort extraction method.

## Agent Reach — Agent Internet Access (NEW 2026-07-25)

**Agent Reach** (`https://github.com/Panniantong/Agent-Reach`) gives AI agents CLI access to the internet. One command installs all upstream tools.

### What it unlocks
| Platform | Upstream Tool | Capability |
|----------|---------------|------------|
| YouTube | `yt-dlp` | Subtitles, search, metadata |
| Twitter/X | `twitter` / `opencli` | Search tweets, timeline, long-form (needs Cookie) |
| GitHub | `gh` | Read repos, search, issues, PRs (needs auth for private) |
| Reddit | `opencli` / `rdt` | Search, read posts/comments (needs Cookie) |
| Bilibili | `bili` / `opencli` | Search, video details, subtitles |
| RSS/Atom | `feedparser` | Read any feed |
| Web | `curl` + Jina AI | Read any URL via `r.jina.ai/http://<url>` |
| Exa Search | `mcporter` | Semantic web search (free, no key) |
| 小红书 | `opencli` / `xiaohongshu-mcp` | Search, read (needs Chrome session/Cookie) |
| Facebook/Instagram | `opencli` | Search, profiles, groups (needs Chrome session) |
| 小宇宙播客 | `xiaoyuzhou` + Groq Whisper | Audio → transcript (free Groq key) |
| LinkedIn | `linkedin-scraper-mcp` | Profiles, jobs, companies (needs browser login) |
| V2EX | built-in | Hot posts, nodes, users |
| 雪球 | built-in | Stock quotes, posts |

### Installation (for agent)
```bash
# Auto-detect environment, install core + zero-config channels
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto

# Optional channels (ask user which they need)
agent-reach install --env=auto --channels=twitter,xiaohongshu
agent-reach install --env=auto --channels=opencli  # desktop: Reddit/FB/IG/B站字幕
```

### Usage pattern for autonomous research
```python
# 1. Search YouTube for method videos
yt-dlp "ytsearch5:faceless YouTube automation AI 2024" --dump-json

# 2. Extract transcripts
yt-dlp --write-auto-subs --sub-langs en --skip-download URL

# 3. Read GitHub repos for skills/tools
gh api repos/Panniantong/Agent-Reach/contents

# 4. Search Reddit for case studies
opencli reddit search "CPA arbitrage case study 2024" -f yaml

# 5. Monitor RSS feeds for new opportunities
python -c "import feedparser; f=feedparser.parse('https://partnerkin.com/feed/'); print(f.entries[0].title)"
```

### Key insight
**Agent Reach replaces browser automation for data extraction.** It's faster, cheaper, and scriptable. Use `browser_navigate` only when you need to interact (click, fill forms, handle JS-heavy auth flows).

### Integration with Hermes
- Add as a plugin/skill: `skills/agent-reach/` with wrapper scripts
- Event-driven: `event_sense.py` can emit `new_youtube_video`, `new_github_release`, `new_reddit_post` via Agent Reach polling
- Research workflow: Agent Reach → extract → KC → crystal → action

## Verification Checklist

After using this toolkit:
- [ ] arxiv: relevant papers retrieved & tagged
- [ ] blogwatcher: feeds fetched, new items processed
- [ ] llm-wiki: concepts linked, queryable
- [ ] polymarket: signals extracted, probabilities noted
- [ ] notebooklm-py: sources uploaded, synthesis done
- [ ] lavra-patterns: patterns documented for reuse
- [ ] research-paper-writing: draft structured + exported
- [ ] KC entry created with all tags

---

**Origin:** g-007 Unlock: research (125 entries, 36 failures, 13 successes)
**Created:** 2026-07-24 via auto_patch_g007
**Source:** Knowledge Cube domain `research` + all 7 component skills