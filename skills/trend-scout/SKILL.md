---
name: trend-scout
description: Search web for emerging trends, evaluate repos, and integrate useful tools for Hermes.
category: research
---

# Trend Scout — Proactive Research & Repo Evaluation

## Trigger Conditions (comprehensive, 2026-07-22)
- User asks about trends, trending topics, what's hot in AI
- Need content ideas for Telegram channels
- **AFTER system revival** — alerts → 0, all modules healthy. Run immediately.
- **User provides repos list** — evaluate ALL, install top 2-3, record in KC. Do NOT just report — integrate.
- Periodic autonomous scan (cron)

## GitHub Trending Pattern
When user says "сходи прогуляйся в инет" or "что нового":

### 1. Fetch trending
curl -s "https://github.com/trending" | grep -oP 'href="/[^"]+/[^"]*"'

### 2. ACTION after exploration (CRITICAL):
- INSTALL the most promising repo (npm/pip/curl)
- TEST with our data
- REPORT what you FOUND + what you BUILT

## 10-Repo Parallel Evaluation Protocol (2026-07-22)

When user provides repos or when research finds multiple candidates:

### Step 1: Batch fetch all READMEs
### Step 2: Extract key data per repo
Stars, language, license, MCP/SKILL support, already integrated?

### Step 3: Install/integrate top 2-3 immediately
### Step 4: Record ALL evaluations in Knowledge Cube
### Step 5: Report — ✅ installed, 🟡 deferred, ❌ rejected

### Pitfalls
- Do NOT just read and report — install the top candidates
- Do NOT skip niche repos (OfficeCLI with 20.5k replaced excel-author)
- Always check: already a Hermes skill? (hallmark, codex exist)

## Critical: Recording Destination
ALWAYS write to ARBITRAGE_WORKSHOP.md FIRST, then hooks.

## Technique: Agent Reach — Unified Internet Access for Trend Scouting (2026-07-25)

**Agent Reach** (`https://github.com/Panniantong/Agent-Reach`) provides a single capability layer for all internet access needs during trend scouting.

### What it unlocks for trend research
| Platform | Capability | Command |
|----------|------------|---------|
| GitHub | Search repos, read files, issues | `gh search repos "query" --limit 10 --json name,description,stargazerCount,url` |
| YouTube | Search trending content, extract methods | `yt-dlp "ytsearch10:AI automation 2024" --dump-json` |
| Twitter/X | Real-time trend detection | `twitter search "AI agents 2024" -n 20` (needs auth) |
| Reddit | Community sentiment, early signals | `opencli reddit search "AI agents" -f yaml` (needs auth) |
| Bilibili | Chinese tech trends | `bili search "AI agent" --type video` |
| Exa Search | Semantic web search | `mcporter call 'exa.web_search_exa({"query": "AI agent trends 2024", "max_results": 10})'` |
| RSS/News | Aggregator monitoring | `feedparser.parse("https://news.ycombinator.com/rss")` |
| GitHub Trending | Daily pulse | `curl -s "https://github.com/trending" \| grep -oP 'href=\"/[^\"]+/[^\"]*"'` |

### Why Agent Reach > Manual curl/browser for trend scouting
- **Unified interface**: One install → all channels work
- **Auto-updating backends**: When GitHub API changes, Agent Reach updates its `gh` CLI usage
- **Zero-config for public sources**: GitHub, YouTube, RSS, V2EX work immediately
- **Auth management**: Secure cookie/token storage for private sources
- **Health checks**: `agent-reach doctor` tells you what's working

### Installation (once per environment)
```bash
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto
```

### Autonomous daily trend scan pattern
```python
# cron: 0 6 * * *  (daily 6 AM)
import subprocess, json, feedparser
from datetime import datetime

results = {}

# 1. GitHub Trending
results['github_trending'] = subprocess.run(
    ['curl', '-s', 'https://github.com/trending'],
    capture_output=True, text=True, timeout=30
).stdout

# 2. YouTube AI trends
yt = subprocess.run(
    ['yt-dlp', 'ytsearch5:AI agents 2024', '--dump-json'],
    capture_output=True, text=True, timeout=60
)
results['youtube'] = [json.loads(l) for l in yt.stdout.strip().split('\n') if l]

# 3. Hacker News
rss = feedparser.parse('https://news.ycombinator.com/rss')
results['hackernews'] = [{'title': e.title, 'link': e.link} for e in rss.entries[:10]]

# 4. Exa semantic search
exa = subprocess.run(
    ['mcporter', 'call', 'exa.web_search_exa', json.dumps({"query": "emerging AI tools July 2024", "max_results": 10})],
    capture_output=True, text=True, timeout=30
)

# Save to KC / ARBITRAGE_WORKSHOP.md
```

## Technique: OMH Skills — Structured Multi-Agent Research (2026-07-25)

**Oh My Hermes** (`https://github.com/witt3rd/oh-my-hermes`) replaces ad-hoc subagent patterns with composable, verified skills.

### OMH Research Pipeline for Trend Scouting
```bash
# Install OMH skills (once)
hermes skills tap add witt3rd/oh-my-hermes
hermes skills install omh-deep-research omh-ralplan omh-ralph omh-autopilot
```

### OMH Skill Roles for Trend Research
| Skill | Role | When to Use |
|-------|------|-------------|
| `omh-deep-research` | Multi-phase web research: decompose → parallel search → synthesize → verify citations | Need comprehensive data on unfamiliar trend |
| `omh-deep-interview` | Socratic requirements interview with coverage tracking | Vague trend → structured research brief |
| `omh-ralplan` | Consensus planning: Planner → Architect → Critic debate until agreement | Need robust execution plan for trend integration |
| `omh-ralph` | Verified execution: implement → verify → iterate until done | Have plan, need reliable implementation |
| `omh-autopilot` | Full pipeline composing all three skills end-to-end | End-to-end unfamiliar trend project |

### Integration with Agent Reach
```python
# Instead of manual 10-repo evaluation:
# 1. Agent Reach fetches candidates (GitHub trending + Exa search)
# 2. omh-deep-research decomposes: "evaluate these 10 repos for Hermes integration"
# 3. Parallel researchers fetch READMEs, analyze MCP/SKILL support, license, stars
# 4. Synthesist produces comparison table
# 5. Verifier checks: already integrated? MCP support? License compatible?
# 6. omh-ralplan → integration plan for top 2-3
# 7. omh-ralph → execute integration

# Cost envelope: ~5-8 delegate_task calls (3-5 researchers + synthesist + verifier)
# With retry: up to ~10-12 calls. 3-strike cap bounds worst-case at ~14-16.
```

### 10-Repo Parallel Evaluation → OMH Upgrade
**OLD (manual):**
1. Fetch all READMEs
2. Extract key data per repo
3. Install/integrate top 2-3 immediately
4. Record ALL evaluations in Knowledge Cube
5. Report — ✅ installed, 🟡 deferred, ❌ rejected

**NEW (OMH):**
```python
# 1. Agent Reach gathers candidates
repos = agent_reach.github_trending() + agent_reach.exa_search("AI agent framework 2024")

# 2. omh-deep-research decomposes evaluation criteria
# 3. Parallel researchers (3-5) evaluate subsets
# 4. Synthesist produces comparison matrix
# 4. omh-ralplan → integration plan for top candidates
# 5. omh-ralph → executes integration
```

### Cost Envelope
- `omh-deep-research`: ~5-8 delegate_task calls (happy path)
- With one retry: up to ~10-12 calls
- 3-strike retry cap bounds worst-case at ~14-16 calls
- Each call is a subagent with full context — higher quality than manual

## Structured Trend Report — JSON Schema (2026-07-25)

When user requests structured trend analysis, output this JSON:

```json
{
  "scan_date": "2026-07-25",
  "sources": ["github_trending", "youtube_ai", "hackernews", "exa_search"],
  "trends": [
    {
      "title": "Multi-agent AI frameworks (LangGraph, CrewAI, AutoGen)",
      "category": "AI Infrastructure",
      "signal_strength": "high",
      "evidence": [
        {"source": "github_trending", "repo": "langchain-ai/langgraph", "stars": 8500, "growth": "+400/week"},
        {"source": "youtube", "video": "LangGraph vs CrewAI vs AutoGen", "views": 45000, "channel": "AI Jason"},
        {"source": "exa_search", "query": "production multi-agent systems 2024", "results": 12}
      ],
      "hermes_integration": "omh-autopilot uses similar patterns; consider adding LangGraph as orchestrator backend",
      "action": "✅ evaluate LangGraph as orchestrator replacement for crystal loops"
    }
  ],
  "repos_evaluated": [
    {"name": "langchain-ai/langgraph", "status": "✅ installed", "integration": "orchestrator backend"},
    {"name": "joaomdmoura/crewAI", "status": "🟡 deferred", "reason": "overlaps with omh-autopilot"},
    {"name": "microsoft/autogen", "status": "❌ rejected", "reason": "heavy, MS-ecosystem"}
  ],
  "next_scan": "2026-07-26"
}
```