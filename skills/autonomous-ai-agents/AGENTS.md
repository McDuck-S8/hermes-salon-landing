# Autonomous AI Agents — Skills Directory

## Purpose
Skills for multi-agent orchestration, parallel research, financial intelligence, background surveillance, and self-improving agent patterns. These are **production-grade skills** for arbitrage/CPA automation — not experiments.

## Ownership
Created and maintained by Hermes Orchestrator. Each skill is self-contained with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- Every skill declares `self_improving: true` in frontmatter + eval schedule
- Skills integrate via `delegate_task` (workers) + Advisor consults
- Cron jobs defined in skill SKILL.md under "Cronjob Template"
- State persisted in `finance-core` (SQLite) + Knowledge Cube

## Work Guidance
**Adding a new skill:**
1. Create folder under `autonomous-ai-agents/`
2. SKILL.md with: name, description, license, metadata (author, version, source), self_improving config
3. references/ for domain knowledge (sensor specs, failure patterns, etc.)
4. templates/ for briefs, prompts, output formats
5. scripts/ for any Python helpers
6. Update this AGENTS.md Child DOX Index

**Modifying a skill:**
- Edit SKILL.md + affected references/scripts
- Run evals if self_improving: true (auto via cron at 03:00)
- Log to Knowledge Cube via `on_task_complete`

## Child DOX Index

| Skill | Purpose | Key Integrations |
|---|---|---|
| `advisor-orchestrator-worker` | **Meta-skill**: 3-tier model team pattern (Orchestrator/Workers/Advisor). Foundation for all multi-agent work. | `delegate_task`, any skill |
| `multi-agent-researcher` | Parallel research: CPA offers, networks, competitors, creatives, traffic sources. | `arbitrage-sensors`, `browser-automation`, `finance-core` |
| `ai-financial-coach` | P&L reconciliation, scheme viability scoring, budget allocation, risk alerts. | `finance-core`, `arbitrage-sensors`, `multi-agent-researcher` |
| `always-on-agent` | Background surveillance: fast (30m), medium (1h), deep (6h) sensors. Signal scoring → Telegram. | `finance-core`, `arbitrage-sensors`, `multi-agent-researcher` |
| `mcp-integration-pattern` | Standardized wrapper for external MCP servers (BrowserClaw, Figma, Vapi, Supabase...). | Hermes native MCP client, config.yaml |
| `self-improving-skills` | Skills that run evals, analyze failures via Gemini, patch themselves. | `skill-indexer`, Knowledge Cube, chain_heartbeat |

## Active Cron Jobs (deployed)

| Job ID | Skill | Schedule | Delivery |
|---|---|---|---|
| `2e04bc051ee0` | always-on-agent (fast) | `*/30 * * * *` | Telegram |
| `3543d7cd2e07` | always-on-agent (medium) | `0 * * * *` | Telegram |
| `929901b02307` | ai-financial-coach (daily P&L) | `0 7 * * *` | Telegram |
| `d23201880828` | ai-financial-coach (weekly) | `0 9 * * 0` | Telegram |
| `bfcb16ffa847` | self-improving-skills | `0 3 * * *` | Telegram |
| `6702b8f1b014` | self-improving-skills | `0 3 * * *` | Local |

## Architecture Flow

```
ALWAYS-ON (sensors) 
    │
    ▼
FINANCIAL COACH (scores portfolio impact)
    │
    ▼
ORCHESTRATOR (you) — decides: scale / kill / test
    │
    ├───► DELEGATE_TASK → Workers (landers, creatives, tests)
    │
    └───► ADVISOR CONSULT → Review before ship
    │
    ▼
SELF-IMPROVING SKILLS (nightly evals → patches)
```

## Verification
- Each skill has evals in `evals/` (cases.yaml, rubric.md, run_eval.py)
- Self-improving cron runs nightly, logs to KC
- Chain heartbeat event: `skill_self_improved` with pass rates