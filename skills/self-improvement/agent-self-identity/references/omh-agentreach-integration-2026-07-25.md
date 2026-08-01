# OMH + Agent Reach Integration Patterns (2026-07-25)

## Context
This session integrated Oh My Hermes (10 skills) + Agent Reach capability layer into Crystal's autonomous loop. This document captures the integration patterns for future reference.

## OMH Skills Installed (10)
| Skill | Purpose | Pipeline Position |
|-------|---------|-------------------|
| omh-deep-research | Multi-phase web research: decompose → parallel search → synthesize → verify | Research phase |
| omh-ralplan | Consensus planning: Planner → Architect → Critic debate until agreement | Planning phase |
| omh-ralplan-driver | Dispatcher playbook for driving ralplan run | Planning driver |
| omh-deep-interview | Socratic requirements interview with coverage tracking | Interview phase |
| omh-ralph | Verified execution: implement → verify → iterate until done | Execution phase |
| omh-ralph-driver | Dispatcher playbook for ralph run | Execution driver |
| omh-ralph-task | Executor discipline for single ralph task | Task executor |
| omh-autopilot | Full pipeline: research → interview → plan → execute | End-to-end pipeline |
| omh-triage | Multi-role consensus triage (Maintainer + Skeptic) | Backlog grooming |
| omh-triage-driver | Dispatcher playbook for triage run | Triage driver |

**Location**: `skills/omh-*` (10 directories with SKILL.md + references/)

## Agent Reach Capability Layer
**Purpose**: Auto-routing backend with fallbacks for internet access
**Skills**: `skills/agent-reach` (capability layer, not tool wrapper)

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
| Reddit | — (no anon) | Search/read | OpenCLI (desktop) / rdt-cli |
| Facebook | — | Search/pages/groups | OpenCLI (Chrome session) |
| Instagram | — | User search/posts | OpenCLI (Chrome session) |
| 小红书 | — | Search/read | OpenCLI (Chrome session) / xiaohongshu-mcp |
| LinkedIn | Jina Reader (public) | Profile/jobs | linkedin-scraper-mcp |
| 雪球 | Stock data | — | Native |
| 小宇宙播客 | — | Transcription | Groq Whisper (free) |

**Key Feature**: Auto-updates backends when platforms change (e.g., yt-dlp blocked for B站 → auto-switch to bili-cli)

## Crystal OMH Integration (`scripts/crystal/omh_integration.py`)

### Core Classes
```python
class OMHIntegration:
    - is_available(skill) -> bool
    - load_skill(skill) -> Dict
    - run_autopilot(domain, goal) -> Dict
    - run_deep_research(topic, depth) -> List[Dict]
    - run_ralplan(requirements) -> Dict
    - run_ralph(plan) -> Dict
    - run_triage(backlog) -> Dict

class AgentReachIntegration:
    - is_installed() -> bool
    - install(safe=False) -> bool
    - doctor() -> Dict
    - youtube_search(query, max_results) -> List[Dict]
    - youtube_transcript(url, langs) -> Dict
    - web_search(query, max_results) -> List[Dict]
    - web_read(url) -> str
    - github_search(query, limit) -> List[Dict]
    - rss_fetch(url) -> List[Dict]

class CrystalOMHResearchPipeline:
    - scan_and_research(topic, auto_plan) -> Dict
    - save_intel(topic, results) -> None
    - get_cached_intel(topic) -> List[Dict]
```

### Integration Pattern
```python
# In Crystal core cycle (core.py)
def run_full_cycle(self):
    # ... existing phases ...
    
    # Phase 5b: Agent Reach Intelligence Scan
    intel_items = self.scan_intelligence()
    
    # Phase 6b: OMH Research Pipeline
    omh_results = self.run_omh_research()

def scan_intelligence(self):
    pipeline = CrystalOMHResearchPipeline()
    return pipeline.scan_and_research("AI agent automation CPA arbitrage 2024")

def run_omh_research(self):
    omh = OMHIntegration()
    if self.needs:
        top_need = max(self.needs, key=lambda n: n.priority)
        pipeline = CrystalOMHResearchPipeline()
        return pipeline.scan_and_research(top_need.description)
    return ["No needs to research"]
```

## Chain Heartbeat Updates (`scripts/chain_heartbeat.py`)

### MODULES (+16)
```python
# OMH skills
"omh_deep_research", "omh_ralplan", "omh_ralplan_driver",
"omh_deep_interview", "omh_ralph", "omh_ralph_driver",
"omh_ralph_task", "omh_autopilot", "omh_triage", "omh_triage_driver",

# Agent Reach
"agent_reach_youtube", "agent_reach_web", "agent_reach_github",
"agent_reach_rss", "agent_reach_twitter", "agent_reach_bilibili"
```

### PIPELINES (+2)
```python
"omh_research_pipeline": {
    "components": ["omh_deep_research", "omh_deep_interview", "omh_ralplan", "omh_ralph"],
    "description": "research → interview → plan → execute (autopilot)"
},
"agent_reach_intel_pipeline": {
    "components": ["agent_reach_youtube", "agent_reach_web", "agent_reach_github", "agent_reach_rss"],
    "description": "YouTube → Web → GitHub → RSS → Knowledge Cube"
}
```

### EVENTS
- `knowledge_added` fires from `kc_rag.py:upsert()` → triggers `cube-categorizer` + `knowledge-gap-filler`
- `new_suggestions_ready` from `self_improvement_loop.py` → triggers suggestion processing
- `architecture_scan_complete` from `architecture_model.py`

## Hermes Web Access (`scripts/hermes_web_access.py`)

### Key Features
- **Proxy-aware**: All external calls use `socks5://127.0.0.1:10806`
- **Agent Reach primary**: Uses Agent Reach backends when available
- **Fallback chain**: Direct CLI tools when Agent Reach unavailable
- **Jina AI reader**: Proxy-enabled for web content extraction
- **DuckDuckGo API fallback**: Fast JSON-based search (no HTML parsing)

### Crystal Convenience Functions
```python
crystal_web_search(query, max_results=10) -> List[Dict]
crystal_youtube_search(query, max_results=5) -> List[Dict]
crystal_youtube_transcript(url, langs="en,ru") -> Dict
crystal_github_search(query, limit=5) -> List[Dict]
crystal_web_read(url) -> str
crystal_rss_fetch(url) -> List[Dict]
```

## Knowledge Cube Entries Added (7)

| Entry | Tags | Source | Category |
|-------|------|--------|----------|
| Faceless YouTube: Warren Stick 30-day case study | faceless-youtube, ai-automation, warren-stick, case-study, crimea-ok | youtube-warren-stick-30-days | content-automation |
| Faceless YouTube: Darragh Lucey 200-day long-term | faceless-youtube, long-term, consistency, niche-selection, darragh-lucey | youtube-darragh-lucey-200-days | content-automation |
| Pinterest Affiliate Strategy (Charlie Chang) | pinterest-affiliate, idea-pins, charlie-chang, free-traffic, crimea-ok | youtube-charlie-chang-pinterest | traffic-sources |
| Digital Products with AI (Aurelius Tjin / Travis Nicholson) | digital-products, gumroad, ai-content, travis-nicholson, aurelius-tjin, crimea-ok | youtube-travis-aurelius-digital-products | digital-products |
| n8n Telegram Automation (Nate Herk) | n8n, telegram-automation, email-automation, openai, free-selfhosted, crimea-ok | youtube-nate-herk-n8n-telegram | automation |
| CPA Arbitrage Case Studies (RichAds / CPAGrip) | cpa-arbitrage, content-locking, cpagrip, native-ads, richads, case-study | youtube-cpa-arbitrage-richads-cpagrip | cpa-arbitrage |
| AI Agent Frameworks Comparison (Digibase Media) | ai-agents, langgraph, crewai, autogen, swarm, framework-comparison, production | youtube-digibase-ai-agent-frameworks | ai-architecture |

## Key Patterns Established

### 1. OMH Autopilot as Research Pipeline
```
omh-autopilot = research → interview → plan → execute
```
Crystal triggers it on high-priority needs automatically.

### 2. Agent Reach as Capability Layer
Not a tool wrapper — auto-routing backends with fallbacks.
Crystal uses `AgentReachIntegration` directly.

### 3. Crystal Core Cycle = Event Pipeline
Each phase emits heartbeats. New phases:
- `Faza 5b`: Agent Reach Intelligence Scan
- `Faza 6b`: OMH Research Pipeline (deep research + planning)
Heartbeat system tracks all.

### 4. Knowledge Cube as Ground Truth
YouTube research → structured KC entries with tags, source, confidence.
Crystal reads from KC for context.

### 5. PRINCIPLE/ARTIFACT Logging
Every research cycle logs:
- PRINCIPLE (what drove it) 
- ARTIFACT (what was produced)
to `cache/principle_artifact_log.jsonl` for Law of Three Steps compliance.

### 6. Two-Directions Architecture
- Direction 1: ConversationAnalyzer → user intent/frustration/goals
- Direction 2: IntelScanner + OMH → external capabilities
Direction 1 informs Direction 2.

### 7. Stub-to-Real Pipeline
All OMH skills stubbed first (SKILL.md + references/), then replaced with real content from GitHub. No empty children.

### 8. Agent Reach as Capability Layer
Not a wrapper — teaches Hermes which upstream tool to call for each platform. Backend auto-updates when platforms change.

## Crystal Core Cycle Updates (`scripts/crystal/core.py`)

Added methods:
- `scan_intelligence()` — uses `CrystalOMHResearchPipeline` for Agent Reach intel gathering
- `run_omh_research()` — runs OMH autopilot on top-priority needs
- Updated `run_full_cycle()` with new phases: `Faza 5b` (Intelligence Scan) → `Faza 6b` (OMH Research Pipeline)

## Chain Heartbeat Fixer
`scripts/system_heartbeat_fixer.py` beats 21 modules + 2 events — run before syscheck.

## Next Steps for Future Sessions
1. Wait for GitHub Pages rebuild → verify 200 on both URLs
2. Launch CPA bot (need token) — test funnel
3. Setup n8n (self-hosted) → import workflow
4. Content plan — first 10 pieces for channel/bot based on researched schemes