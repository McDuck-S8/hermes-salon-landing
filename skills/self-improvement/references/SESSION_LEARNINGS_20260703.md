# Session Learnings: Kill Switches + Exfiltration Guard + Three-Layer Memory Integration

## Key Techniques Discovered

### 1. FTS5 Contentless Table Sync (Critical Fix)
**Problem**: FTS5 table with `content='experiences', content_rowid='id'` requires JOIN with main table for queries.
**Solution**: 
```sql
-- WRONG (contentless FTS5 has no id/content columns)
SELECT id, content FROM knowledge_cube_fts WHERE knowledge_cube_fts MATCH ?

-- CORRECT (JOIN with experiences)
SELECT e.id, e.content, e.axis_domain, e.axis_outcome, e.tags, e.source, e.ts, e.importance,
       bm25(knowledge_cube_fts) as rank
FROM knowledge_cube_fts
JOIN experiences e ON knowledge_cube_fts.rowid = e.id
WHERE knowledge_cube_fts MATCH ?
```

### 2. Kill Switch Integration Pattern
**Standard pattern** for every dangerous boundary:
```python
# 1. Kill Switch check FIRST
if os.environ.get("HERMES_<SWITCH>_ENABLED", "true").lower() != "true":
    return {"status": "blocked", "reason": "HERMES_<SWITCH>_ENABLED=false"}

# 2. Exfiltration Guard check SECOND (if applicable)
try:
    from skills.devops.exfiltration_guard.scripts.exfil_guard import scan_outbound
    exfil_result = scan_outbound(content, source=f"<component>:<id>")
    if exfil_result.get("blocked"):
        return {"status": "blocked", "reason": f"Exfiltration: {exfil_result['matches']}"}
except ImportError:
    pass

# 3. Proceed with operation
```

### 3. Python Environment for Hermes
**Critical**: Hermes uses venv at `D:\Portable_Soft\hermes\hermes-agent\venv\Scripts\python.exe`
- Install deps with: `D:\Portable_Soft\hermes\hermes-agent\venv\Scripts\python.exe -m pip install <pkg>`
- System pip installs won't be visible to Hermes

### 4. Async Delegation Timeout Pattern
**Problem**: 3 parallel subagents × 600s timeout = network/API instability
**Solution**: 
- Direct execution in main thread for critical paths
- Small atomic steps via terminal/file tools
- Circuit breaker pattern for delegation (retry with backoff, fallback to local)

## User Preference Corrections (Embed in Workflows)

1. **Never use `write_file` for full Python file replacement** — use `sed -i` or `patch` for targeted edits (high risk of truncation)
2. **Always use correct tools**: `read_file`, `search_files`, `patch` — NOT `terminal` with cat/grep/sed
3. **Respond in Russian** — user communicates in Russian
4. **Autonomous execution** — don't wait for instructions, "бери и делай"
5. **Save findings immediately** — never "report without saving"
6. **Pre-Report Checklist**: Did I do Action A (found/researched)? → Did I do Action B (saved/recorded)? If NO → Save first, then report

## Architecture Insights for Future

### Middleware Pipeline Needed
Kill Switch, Exfil Guard, Audit Log all want to intercept tool calls → **unified middleware chain**:
```
pre_hooks (kill_switch, exfil_guard, audit_log) → tool → post_hooks
```

### Event Bus v2 Needed
Current `event_bus.py` + `event_daemon.py` are fragmented → need:
- Schema registry
- Replay capability
- Dead letter queue
- Guaranteed delivery

### KC Versioning Needed
For arbitrage: "how did KC look 1 week ago?" → git-like history for memory

### Agent Registry Protocol
Agents should self-register capabilities dynamically, not hardcoded in War Room

## Integration Status (2026-07-03)

| Component | Kill Switch | Exfil Guard | 3-Layer Memory |
|-----------|-------------|-------------|----------------|
| Telegram Bridge | ✅ HERMES_BRIDGE_ENABLED | ✅ check_telegram_message | — |
| KC Write | ✅ HERMES_KC_WRITE_ENABLED | ✅ scan_outbound | ✅ FTS5 + query_cube(query_text) |
| Cron Scheduler (tick) | ✅ HERMES_CRON_ENABLED | — | — |
| Cron Job (run_job) | ✅ HERMES_CRON_ENABLED | ✅ scan_outbound(prompt/script) | — |
| LLM Analyst | ✅ HERMES_LLM_ENABLED | — | — |
| File Writer | 🔄 Planned | 🔄 Planned | — |
| HTTP Client | 🔄 Planned | 🔄 Planned | — |