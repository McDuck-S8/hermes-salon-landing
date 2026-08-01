---
name: tool-catalog
description: "** loaded at session boot. Agent MUST check this before deciding how to work.**"
---

# Tool Awareness Catalog

## File Search — ALWAYS use es.exe

**Path:** `D:/Portable_Soft/Everything-1.5.0.1408a.x64/es.exe`

```bash
ES="/d/Portable_Soft/Everything-1.5.0.1408a.x64/es.exe"
"$ES" salon_booking_bot    # finds ALL copies across the system instantly
"$ES" "event_classifier"   # instant, even on full disk
"$ES" -path "hermes" goal  # search within a path
```

NEVER use `find`, `ls -R`, `grep -r`, or `search_files` for locating files by name. es.exe queries the Everything index — instant. `find`/`ls` scan disk — slow, often times out on Windows.

## How to Use This Catalog

When you receive a task:
1. Read this catalog
2. Find the best tool/skill for the job
3. Use it — don't just chat about it

---

## Self-Identity (read FIRST)

**SELF_IDENTITY.md** — карта из 13 отделов. Читай ПЕРВЫМ при старте сессии.
Знает какой отдел за что отвечает, какие инструменты, какое состояние.
Путь: `D:/Portable_Soft/hermes/SELF_IDENTITY.md`

## Core Infrastructure (Hermes) — 151 active scripts

| Tool | What It Does | When to Use |
|------|-------------|-------------|
| `session_boot.py` | Processes all pending events at session start | EVERY session start — MANDATORY |
| `session_bridge.py` | Saves/loads session state between sessions | Session end — save state |
| `session_context.py` | Builds context from decisions, goals, weights | Session start — load context |
| `auto_recall.py` | Searches Knowledge Cube for relevant past experiences | Before any task — check what you already know |
| `knowledge_cube.py` | Stores experiences, domains, outcomes | After any task — record what happened |
| `hermes_hooks.py` | Event tracking (task/error/correction) | After every action — record outcome |
| `event_log.py` | Lightweight logging (no imports) | When hooks too heavy |
| `goal_queue.py` | Manages autonomous goals | Before work — check active goals |
| `reality_gate.py` | Checks system state (gateway, cron, network) | Session boot |
| `chain_executor.py` | Executes action chains (648 lines) | When multi-step needed |
| `autonomous_agent.py` | Core autonomy engine (2562 lines) | Manual execution |
| `file_watcher.py` | Event-driven file monitoring (watchdog) | Background daemon |
| `event_daemon.py` | Event processing daemon (every 2 min) | Cron: event-heartbeat |
| `event_reactor.py` | Reacts to KC changes, errors, goals | Auto — processes events |
| `file_watcher.py` | Watches sessions/data/cache for changes | Background — triggers ingestion |
| `conversation_ingester.py` | Extracts knowledge from full dialogs | On new session dumps |
| `session_dump_ingester.py` | Ingests session metadata into KC | On new session dumps |

## Skills (Specialized Agents)

### Engineering
| Skill | Purpose | Activate With |
|-------|---------|---------------|
| `engineering-frontend-developer` | React/Vue/Angular, UI, performance | "Use frontend developer" |
| `engineering-backend-architect` | API design, database, scalability | "Use backend architect" |
| `engineering-ai-engineer` | ML models, AI integration | "Use AI engineer" |
| `engineering-devops-automator` | CI/CD, infrastructure, deployment | "Use devops automator" |
| `engineering-code-reviewer` | Code review, security, quality | "Use code reviewer" |
| `engineering-database-optimizer` | Schema, queries, indexing | "Use database optimizer" |
| `engineering-software-architect` | System design, DDD, patterns | "Use software architect" |
| `engineering-security-engineer` | Security audit, hardening | "Use security engineer" |
| `engineering-prompt-engineer` | LLM prompt design | "Use prompt engineer" |

### Design
| Skill | Purpose | Activate With |
|-------|---------|---------------|
| `design-ui-designer` | Visual design, components | "Use UI designer" |
| `design-ux-researcher` | User testing, behavior analysis | "Use UX researcher" |
| `design-brand-guardian` | Brand identity, consistency | "Use brand guardian" |

### Marketing
| Skill | Purpose | Activate With |
|-------|---------|---------------|
| `marketing-growth-hacker` | User acquisition, viral loops | "Use growth hacker" |
| `marketing-content-creator` | Content strategy, copywriting | "Use content creator" |
| `marketing-social-media-strategist` | Cross-platform strategy | "Use social media strategist" |
| `marketing-seo-specialist` | SEO optimization | "Use SEO specialist" |

### Business
| Skill | Purpose | Activate With |
|-------|---------|---------------|
| `sales-outbound-strategist` | Prospecting, outreach | "Use outbound strategist" |
| `sales-deal-strategist` | Deal qualification, positioning | "Use deal strategist" |
| `finance-analyst` | Financial analysis | "Use finance analyst" |
| `product-manager` | Product strategy, roadmap | "Use product manager" |

### Research & Analysis
| Skill | Purpose | Activate With |
|-------|---------|---------------|
| `deep-research` | Multi-source fact-checked research | "Research this topic" |
| `graphify` | Build knowledge graph from any input | "Graphify this" |
| `discover` | Find new tools, updates, releases | "What's new in..." |
| `lavra-research` | Domain-matched research agents | "Research this" |

### Creative
| Skill | Purpose | Activate With |
|-------|---------|---------------|
| `imagegen` | Generate images, photos, illustrations | "Generate image of..." |
| `gemini-imagegen` | Gemini-based image generation | "Create image with Gemini" |
| `html-report` | Beautiful HTML reports | "Create HTML report" |

### Automation
| Skill | Purpose | Activate With |
|-------|---------|---------------|
| `agent-browser` | Browser automation, web scraping | "Open page, click, fill form" |
| `marketplace-search` | Ozon/Wildberries deal finding | "Find best price for..." |
| `rclone` | Cloud storage sync | "Sync files to S3" |
| `youtube-monitor` | Scan YouTube for tools, APIs, income ideas | "Check YouTube for...", "ютуб новинки" |
| `yt_pipeline.py` | YouTube URL → transcript → KC record → assess | "Process this YouTube URL" |
| `discover` | Find new tools, updates, releases | "What's new in..." |

## Built-in Browser Tools (替代 playwright+chromish)

**Hermes agent has built-in browser tools — DO NOT install playwright+chromium separately.**

| Tool | What It Does |
|------|-------------|
| `browser_navigate` | Open any URL |
| `browser_snapshot` | Get page accessibility tree |
| `browser_click` | Click elements by ref ID |
| `browser_type` | Type into input fields |
| `browser_scroll` | Scroll page |
| `browser_vision` | Take screenshot for visual inspection |
| `browser_console` | Get console output / evaluate JS |

Use these for ALL web surfing, scraping, and site analysis. They replace playwright+stealth+chromium.

## Workshop Index

**WORKSHOP_INDEX.md** — полный индекс всех 165 скриптов, cron расписания, зависимостей.
Путь: `D:/Portable_Soft/hermes/WORKSHOP_INDEX.md`
Читай когда нужно найти скрипт или понять что запускается когда.

### Self-Improvement
| Skill | Purpose | Activate With |
|-------|---------|---------------|
| `lavra-knowledge` | Capture solved problems | "Remember this solution" |
| `lavra-review` | Multi-agent code review | "Review this code" |
| `lavra-eng-review` | Engineering review | "Engineering review" |
| `lavra-ceo-review` | Business fit review | "CEO review this plan" |
| `yolo` | Toggle auto-approve mode | "/yolo on" |
| `ponytail` | Lazy senior dev mode — YAGNI, stdlib first, one line > fifty | "ponytail", "lazy mode", "simplest", "yagni", "do less" |

## Agency-Agents (249 specialized agents)

Full collection from msitarzewski/agency-agents. Each is a specialized expert with personality and workflows.

### Engineering (50+ agents)
`frontend-developer` `backend-architect` `mobile-app-builder` `ai-engineer` `devops-automator` `rapid-prototyper` `senior-developer` `code-reviewer` `database-optimizer` `software-architect` `sre` `data-engineer` `prompt-engineer` `multi-agent-systems-architect` `technical-writer` `git-workflow-master` `embedded-firmware-engineer` `incident-response-commander` `solidity-smart-contract-engineer` `codebase-onboarding-engineer` `minimal-change-engineer`

### Design (9 agents)
`ui-designer` `ux-researcher` `ux-architect` `brand-guardian` `visual-storyteller` `whimsy-injector` `image-prompt-engineer` `inclusive-visuals-specialist` `persona-walkthrough-specialist`

### Marketing (15+ agents)
`growth-hacker` `content-creator` `twitter-engager` `tiktok-strategist` `instagram-curator` `reddit-community-builder` `app-store-optimizer` `social-media-strategist` `seo-specialist` `linkedin-content-creator`

### Sales (9 agents)
`outbound-strategist` `discovery-coach` `deal-strategist` `sales-engineer` `proposal-strategist` `pipeline-analyst` `account-strategist` `sales-coach` `offer-lead-gen-strategist`

### Security (5 agents)
`security-auditor` `penetration-tester` `incident-responder` `compliance-officer` `threat-modeler`

### Strategy (5 agents)
`business-strategist` `competitive-analyst` `market-researcher` `pricing-strategist` `partnership-developer`

### Product (5 agents)
`product-manager` `product-analyst` `feature-prioritizer` `user-story-writer` `roadmap-planner`

### Finance (3 agents)
`financial-analyst` `budget-optimizer` `revenue-modeler`

### Testing (3 agents)
`qa-engineer` `test-architect` `performance-tester`

**To activate any agent:** "Use the [agent-name] agent to [task]"

## Dynamic Workflow Patterns (from PDF)

6 паттернов для автономной работы агента:

| Pattern | Когда использовать | Как работает |
|---------|-------------------|-------------|
| **Classify and Act** | Множество входящих запросов | Classifier → Handler. quarantine для untrusted input |
| **Fan Out and Synthesize** | Большое дело → много кусков | Один subagent на кусок, barrier merge |
| **Adversarial Verification** | Нужна проверка, не самооценка | Один извлекает, другой верифицирует |
| **Generate and Filter** | Нужен лучший из многих вариантов | Generator → Judge → Top N |
| **Tournament** | Ранжирование по judgment | Pairwise comparison, bracket |
| **Loop Until Done** | Неизвестно сколько проходов | Крутит до stop condition |

**Stack:** Fan Out + Adversarial Verify + Loop = zero false alarms

**Control dials:** /goal (hard completion), /loop (schedule), token cap (cost limit)

## Installed Tools & Where They Are

### Automated Income (Research-Backed)
| Method | Income/mo | Budget | Rating | How to start |
|--------|-----------|--------|--------|-------------|
| **Bandwidth Sharing (money4band)** | $10-30 | $0 | 8/10 | Docker + 15 platforms |
| Multi-Proxy Scaling | $30-80 | $0-20 | 7/10 | Method 1 + proxies |
| Crypto Funding Rate Arb | $15-50 | $500+ | 6/10 | Binance+Bybit bot |
| DePIN Storage (DeNet/Storj) | $5-20 | $0-20 | 6/10 | Run storage node |
| AI Content Pipeline | $5-30 | $0 | 5/10 | MoneyPrinterV2 |
| Binary Options Bot | -$50 to $50 | $10-50 | 3/10 | ORSTAC scripts |

**TOP PICK:** Bandwidth Sharing Stack — $0 start, Docker, 15+ platforms, $10-30/month, passive 24/7.
**Quick start:** `git clone https://github.com/MRColorR/money4band.git && cd money4band && python main.py`

### Social Media Posting (scripts/posting/)
| Script | Purpose | Status | To activate |
|--------|---------|--------|-------------|
| post_all.py | Post to 3 Telegram channels | Installed, not in cron | Add cron job |
| post_final.py | Post text + images to channels | Installed, not in cron | Add cron job |
| post_frontier.py | Posts for AI Frontier channel | Installed, not in cron | Add cron job |
| post_debug.py / post_debug2.py | Debug versions | Installed | Testing only |
| post_urls.py | Post URLs | Installed | Not active |
| post_with_images.py | Post with images | Installed | Not active |
| read_posts.py | Read post history | Installed | Utility |

**Telegram Bot Token:** in `hermes/.env` (TELEGRAM_BOT_TOKEN)
**Channels:** @neuro_kitchen_ai, @max_brain_chef_official, @max_brain_chef_ai, @ai_frontier_you
**Note:** Scripts read from `D:/Portable_Soft/.env` — fix path or copy token

### Data Seeding (scripts/)
| Script | Purpose | Status |
|--------|---------|--------|
| seed_creative_knowledge.py | Seed KC with creative domain | One-shot, done |
| seed_tools_knowledge.py | Seed KC with tools knowledge | One-shot, done |
| insert_mobile_mcp_kb.py | Insert mobile MCP research | One-shot, done |

### YouTube (scripts/)
| Tool | Purpose | Status |
|------|---------|--------|
| yt_pipeline.py | URL → transcript → KC → assess | Works, YouTube IP blocked |
| youtube-transcript-api | Python lib for transcripts | Installed (1.2.4) |
| yt-dlp | Video/audio downloader | Installed (2026.3.3) |
| youtube-monitor skill | Scan YouTube for tools/APIs | Installed |

### Security Scanning
| Tool | Purpose | Status |
|------|---------|--------|
| skillspector | NVIDIA skill security scanner | Repo cloned, needs Python 3.12+ |
| skill_scanner.py | Our regex-based scanner | Works, 64 patterns |
| llm_filter.py | False positive remover | Works, 47% filter rate |

### Knowledge Graph
| Tool | Purpose | Status |
|------|---------|--------|
| graphify | Build knowledge graphs | Installed, graph built (2002 nodes) |
| graph.html | Interactive visualization | D:/Portable_Soft/hermes/graphify-out/graph.html |
| graph.json | Raw graph data | D:/Portable_Soft/hermes/graphify-out/graph.json |

### MCP Servers
| Server | Config location | Status |
|--------|----------------|--------|
| memory | hermes config.yaml | Configured, never synced |
| context7 | lavra plugin .mcp.json | Installed |
| browseros | Available via browser tools | Works |

### Agency-Agents (249 specialists)
| Location | Count | Install command |
|----------|-------|-----------------|
| C:/Users/Asus/.claude/agents/ | 249 .md files | Done |
| D:/Portable_Soft/hermes/skills/agency-agents/ | Full repo (21 divisions) | Done |

### Key Config Files
| File | Purpose |
|------|---------|
| hermes/config.yaml | Main config (delegation, providers, tools) |
| hermes/.env | Telegram bot token, API keys |
| hermes/cron/jobs.json | 50 cron jobs (48 enabled) |
| hermes/skills/tool-catalog/SKILL.md | This file — tool awareness catalog |

## MCP Servers

| Server | What It Does | When to Use |
|--------|-------------|-------------|
| `memory` | Knowledge graph (entities + relations) | When you need semantic memory |
| `context7` | Documentation lookup | When you need API docs |
| `browseros` | Browser automation + 40+ services | Gmail, Slack, GitHub, Notion, etc. |

## Workflow Engine

The `workflow` tool chains multiple actions into automated pipelines:

| Workflow | What It Does | When to Use |
|----------|-------------|-------------|
| `deep-research` | Multi-source research with cross-checking | When you need thorough fact-checked answer |
| Custom inline JS | Chain agent(), parallel(), pipeline() | When you need multi-step automation |

```javascript
// Example: auto-pipeline for a YouTube URL
export const meta = { name: "youtube-pipeline", description: "Process YouTube URL" }
// agent() spawns subagent, parallel() runs concurrent tasks
```

## Deprecated Scripts (archived in scripts/_deprecated/)

All `_*`, `test_*`, `check_*` files moved to `scripts/_deprecated/`.
14 files archived. Do NOT use these.

## Workshop Index

**WORKSHOP_INDEX.md** — полный индекс мастерской (165 скриптов, 45 cron jobs).
Читай при необходимости понять что запускается и когда.
Путь: `D:/Portable_Soft/hermes/WORKSHOP_INDEX.md`

## Cron Schedule (45 jobs)

### Night (00:00-06:00)
- 01:00 self-assessment
- 02:00 nightly-self-analysis  
- 03:00 nightly-brain-scan
- 04:00 skill-evolution
- 04:15 cube-feeder
- 05:00 self-improvement-loop

### Day (06:00-22:00)
- 08:00 morning-report
- 09:00 curiosity-engine
- 10:00 Trend Scout (all)
- 18:00 Trend Scout (salon)
- 21:00 daily-report

### Periodic
- Every 2 min — event-heartbeat
- Every hour — hermes-heartbeat, salon-reminders
- Every 6h — cube-to-memory, system-metrics

## Auto-Repair (Step 0.6)

At every boot, session_boot.py scans SELF_IDENTITY.md for degraded departments.
Departments with "Требует настройки" or "Не работе...[truncated]

```
User gives task
    ↓
1. Run session_boot.py (MANDATORY)
    ↓
2. Check goal_queue for active goals
    ↓
3. Check session_context for history
    ↓
4. Read THIS catalog for available tools
    ↓
5. Pick best tool for the job
    ↓
6. Execute using the tool
    ↓
7. Record outcome via hermes_hooks
    ↓
8. Save state via session_bridge
    ↓
9. IF finding/planning → create/update project in projects/
    ↓
10. IF two projects complement → create synthesis project
```

## Project Management Rules

**Everything is a project:**
- Agent discovers something useful → create project entry
- Agent plans to build something → register as project
- Two projects complement each other → create synthesis project

**Project lifecycle:**
- DISCOVER → PLAN → BUILD → TEST → DEPLOY → MONITOR → SYNTHESIZE
- Agent must update status after each action
- Agent must track income from each project

**Synthesis projects:**
- Combine existing projects into new capabilities
- Example: salon-bot + telegram-tools = TG Business Suite
- Agent should suggest syntheses when it finds complementary projects

## CRITICAL: Tool Selection Rules (NEVER violate)

**Before EVERY action, use the RIGHT tool:**

| Task | USE | NOT |
|------|-----|-----|
| Read a file | `read_file` | `cat`, `terminal` |
| Search in files | `search_files` | `grep`, `terminal` |
| Edit a file | `patch` | `sed`, `terminal` |
| Create a file | `write_file` | `echo`, `terminal` |
| Web search | `web_search` | `curl`, `terminal` |
| Web extract | `web_extract` | `curl`, `terminal` |
| Complex task | `delegate_task` | manual coding |

**If you catch yourself using `terminal` for read/search/edit — STOP. Use the correct tool.**

## Knowledge Brain Integration (MANDATORY)

**Before acting:** call `knowledge_brain.py`
```python
from knowledge_brain import Brain
brain = Brain()
advice = brain.before("action description")
# Use advice["recommendation"] to pick the right tool
```

**After acting:** record result
```python
brain.after("action description", outcome="success", tools=["tool1", "tool2"])
```

**CLI:** `python scripts/knowledge_brain.py --record 'action' success 'tool1'`
**Status:** `python scripts/knowledge_brain.py --status`

## Subagent Timeout Handling

Subagents timeout at 600s. If a subagent times out:
1. Break the task into smaller pieces (max 3 subagents per batch)
2. If still timing out — do it yourself via `execute_code`
3. Never wait more than 2 minutes before checking status
4. If 3 consecutive timeouts — switch to `execute_code`

## Event-Driven > Cron

The system is event-driven. Do NOT create cron jobs for things that should react to events.
- Use `event_bus.py` for event-driven handlers
- Use `DIRECT_EVENT_HANDLERS` to register handlers
- Cron is ONLY for periodic tasks (heartbeats, reports)

## Rules

- **NEVER** just chat when a tool can do the job
- **NEVER** code yourself — delegate to Lavra via `delegate_task`
- **ALWAYS** check this catalog before deciding how to work
- **ALWAYS** use the most specific tool available
- **ALWAYS** record what you did (hermes_hooks)
- **ALWAYS** save state when done (session_bridge)
- **ALWAYS** when given a URL — auto-pipeline: fetch → extract → record → assess → act
- **ALWAYS** check scripts/ for EXISTING functionality before writing new code
- **NEVER** ask user "which scripts should I use?" — READ THEM YOURSELF
- **NEVER** ask unnecessary questions — just DO it
- **NEVER** say "I'll do X" without having done X

## Delegation Pattern

When task requires coding or long work:
```
1. user gives task
2. you delegate: delegate_task(goal="...", toolsets=["terminal", "file"])
3. you IMMEDIATELY respond: "Задача запущена. [что делает]."
4. subagent works in background
5. when done — you deliver result
```

User NEVER waits for you to finish. You are coordinator, not executor.

## delegate_task Pattern (Hermes built-in)

For heavy reasoning or parallel work, use `delegate_task`:
```
# Parallel (up to 3 concurrent):
delegate_task(tasks=[
    {goal: "Research X", context: "..."},
    {goal: "Analyze Y", context: "..."},
    {goal: "Plan Z", context: "..."},
])

# Single heavy task:
delegate_task(goal="Implement X", context="...", toolsets=["terminal", "file"])
```

Config: max_concurrent_children=3, max_spawn_depth=1, timeout=600s

**Batch sizing:** Max 3 beads per call. 600s timeout = ~3 beads. More = timeout.

## Auto-Pipeline for URLs

When user gives a URL:
```
1. webfetch(url) → get content
2. Extract: tools, APIs, techniques, ideas, code
3. hermes_hooks.on_task_complete("Discovered: ...", tags=["discovery"])
4. goal_queue.create_goal("Implement: ...", priority=5) — if actionable
5. Report to user: what found, what will do
```
