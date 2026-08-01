# EverOS Anti-Rot Integration in Hermes (2026-07-02)

## Summary
Applied EverOS ROT.md model to Hermes to prevent system rot after ~1 month of autonomy.

## Layered Rot Model Applied

| Layer | Rot Rate | Trigger | Action |
|-------|----------|---------|--------|
| Identity (SOUL.md, AGENTS.md) | Months | Role/principles change | Quarterly review |
| Rules & Hooks (PROCEDURAL_SKILLS.md, scripts/AGENTS.md) | Weeks | New reflex patterns | Monthly scan |
| Skills (crystal/, scripts/*.py) | Days-weeks | New patterns, infra changes | On-contact fix |
| Agents (autonomous_agent, goal_executor) | Days | Decision matrix changes | Weekly eval |
| Tools/MCPs (hermes_config, providers) | Hours | API changes, token expiry | Auto-fix + alert |
| Substrate (KC, session_recall, MEMORY.md) | Grows | Never rots, only compacts | On-contact enrich |

## Implementation

### 1. Revisit Lines on 50+ Core Files
Every file now has a `> Revisit:` line after the docstring:
```
> Revisit: when <trigger condition>. Last touched: 2026-07-02.
```

**Injection pattern:**
```bash
sed -i '4a\n\n> Revisit: when <trigger>. Last touched: 2026-07-02.' file.py
```
- Line 4 = after opening docstring
- Works for .md (markdown blockquote) and .py (docstring)
- Patch tool corrupts long files → use terminal `sed`

### 2. expiry.md Registry
Single source of truth at `scripts/cache/expiry.md`:
- All tracked files organized by layer
- Revisit trigger + last touched date + status
- `sync_expiry.py` script (to be written) regenerates from Revisit: lines

### 3. Maintenance Cadence
- **Monthly auto**: `maintain-os` workflow scans Revisit dates, interviews for refresh
- **Weekly light**: Scan for stale files, broken cron, dead proxies
- **On-contact**: When editing a file, update its Revisit line

### 4. Sealed-Box Entities
Entity isolation enforced:
- Arbitrage entities → never touch Salon entities
- Personal entities → never touch Client entities
- Each project = sealed box in Knowledge Cube

### 5. Cascade Daemon (Planned)
Replace event_daemon polling with:
- `watchdog` for file changes → auto-ingest → KC update
- `apscheduler` for timed scans with adaptive backoff
- Auto-evolution: pattern detected → proposal → test → apply

## Next Steps
1. Add LanceDB vector index to Knowledge Cube (3-piece storage: md + sqlite + lancedb)
2. Migrate log_*.py to structlog (structured, queryable logs)
3. Prompt slots in session_boot + autonomous_agent (dynamic context assembly)
4. Write `sync_expiry.py` to auto-generate expiry.md from Revisit: lines