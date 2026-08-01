# EverOS Anti-Rot Integration - Work Plan (2026-07-02)

## Completed ✅
- Revisit lines on 100+ core Hermes files (5 layers + substrate)
- scripts/cache/expiry.md registry created
- salon-lumiere index.html fixed (paths, gallery, year)
- self-improvement skill updated with references

## Remaining Revisit Lines (16 scripts)
| Script | Status |
|--------|--------|
| curiosity_engine.py | ❌ |
| feedback_store.py | ❌ |
| fix_critical.py | ❌ |
| fix_proxy_all.py | ❌ |
| kc_feeder.py | ❌ |
| kc_populator.py | ❌ |
| kc_rag.py | ❌ |
| mcp_memory_bridge.py | ❌ |
| monitor.py | ❌ |
| result_producer.py | ❌ |
| salon_ai_bot.py | ❌ |
| skill_scanner.py | ❌ |
| user_needs_profiler.py | ❌ |
| web_surfer.py | ❌ |
| workflow_executor.py | ❌ |
| yt_pipeline.py | ❌ |

## Post-Revisit Integration Tasks
| Task | Description |
|------|-------------|
| sync_expiry.py | Auto-generate expiry.md from Revisit lines |
| LanceDB vector index | Add to Knowledge Cube (md + sqlite + lancedb) |
| Sealed entities | Namespace isolation in KC (arbitrage ≠ salon ≠ personal) |
| Cascade daemon | watchdog + apscheduler for event_daemon |
| Structlog migration | Migrate log_*.py to structured logging |
| Prompt slots | Dynamic context assembly in session_boot + autonomous_agent |
| Maintain-os workflow | Monthly auto + weekly light + on-contact cadence |

## Priority Order
1. Finish Revisit lines on remaining 16 scripts
2. Write sync_expiry.py
3. Add LanceDB to knowledge_cube.py
4. Add namespaces to KC for sealed entities
5. Rewrite event_daemon.py as cascade daemon
6. Migrate logging to structlog
7. Implement prompt slots
8. Create maintain-os cron workflow