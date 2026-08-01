# Live Deployment Notes — Advisor-Orchestrator-Worker

## Current State (2026-07-22)

### Deployed Skills (6 + 1 meta)
1. **advisor-orchestrator-worker** — Meta-pattern for 3-tier model teams
2. **multi-agent-researcher** — Parallel CPA/competitor/creative research
3. **ai-financial-coach** — P&L, ROI, budget allocation, risk alerts
4. **always-on-agent** — Background surveillance (fast/medium/deep sensors)
5. **mcp-integration-pattern** — BrowserOS, Figma, Vapi, Supabase MCP wrappers
6. **self-improving-skills** — Skills that rewrite themselves via evals (Gemini)
7. **browser-automation** — BrowserOS MCP wrapper (for workers needing browser)

### Active Cron Jobs (Telegram delivery)
| Job ID | Skill | Schedule | Purpose |
|---|---|---|---|
| 2e04bc051ee0 | always-on-agent (fast) | */30 * * * * | Traffic costs, network health — CRITICAL only |
| 3543d7cd2e07 | always-on-agent (medium) | 0 * * * * | Offer scanner, creative radar — HIGH+ |
| 929901b02307 | ai-financial-coach (daily) | 0 7 * * * | Daily P&L reconcile + budget plan |
| d23201880828 | ai-financial-coach (weekly) | 0 9 * * 0 | Weekly portfolio review + test budget |
| bfcb16ffa847 | self-improving-skills | 0 3 * * * | Nightly evals on all self_improving skills |

### MCP Infrastructure
- **BrowserOS MCP** — Running on port 9003 (66 tools)
- **CDP on Chrome** — Port 9222 (user's real browser, authenticated tabs)
- **browser-harness** — Local copy at `/skills/autonomous-ai-agents/browser-harness/` for CDP bridge

### Worker Protocol (Validated 2026-07-22)

**WORKER TIMEOUTS ARE MANDATORY**
- Default 600s is too long for stuck calls
- Set `timeout: 300` in delegate_task
- Timeout handling: timeout = FIX (redispatch simpler) or ESCALATE

**WORKER BRIEF MUST INCLUDE:**
```json
{
  "goal": "...",
  "context": "...",
  "acceptance": [...],
  "tools_required": ["browser-automation", "web-search", "mcp-browseros"]
}
```

**TOOLS MAP FOR WORKERS:**
| Task Type | tools_required |
|---|---|
| Scrape CPA networks | ["browser-automation", "mcp-browseros"] |
| Search forums/news | ["web-search", "web-extract"] |
| Analyze creatives | ["browser-automation", "mcp-browseros"] |
| Financial calc | ["finance-core", "python"] |
| Sync data | ["mcp-supabase"] |

### Advisor Consult Protocol
**MANDATORY before ANY dispatch:**
```python
delegate_task(
  goal="Review this plan for gaps, contradictions, missing dependencies",
  context=f"Plan: {plan_json}",
  role="orchestrator"
)
```
Failure to consult = protocol violation. The orchestrator (you) does the consult.

### Status Board Format (after each loop step)
```
W1: DISPATCHED (browser-automation, 300s) | W2: DISPATCHED (web-search) | W3: PASS
```

### Budget Tracking
Set at Frame: `budget = 2 * subtask_count + 2 advisor_consults`
Track: dispatches, retries, advisor calls. Stop at budget or report.

## Known Issues / Fixes Applied

1. **Worker timeouts** — 3/4 initial workers timed out (600s). Fix: explicit 300s timeout + tools_required.
2. **Browser access** — Workers need `browser-automation` skill + `mcp-browseros` for real browser.
3. **Advisor consult** — Was optional, now MANDATORY before dispatch (patched).
4. **Worker brief format** — Added `tools_required` field (patched).

## Next Session Checklist
- [ ] Verify browser-harness CDP bridge to user's Chrome (port 9222)
- [ ] Test worker with `tools_required: ["browser-automation"]`
- [ ] Run Advisor consult on next multi-worker task
- [ ] Check self-improving-skills eval results (3am cron)