---
name: crystal-capability-layer-integration
description: "Integrate external capability layers (Agent Reach, Oh My Hermes) into Crystal autonomous loop for internet access, multi-agent orchestration, and verified execution"
version: 1.0.0
category: autonomous-ai-agents
tags:
  - crystal
  - agent-reach
  - oh-my-hermes
  - capability-layer
  - autonomous-loop
  - web-access
  - multi-agent
---

# Crystal Capability Layer Integration

## Purpose

Connect Crystal's autonomous self-learning loop to external capability layers:
- **Agent Reach** — Internet access (YouTube, GitHub, Web, RSS, Exa, Twitter, Bilibili, Reddit)
- **Oh My Hermes (OMH)** — Multi-agent orchestration (deep research, consensus planning, verified execution, triage)

This skill documents the integration patterns so future sessions can wire capability layers into Crystal without rediscovering the plumbing.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Crystal Autonomous Loop                   │
│  Observe → Analyze → Context → Act → Monitor → Evolve       │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
            ┌───────────────┐   ┌───────────────┐
            │ Agent Reach   │   │ Oh My Hermes  │
            │ (Capability   │   │ (Multi-Agent  │
            │  Layer)       │   │  Skills)      │
            │               │   │               │
            │ • YouTube     │   │ • omh-deep-   │
            │ • GitHub      │   │   research    │
            │ • Web Search  │   │ • omh-ralplan │
            │ • RSS         │   │ • omh-ralph   │
            │ • Exa         │   │ • omh-autopilot│
            │ • Twitter/X   │   │ • omh-triage  │
            │ • Bilibili    │   │               │
            │ • Reddit      │   │               │
            └───────────────┘   └───────────────┘
```

## Integration Points

### 1. Crystal `intelligence.py` → Agent Reach

**File:** `scripts/crystal/intelligence.py`

The `IntelScanner.scan()` method now uses Agent Reach backends:

```python
# Before: DuckDuckGo HTML scrape (unreliable)
# After: Agent Reach backends with auto-failover

def _scan_youtube(self) -> list:
    videos = crystal_youtube_search(query, max_results=2)
    for v in videos:
        transcript = crystal_youtube_transcript(v["url"])
        items.append(IntelItem(source="youtube", ...))

def _scan_rss(self) -> list:
    for feed_url in rss_feeds:
        entries = crystal_rss_fetch(feed_url)
        items.append(IntelItem(source="rss", ...))

def _scan_github(self) -> list:
    results = crystal_github_search(query, limit=3)
    ...
```

**Key convenience functions** (in `scripts/crystal/omh_integration.py`):
```python
from scripts.crystal.omh_integration import (
    crystal_web_search,
    crystal_youtube_search,
    crystal_youtube_transcript,
    crystal_github_search,
    crystal_web_read,
    crystal_rss_fetch,
    ensure_agent_reach,
)
```

### 2. Crystal `core.py` → OMH Research Pipeline

**File:** `scripts/crystal/core.py` — `run_full_cycle()` extended with two new phases:

```python
# Phase 5b: Agent Reach Intelligence Scan (NEW)
print("\n[Faza 5b] Agent Reach Intelligence Scan")
intel_items = self.scan_intelligence()
print(f"   Found: {len(intel_items)} insights")

# Phase 6b: OMH Research Pipeline (NEW)
print("\n[Faza 6b] OMH Research Pipeline")
omh_results = self.run_omh_research()
print(f"   OMH cycles: {len(omh_results)}")
```

**New methods in `CrystalEngine`:**
```python
def scan_intelligence(self) -> list:
    """Run Agent Reach intelligence scan via IntelScanner."""
    from scripts.crystal.intelligence import IntelScanner
    scanner = IntelScanner()
    return scanner.scan()

def run_omh_research(self) -> list:
    """Run OMH deep research on high-priority needs."""
    from scripts.crystal.omh_integration import OMHIntegration
    omh = OMHIntegration()
    results = []
    for need in self.needs[:3]:  # Top 3 needs
        if omh.is_available("omh-deep-research"):
            results.append(omh.run_deep_research(need.description))
    return results
```

### 3. Chain Heartbeat → OMH + Agent Reach Pipelines

**File:** `scripts/chain_heartbeat.py` — Added Level 3 pipelines:

```python
PIPELINES = {
    # ... existing pipelines ...
    
    # OMH research pipeline
    "omh_research_pipeline": {
        "components": ["omh_deep_research", "omh_deep_interview", 
                       "omh_ralplan", "omh_ralph"],
        "description": "research → interview → plan → execute (autopilot)",
    },
    
    # Agent Reach intelligence pipeline
    "agent_reach_intel_pipeline": {
        "components": ["agent_reach_youtube", "agent_reach_web", 
                       "agent_reach_github", "agent_reach_rss"],
        "description": "YouTube → Web → GitHub → RSS → Knowledge Cube",
    },
}
```

**Level 2 modules** registered:
```python
MODULES = [
    # ... existing modules ...
    # OMH skills (Oh My Hermes)
    "omh_deep_research", "omh_ralplan", "omh_ralplan_driver",
    "omh_deep_interview", "omh_ralph", "omh_ralph_driver",
    "omh_ralph_task", "omh_autopilot", "omh_triage", "omh_triage_driver",
    # Agent Reach capability layer
    "agent_reach_youtube", "agent_reach_web", "agent_reach_github",
    "agent_reach_rss", "agent_reach_twitter", "agent_reach_bilibili",
]
```

### 4. Knowledge Cube → YouTube Research

**File:** `scripts/kc_rag.py` — `upsert()` fires `knowledge_added` event.

Used to store structured YouTube research findings:

```python
from scripts.kc_rag import upsert

upsert(
    content="Faceless YouTube Automation Method (Warren Stick - 30 days case study): "
            "AI scripts (ChatGPT) + ElevenLabs voiceover + InVideo editing. "
            "Result: realistic numbers, not '100k/month' fantasy. "
            "Key insight: consistency > quality, need 100+ videos for traction. "
            "Tools: ChatGPT, ElevenLabs, InVideo. Cost: ~$50-100/month. "
            "Works from restricted regions (Crimea) - no face, no KYC for tools.",
    tags="faceless-youtube,ai-automation,warren-stick,case-study,crimea-ok",
    source="youtube-warren-stick-30-days",
    category="content-automation",
    importance=9,
    confidence=0.85,
    verification_method="youtube_research",
)
```

## Setup Commands

### One-time setup (run once per environment)

```bash
# 1. Install Agent Reach capability layer
hermes skills install agent-reach
# Or manual:
git clone https://github.com/Panniantong/Agent-Reach ~/.hermes/skills/agent-reach
cd ~/.hermes/skills/agent-reach
pip install -e .
agent-reach install --env=auto

# 2. Install Oh My Hermes skills
hermes skills tap add witt3rd/oh-my-hermes
hermes skills install omh-deep-research omh-ralplan omh-ralplan-driver \
    omh-deep-interview omh-ralph omh-ralph-driver omh-ralph-task \
    omh-autopilot omh-triage omh-triage-driver

# 3. Verify
hermes skills list | grep -E "omh-E "agent-reach|omh-"
```

### Development setup (project-local)

```bash
# OMH skills copied to project skills/
mkdir -p skills/omh-deep-research skills/omh-ralplan ... (10 skills)
# Download SKILL.md + references/ from github.com/witt3rd/oh-my-hermes/plugins/omh/skills/

# Agent Reach skill
mkdir -p skills/agent-reach/references
# Create SKILL.md from Agent Reach README
```

## Usage Patterns

### Pattern 1: Research Topic → Knowledge Cube

```python
from scripts.crystal.omh_integration import CrystalOMHResearchPipeline

pipeline = CrystalOMHResearchPipeline()
result = pipeline.scan_and_research("faceless YouTube automation AI 2024", auto_plan=True)

# result.stages contains:
# - intel_scan: YouTube videos + web results
# - deep_research: OMH multi-phase research plan
# - video_analysis: Transcripts + key findings
# - plan: OMH consensus plan (if auto_plan=True)

pipeline.save_intel("faceless YouTube automation AI 2024", result)
```

### Pattern 2: Deep Dive Single Video

```python
from scripts.crystal.omh_integration import crystal_youtube_transcript, crystal_web_read

transcript = crystal_youtube_transcript("https://youtube.com/watch?v=...")
web_content = crystal_web_read("https://github.com/user/repo")
```

### Pattern 3: Daily Intelligence Scan (Cron)

```python
# In cron job or autonomous loop
from scripts.crystal.intelligence import IntelScanner

scanner = IntelScanner()
items = scanner.scan()  # YouTube + GitHub + Web + RSS + AI news + Tools

# Items are IntelItem dataclasses ready for Knowledge Cube upsert
for item in items:
    upsert(content=item.description, tags=item.source, 
           source=item.source, category="intel-scan", ...)
```

### Pattern 4: OMH Autopilot for Complex Tasks

```python
from scripts.crystal.omh_integration import OMHIntegration

omh = OMHIntegration()

# Full pipeline: research → interview → plan → execute
autopilot = omh.run_autopilot(
    domain="CPA arbitrage funnel automation",
    goal="Build Telegram bot → lead magnet → email sequence → CPA offers"
)

# Or step by step:
research = omh.run_deep_research("Telegram CPA funnel automation 2024")
plan = omh.run_ralplan("Requirements from research...")
execution = omh.run_ralph(plan)
```

## Key Files Created/Modified

| File | Purpose |
|------|---------|
| `scripts/crystal/omh_integration.py` | Main integration layer: OMHIntegration, AgentReachIntegration, CrystalOMHResearchPipeline |
| `scripts/crystal/intelligence.py` | Updated IntelScanner with Agent Reach backends |
| `scripts/crystal/core.py` | CrystalEngine.run_full_cycle() + scan_intelligence() + run_omh_research() |
| `scripts/chain_heartbeat.py` | OMH + Agent Reach pipelines + modules registered |
| `scripts/kc_rag.py` | Knowledge upsert for YouTube research findings |
| `scripts/generate_portfolio.py` | Auto-regenerates docs/index.html from filesystem |

## Verification

```bash
# 1. Verify Agent Reach backends work
python -c "
from scripts.crystal.omh_integration import AgentReachIntegration
r = AgentReachIntegration()
print('YouTube:', len(r.youtube_search('test', 2)))
print('Web:', len(r.web_search('test', 2)))
print('GitHub:', len(r.github_search('AI agent', 2)))
"

# 2. Verify OMH skills available
python -c "
from scripts.crystal.omh_integration import OMHIntegration
omh = OMHIntegration()
print('Available:', [s for s in OMHIntegration.SKILLS if omh.is_available(s)])
"

# 3. Test Crystal full cycle
python -c "
import sys; sys.path.insert(0, 'scripts')
from scripts.crystal.core import CrystalEngine
e = CrystalEngine()
artifacts = e.run_full_cycle(quick=True)
print('Cycle artifacts:', artifacts)
"

# 4. Check chain heartbeat
python scripts/syscheck.py
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: agent_reach` | Run `agent-reach install --env=auto` or `pip install -e ~/.hermes/skills/agent-reach` |
| OMH skills not found | Check `skills/omh-*/SKILL.md` exists in project or `~/.hermes/skills/` |
| `yt-dlp` SSL errors | Use proxy: `yt-dlp --proxy socks5://127.0.0.1:10806 ...` |
| Chain heartbeat shows SILENT for new modules | Run `python scripts/system_heartbeat_fixer.py` then `python scripts/syscheck.py` |
| OMH skills not showing in `hermes skills list` | Ensure `hermes skills tap add witt3rd/oh-my-hermes` then `hermes skills install omh-*` |

## Lessons Learned (2026-07-25)

1. **Path handling on Windows**: Use raw strings `r"D:\\Portable_Soft\\hermes\\skills"` not `/d/Portable_Soft/hermes/skills` in Python code
2. **OMH skills location**: They live in `plugins/omh/skills/` in the repo, not `skills/` — copy to project `skills/` for local discovery
3. **Agent Reach is a capability layer, not a wrapper**: It installs/configures upstream tools (yt-dlp, gh, opencli, mcporter). Crystal calls those tools directly via convenience functions.
4. **Chain heartbeat needs all 3 events**: Missing `new_suggestions_ready` or `architecture_scan_complete` causes cascade failure (50 alerts observed 2026-07-24)
5. **Atomic JSON writes mandatory**: `os.replace(tmp, path)` prevents corruption when 10+ cron jobs write concurrently
6. **YouTube research synthesis (2026-07-25)**: 17 videos analyzed across 6 categories. Key patterns:
   - Faceless YouTube: AI scripts + ElevenLabs + InVideo → consistency > quality, 100+ videos for traction
   - Pinterest affiliate: Idea Pins → profile link → Amazon/high-ticket affiliate, free traffic, Crimea OK
   - Digital products: Gumroad templates/checklists/prompt packs, $15K with $5 PDF, free traffic via Medium
   - n8n Telegram automation: self-hosted free tier, webhook → OpenAI → Gmail/Telegram
   - CPA arbitrage: content locking + native ads (RichAds/PropellerAds), CPAGrip $50/day method
   - AI agent frameworks: LangGraph (production), CrewAI (beginner), AutoGen (flexible), Swarm (lightweight)
   - SEO 2026: AI-citable content, custom domains for AI tools, utility tools as lead magnets
   - Agent terminal: Herdr (spaces/worktrees/agent integration) > Tmux for agent work
   - Workday consulting: $95-400/hr but geo-locked, skip for Crimea
   - Priority for Crimea: faceless content, digital products, CPA, AI agents (all globally accessible)

## Lessons Learned (2026-07-26)

7. **GitHub Pages deployment fix**: Main branch was source, but content was on gh-pages branch. Solution: merge gh-pages → user branch → push to trigger Pages rebuild. `smart-home-cpa` now returns 200 OK.
8. **OMH skills tap location**: `witt3rd/oh-my-hermes` has skills in `plugins/omh/skills/` NOT root `skills/`. Download SKILL.md from `plugins/omh/skills/{skill}/SKILL.md`.
9. **Crystal cycle SILENT modules**: New OMH (10) + Agent Reach (6) modules show SILENT until first heartbeat. Run `python scripts/system_heartbeat_fixer.py` after using any OMH skill to activate them.
10. **Agent Reach YouTube backend**: Uses yt-dlp directly with proxy support. For Crimea/proxy environments: `yt-dlp --proxy socks5://127.0.0.1:10806 ...`
11. **Shane's 5 Plays pattern**: Translator / Juicer / Documentary / Campfire / Buffet — map directly to content pipeline templates.
12. **Google Flow Agent + ElevenLabs**: Avatar video generation for consistent character, voice cloning for brand consistency, dialogue automation for interviews.
13. **Custom domain automation**: `tool.yourdomain.com` → CNAME → auto-verify via Google AI Studio. Deploy 10+ AI utility tools as lead magnets.
14. **SEO AI-Citability Scorer**: Pre-publish gate scoring headings, factual density, citation quality, structure clarity. Makes content cite-worthy for AI search.
15. **Herdr terminal**: Spaces (vs Tmux sessions), native Worktrees, Agent API (`herdr agent start`), SSH native, plugin marketplace. Strong candidate for Tmux replacement.
16. **n8n deployment**: Node.js 24 incompatible with n8n (needs ≤22). Use Docker: `docker run -it --rm -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n`
17. **Content locker utilities**: 5 tools as lead magnets (SEO meta checker, roof calc, smart-home checklist, meta optimizer, speed estimator) → GitHub Pages → CPAGrip locker → CPA offers.
18. **Keyword monitoring bot**: 15+ freelance keywords + 5 stop-words → deduplication (msg_id + chat 24h) → formatted admin delivery → n8n webhook.
19. **LangGraph checkpointing in OMH**: Add `MemorySaver()` or `SqliteSaver("checkpoints.db")` with `config = {"configurable": {"thread_id": "session_123"}}` for OMH skill execution recovery.

## Related Skills

- `devops/chain-heartbeat` — System monitoring with OMH/Agent Reach pipelines
- `autonomous-ai-agents/hermes-agent` — Base agent configuration
- `self-improvement/crystal-self-awareness` — Crystal self-map
- `self-improvement/crystal-self-learning` — Crystal growth loop