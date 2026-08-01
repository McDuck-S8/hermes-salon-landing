# Self-Improvement Loop: Low Conversion Root Cause (2026-07-18)

## The Problem

**Conversion rate: 0.27%** (17,704 suggestions → 19 skills over 31 runs)

The agent generates thousands of suggestions but almost none become skills or knowledge entries.

## Root Cause: 5:1 Internal-to-External Knowledge Ratio

```
Knowledge Cube sources (307 total):
├── scripts:           211 (68.7%)  ← INTERNAL
├── errors:             40 (13.0%)  ← INTERNAL
├── github-research:    26 (8.5%)   ← EXTERNAL
├── arbitrage-research: 18 (5.9%)   ← EXTERNAL
├── agent:               6 (2.0%)   ← INTERNAL
├── system:              2 (0.7%)   ← INTERNAL
└── user:                1 (0.3%)   ← EXTERNAL
```

**211 entries from own scripts vs 44 from external research**

The agent "breathes its own exhaust" — learns from its own errors and scripts, but rarely ingests new external knowledge.

## Why This Happens

| Pipeline | Status | Issue |
|----------|--------|-------|
| `signal_daemon` (trend scanner) | DEAD | Not running (daemon recovery needed) |
| `cube-categorizer` cron | STALLED | 1,582 unprocessed entries |
| `knowledge-gap-filler` cron | STALLED | Never fills gaps |
| Self-improvement loop | RUNNING | Only analyzes internal logs/errors |
| GitHub trending fetch | NOT SETUP | No cron for external research |
| AffiliateFix/Partnerkin/Reddit | NOT SETUP | No sources configured |
| YouTube channel monitor | NOT SETUP | No cron for video research |

## The Fix: Mandatory External Knowledge Daily Quota

### 1. Restart Daemons (Immediate)
```bash
python scripts/auto_recovery.py run
# Or manually restart:
python scripts/auto_recovery.py restart --daemon signal_daemon
python scripts/auto_recovery.py restart --daemon event_daemon
```

### 2. Add Daily External Research Cron Jobs

**GitHub Trending (AI, automation, arbitrage):**
```bash
# Every 6 hours
cron: "0 */6 * * *"
script: scripts/github_trending_fetcher.py
```

**AffiliateFix/Partnerkin case studies:**
```bash
# Daily at 9 AM
cron: "0 9 * * *"
script: scripts/affiliate_research_fetcher.py
```

**Reddit monitoring (r/affiliatemarketing, r/crypto, r/passive_income):**
```bash
# Every 12 hours
cron: "0 */12 * * *"
script: scripts/reddit_monitor.py
```

**YouTube channel monitor (arbitrage, AI automation):**
```bash
# Daily at 8 AM
cron: "0 8 * * *"
script: scripts/youtube_channel_monitor.py
```

### 3. Modify Self-Improvement Loop

In `scripts/self_improvement_loop.py`, add external quota check:

```python
def enforce_external_quota(suggestions: list, min_external_pct=0.30) -> list:
    """Ensure at least 30% of new suggestions come from external sources."""
    external_sources = {'github-research', 'arbitrage-research', 'user', 'thecuberesearch.com'}
    external_count = sum(1 for s in suggestions if s.get('source') in external_sources)
    total = len(suggestions)
    
    if total > 0 and external_count / total < min_external_pct:
        # Trigger external research fetch
        from emit_event import emit
        emit("knowledge_gap_detected", {
            "reason": f"External knowledge ratio {external_count/total:.1%} < {min_external_pct:.0%}",
            "action": "run_external_research_cron"
        })
    return suggestions
```

### 4. Knowledge Cube Processing Targets

| Metric | Current | Target (30 days) |
|--------|---------|------------------|
| Unprocessed entries | 1,582 | < 100 |
| External sources % | 14% | > 30% |
| New external entries/week | ~5 | > 30 |
| GitHub trending fetched | 0 | 20+ |
| Affiliate case studies | 0 | 10+ |
| Reddit insights/week | 0 | 15+ |

## Monitoring

Add to daily health check (`scripts/hermes_self_monitor.py`):

```python
def check_external_knowledge_health():
    conn = sqlite3.connect('cache/knowledge_cube.db')
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM knowledge_cube WHERE ts > datetime('now', '-7 days')")
    total_week = c.fetchone()[0]
    
    c.execute("""SELECT COUNT(*) FROM knowledge_cube 
                 WHERE ts > datetime('now', '-7 days') 
                 AND source IN ('github-research', 'arbitrage-research', 'user', 'thecuberesearch.com')""")
    external_week = c.fetchone()[0]
    
    ratio = external_week / total_week if total_week else 0
    
    if ratio < 0.30:
        return {"status": "DEGRADED", "ratio": ratio, "message": "External knowledge intake below 30%"}
    return {"status": "OK", "ratio": ratio}
```

## Success Criteria (30 Days)

- [ ] Signal daemon alive and scanning
- [ ] 3+ external research cron jobs running daily
- [ ] Knowledge Cube unprocessed < 100
- [ ] External sources > 30% of new entries
- [ ] Self-improvement conversion > 1% (3x improvement)
- [ ] At least 50 GitHub trending repos analyzed
- [ ] At least 20 affiliate/arbitrage case studies ingested
- [ ] At least 30 Reddit/forum insights captured

---

**Reference for:** `salon-lumiere-builder` skill (shows agent still builds manually instead of using external patterns), `self_improvement_loop.py`, `auto_recovery.py`, daily health monitoring.