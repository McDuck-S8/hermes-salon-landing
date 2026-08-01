# Suggestions Engine — Implementation Notes (Session 2026-07-03)

## Actual Work Done

### 1. Skill Skeleton Created
- `SKILL.md` with full architecture
- Weekly cron design: `0 3 * * 1` (Monday 3 AM)
- Metrics collection plan per agent
- Analysis prompt for LLM
- Proposal output format
- Auto-execution gated by `HERMES_SUGGESTIONS_AUTO_CREATE`

### 2. Key Design Decisions
- **Metrics per agent per week**: task count, avg duration, failure rate, tool diversity, domain spread, blocked count, skill gaps
- **Thresholds**: >50 tasks/week, >30min avg, >20% failure rate, >10 unique tools, >5 domains, >5 blocked
- **Confidence gate**: ≥0.8 for auto-creation
- **Fallback**: Main agent reviews proposals <0.8

### 3. Integration Points Planned
- `scripts/collector.py` — reads fabric, cron logs, KC for per-agent metrics
- `scripts/analyzer.py` — calls LLM with analysis prompt
- `scripts/proposer.py` — creates agent scaffolds + registers in War Room
- `scripts/weekly_cron.py` — orchestrates the full cycle

### 4. Next Steps (Priority Order)
1. Implement `scripts/collector.py` — gather metrics from fabric + cron + KC
2. Implement `scripts/analyzer.py` — LLM analysis with structured output
3. Implement `scripts/proposer.py` — scaffold new agents + War Room registration
4. Add cron job: `HERMES_SUGGESTIONS_CRON="0 3 * * 1"`
5. Test with current 5 agents (main, comms, content, ops, research)