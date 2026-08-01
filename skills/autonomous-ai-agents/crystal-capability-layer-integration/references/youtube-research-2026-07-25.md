# YouTube Research Findings — 2026-07-25 Session

## Source Videos Analyzed

| Topic | Video | Channel | Views | Key Method |
|-------|-------|---------|-------|------------|
| Faceless YouTube (30 days) | "I tried Faceless YouTube Automation for 30 Days" | Warren Stick | 388K | ChatGPT scripts + ElevenLabs VO + InVideo editing |
| Faceless YouTube (200 days) | "I tried Faceless YouTube Automation for 200 days" | Darragh Lucey | 895K | Consistency > quality, 100+ videos for traction |
| Pinterest Affiliate | "The ONLY Pinterest Affiliate Strategy That Works in 2026" | Wealth Wisdom / Charlie Chang | 31K / 491K | Idea Pins (video) → profile link → Amazon Associates / high-ticket |
| Digital Products | "I Made $15K on Gumroad With a $5 PDF" | Travis Nicholson / Aurelius Tjin | 10K / 257K | Gumroad (free start) + Medium traffic + Mailchimp + ChatGPT + Canva |
| n8n Telegram Automation | "How to Build a Telegram AI Agent in n8n" | Nate Herk / Ritesh Hegde | 11K / 1.5K | n8n → Telegram trigger → OpenAI → Gmail/Outlook |
| CPA Arbitrage | "Case study: 116% ROI on Gambling in Brazil" | RichAds / CPAGrip tutorials | 4K | Content locking + native ads (RichAds/PropellerAds) |
| AI Agent Frameworks | "AutoGen vs CrewAI vs LangGraph vs Swarm" | Digibase Media / Jeff | 73K / 27K | LangGraph (prod), CrewAI (beginner), AutoGen (flexible) |

---

## Structured Knowledge Added to Knowledge Cube

Each entry was added via `scripts.kc_rag.upsert()` with `verification_method="youtube_research"`.

### 1. Faceless YouTube — Warren Stick (30-day case study)
- **Method**: ChatGPT scripts → ElevenLabs voiceover → InVideo editing
- **Result**: Realistic numbers, not "100k/month" fantasy
- **Key insight**: Consistency > quality, need 100+ videos for algorithm traction
- **Tools**: ChatGPT, ElevenLabs, InVideo, TubeBuddy/VidIQ
- **Cost**: ~$50-100/month
- **Crimea OK**: No face, no KYC for tools
- **Category**: content-automation | Importance: 9 | Confidence: 0.85

### 2. Faceless YouTube — Darragh Lucey (200-day long-term)
- **Method**: Long-term consistency, AI assists but human curation needed
- **Result**: AdSense + affiliate + digital products monetization
- **Key insight**: Evergreen niches > trending. 100+ videos for algorithm.
- **Tools**: TubeBuddy/VidIQ for keywords, Canva for thumbnails
- **Category**: content-automation | Importance: 8 | Confidence: 0.8

### 3. Pinterest Affiliate — Charlie Chang / Wealth Wisdom
- **Method**: Idea Pins (video pins) → link in profile → Amazon Associates / high-ticket affiliate
- **Niches**: Decor, recipes, DIY, finance
- **Hidden video strategy**: 6x impressions
- **Free traffic, works from restricted regions**
- **Tools**: Canva (pins), Tailwind (scheduling)
- **Category**: traffic-sources | Importance: 9 | Confidence: 0.9

### 4. Digital Products — Aurelius Tjin / Travis Nicholson
- **Method**: Templates, checklists, prompt packs on Gumroad (free to start)
- **Result**: Travis $15K with $5 PDF
- **Tools**: Gumroad, Medium (traffic), Mailchimp (email), ChatGPT (content), Canva (design)
- **No inventory, infinite margin, works from restricted regions**
- **Category**: digital-products | Importance: 9 | Confidence: 0.85

### 5. n8n Telegram Automation — Nate Herk / Ritesh Hegde
- **Method**: n8n self-hosted → Telegram trigger → OpenAI → Gmail/Outlook
- **Free tier generous, self-hosted on VPS or local**
- **CPA funnel**: webhook → lead magnet → email sequence → CPA offers
- **Alternative to Zapier/Make, no-code workflow builder**
- **Category**: automation | Importance: 9 | Confidence: 0.9

### 6. CPA Arbitrage — RichAds / CPAGrip
- **Method**: Content locking + native ads (RichAds/PropellerAds)
- **ROI**: 116% on gambling Brazil
- **CPAGrip**: Locker setup, pre-lander, postback, click tracking
- **$50/day method**: Free traffic (SEO/social) → content locker → CPA offer
- **Mistakes**: Wrong geo, bad pre-lander, no tracking
- **Tools**: CPAGrip, Voluum/Binomo tracker, native ad networks
- **Category**: cpa-arbitrage | Importance: 8 | Confidence: 0.75

### 7. AI Agent Frameworks — Digibase Media / Jeff
- **LangGraph**: Best for production — stateful graphs, human-in-the-loop, checkpointing
- **CrewAI**: Easiest for beginners — role-based agents
- **AutoGen**: Most flexible — multi-agent chat
- **Swarm**: Lightweight, educational
- **For CPA/arbitrage production**: LangGraph (state management, checkpointing)
- **For rapid prototyping**: CrewAI
- **Category**: ai-architecture | Importance: 8 | Confidence: 0.8

---

## Derived Action Items for Crystal

1. **Content Pipeline**: Faceless YouTube → Pinterest Idea Pins → Gumroad digital products (cross-promote)
2. **CPA Funnel**: Telegram bot (n8n) → Lead magnet (PDF checklist) → Email sequence (n8n) → CPA offers
3. **Traffic Sources**: Pinterest (free, Crimea OK) + YouTube Shorts (faceless, AI-generated)
4. **Automation Stack**: n8n (orchestration) + Agent Reach (intelligence) + OMH (planning/execution)
5. **Production AI Framework**: LangGraph for stateful CPA funnel agents

---

## Verification Commands

```bash
# Check Knowledge Cube entries
python -c "
from scripts.kc_rag import search
for entry in search('faceless-youtube', limit=5):
    print(entry['title'], entry['importance'], entry['confidence'])
"

# Verify all 7 entries
python -c "
from scripts.kc_rag import search
topics = ['faceless-youtube', 'pinterest-affiliate', 'digital-products', 
          'n8n-automation', 'cpa-arbitrage', 'ai-agent-frameworks']
for t in topics:
    results = search(t, limit=3)
    print(f'{t}: {len(results)} entries')
"
```

---

# YouTube Research Findings — 2026-07-26 Session (Extended)

## 17 Videos Analyzed (Extended Research)

| # | Video ID | Title | Key Method / Finding |
|---|----------|-------|---------------------|
| 1 | QNW4fW3moQ4 | Shane's 5 Plays for Content | Translator, Juicer, Documentary, Campfire, Buffet |
| 2 | lH14Z8noQjo | Google Flow Agent + ElevenLabs | Avatar video generation, consistent character |
| 3 | uI8uFjArhBI | Custom Domain AI Tools | tool.yourdomain.com auto-deploy via Google AI Studio |
| 4 | 82KcJA9NdRU | SEO AI-Citability Scorer | Score content for AI citations (headings, facts, citations) |
| 5 | nAcjQEGWoTY | Herdr Terminal for Agents | Spaces > Sessions, Worktrees native, Agent API |
| 6 | DPg3vfCKTXg | Terminal Automation | n8n self-hosted migration from Zapier |
| 7 | -6nsVIijCnI | AI Agent Frameworks Deep Dive | LangGraph stateful graphs for production |
| 8 | 00UsxuaG-5w | Lead Magnet Utility Tools | SEO audit, meta checker, roof calc as content locker bait |
| 9 | 47dS7GT2dHs | CPA Content Locking | CPAGrip locker on pre-lander → CPA offer |
| 10 | Oa2BXTerhtY | AI Video Generation | Consistent avatar + voice for faceless channels |
| 11 | 5WtwU51tcmw | Telegram Bot CPA Funnel | Keyword monitoring → bot → n8n → email → CPA |
| 12 | N_hCXvsR4cA | n8n Workflow Templates | Pre-built CPA funnel templates |
| 13 | A89-_SZ68fU | Smart Home CPA Landing | Content locker on GitHub Pages |
| 14 | PD0NzSu3G8s | Content Pipeline Automation | Shane's 5 plays + Flow Agent + ElevenLabs |
| 15 | g8dQBSKIGyc | Custom Domain AI Tools (Part 2) | Auto-deploy subdomains for AI utilities |
| 16 | EZbQ0qwPOzk | Herdr Deep Dive | Agent terminal with worktree + SSH + plugins |

## Key Patterns Synthesized (2026-07-26)

### Shane's 5 Plays → Production Pipeline Templates
1. **Translator Play**: Multi-language content repurposing → YT → Shorts → TikTok → Reels
2. **Juicer Play**: Long-form → shorts/clips automation → 1 video → 20+ clips
3. **Documentary Producer Play**: Research-heavy evergreen → high CPM niches
4. **Campfire Storyteller Play**: Narrative-driven engagement → community building
5. **Buffet Play**: Curated resource lists → lead magnets → affiliate/CPA

### Google Flow Agent + ElevenLabs Integration
- **Avatar video generation**: Consistent character across videos
- **Voice cloning**: Consistent narration brand
- **Dialogue automation**: Interview-style videos without guests

### Custom Domain Automation (Google AI Studio)
- **Format**: `tool.yourdomain.com` → CNAME → auto-verify
- **Use case**: Deploy 10+ AI utility tools as lead magnets
- **Each tool = content locker entry point**

### SEO "AI-Citability" Scorer
- **Score factors**: Headings hierarchy, factual density, citation quality, structure clarity
- **Integration**: Pre-publish gate in content pipeline
- **Goal**: Make content cite-worthy for AI search (Perplexity, Google AI Overviews)

### Herdr → Agent Terminal Replacement
- **Spaces** (vs Tmux sessions) — isolated agent workspaces
- **Worktrees** (native git worktree management) — parallel feature branches
- **Agent integration API** — `herdr agent start --config agent.yaml`
- **SSH native** — remote agent execution
- **Plugin marketplace** — extensible

---

## Crystal Action Items (2026-07-26)

### Content Pipeline Extension
- Add 5 Shane play templates to `scripts/content_factory.py`
- Integrate Flow Agent + ElevenLabs for avatar videos
- Build custom domain automation script (`deploy_custom_domains.py`)
- Add AI-citability scorer to `scripts/crystal/intelligence.py` pre-publish gate

### CPA Funnel Deployment
- **Keyword monitoring bot** (extend `cpa_telegram_bot.py`):
  - Keywords: "нужен разработчик", "нужен бот", "нужен сайт", "ищу специалиста", "Tilda", "amoCRM", "WebView", "Unity", "Kwork", "Upwork"
  - Stop-words: "бесплатно", "стажер", "тестовое", "стажировка", "опыт не нужен"
  - Deduplication: same message_id + chat within 24h
- **n8n workflow import**: `n8n_telegram_cpa_funnel.json` → local n8n
- **Content locker utilities** (5 tools):
  1. SEO meta title checker
  2. Roof calculator (smart-home)
  3. Smart-home checklist (existing)
  4. Meta description optimizer
  5. Page speed estimator
- **Smart-home-cpa integration**: Deploy locker on `https://mcduck-s8.github.io/hermes-salon-landing/smart-home-cpa/` (now 200 OK)

### Agent Infrastructure
- **Evaluate Herdr** → migrate `scripts/terminal/` from Tmux
- **LangGraph checkpointing** in `omh_integration.py` for OMH skills
- **Crystal core**: Add Herdr health check to chain_heartbeat.py

### SEO/Utility Tools as Lead Magnets
- Build 5 utility tools → deploy to GitHub Pages → content locker → CPA offers
- Each tool = separate subdomain via custom domain automation
- AI-citability scorer runs on all content pre-publish

---

## Session 2026-07-26 Accomplishments

| Component | Status | Notes |
|-----------|--------|-------|
| GitHub Pages smart-home-cpa | ✅ **FIXED** | Merged gh-pages → user branch → push → 200 OK |
| 17 Video Analysis | ✅ Complete | Reports in `reports/youtube_research_synthesis_20260726.md` |
| OMH Skills (10) | ✅ Installed | In `skills/omh-*` with SKILL.md |
| Agent Reach Skill | ✅ Created | `skills/agent-reach/SKILL.md` |
| Chain Heartbeat | ✅ Updated | +10 OMH modules, +6 Agent Reach, +2 pipelines |
| Crystal Core | ✅ Extended | Faza 5b (intel scan) + Faza 6b (OMH research) |
| Hermes Web Access | ✅ Fixed | Proxy, GitHub field fix, Exa search |
| CPA Telegram Bot | ✅ Code ready | `scripts/cpa_telegram_bot.py` (needs token) |
| n8n Workflow | ✅ Created | `scripts/n8n_telegram_cpa_funnel.json` |
| n8n Deployment | 🔄 In progress | Node.js 24 issue, Docker alternative |

---

## System Health Post-Session

```bash
python scripts/syscheck.py
# Events: 2/3 healthy (architecture_scan_complete SILENT)
# Modules: 29/40 healthy (10 OMH + 6 Agent Reach = SILENT until used)
# Pipelines: 5/5 healthy
# Services: 4/5 healthy (browserclaw DOWN due to permission error)
# Alerts: 50 (mostly SILENT modules - expected for new integrations)
```

**Note**: SILENT modules = newly added OMH/Agent Reach modules that haven't fired a heartbeat yet. They will activate on first use. Run `python scripts/system_heartbeat_fixer.py` after using any OMH skill.

---

## Next Session Priorities

1. **Deploy n8n** (Docker if Node.js 24 incompatible) → import workflow → test webhook
2. **Run CPA bot** with real token → test keyword monitoring
3. **Build 5 utility tools** → deploy to GitHub Pages → content locker
4. **Custom domain automation** for AI tools
5. **Evaluate Herdr** → decide migration from Tmux
6. **LangGraph checkpointing** in OMH integration
7. **Full Crystal cycle** with all new phases active