# Content Studio Patterns for Hermes (2026-07-02)

## Dual AI Provider Strategy
| Task Type | Provider | Rationale |
|-----------|----------|-----------|
| Heavy reasoning, complex coding, planning | Claude Code / OpenRouter (Claude Sonnet) | Best reasoning, tool use |
| Cheap classification, embeddings, suggestions, clustering | Gemini Flash (free tier) | Fast, large context, free |
| Local/offline/privacy | Local models (if available) | No API calls, data stays local |

## Pipeline-Centric Architecture (Content Studio → Arbitrage)
```
Research → Create → Publish → Repurpose → Analyze
    ↓
Signal → Validate → Workshop → Deploy → Track
```
- **Research Agent**: signal_daemon + curiosity_engine → кирпичи в WORKSHOP
- **Create Agent**: rd_processor + dev_processor → схема (math + ЦА + withdrawal)
- **Publish Agent**: deploy_salon + telegram_bot → лендинг/бот/канал
- **Repurpose Agent**: один кирпич → под разные geo/каналы/офферы
- **Analyze Agent**: analytics + suggestions → kill/scale decisions

## AGENTS.md + CLAUDE.md Pattern (Already in Hermes, Deepen)
- Каждый скрипт/папка = свой CLAUDE.md с контекстом
- AGENTS.md = правила для AI-ассистентов при разработке
- Global CLAUDE.md (SOUL.md) + Project CLAUDE.md (AGENTS.md per directory)

## Database Schema with RLS/Indexes (Supabase → Knowledge Cube)
- **Indexes**: FTS5 (keyword), Vector (embeddings), B-tree (time, domain)
- **Triggers**: auto-embedding on insert, auto-decay, salience update
- **Namespaces/RLS-analog**: sealed entities (arbitrage ≠ salon ≠ personal)

## Multi-Format Native (Shorts, Carousels, Cross-Platform)
- Один кирпич → под разные geo/каналы/офферы
- В Hermes: одна схема арбитража → под разные трафик-источники/офферы/страны

## Agent-Ready Documentation
- CLAUDE.md для setup workflow
- AGENTS.md для agent instructions
- SETUP.md для manual installation
- supabase-schema.sql equivalent → KC schema migration scripts

## Modern Stack Insights (Next.js 16, React 19, shadcn/ui)
- Edge/Serverless compatible
- TypeScript strict
- Component registry (components.json)
- Vercel deployment ready

## Integration with Hermes
| Content Studio | Hermes Mapping |
|----------------|----------------|
| Video Pipeline | Arbitrage Pipeline |
| Thumbnails | Creative assets per scheme |
| Multi-Platform Publishing | Multi-channel deployment (TG, web, email) |
| Content Repurposing | One scheme → multiple offers/geos |
| Shorts & Carousels | Micro-content for TG channels |
| Analytics | ROI tracking per scheme |
| Peer Tracking | Competitor signal scanning |
| AI News Digest | signal_daemon + curiosity_engine |

## Action Items for Hermes
1. Add Gemini Flash integration for cheap tasks (classifier, embeddings, suggestions)
2. Reorganize skills/ by departments (arbitrage, devops, crystal, content, test-harness)
3. Add LanceDB vector index to Knowledge Cube
4. Implement Test Harness pattern in verify_fix.py
5. Add Closed Loop to procedural_executor (execute → measure → analyze → adjust)
6. Implement Queryable Business Brain (knowledge_brain.py + session_recall + KC)
7. Add Auto-Assign classifier for goals (Gemini Flash)
8. Add Suggestions feature (weekly job analyzing agent workload)
9. Add War Room (/standup, /discuss) for agent council
10. Add Exfiltration Guard for outgoing content