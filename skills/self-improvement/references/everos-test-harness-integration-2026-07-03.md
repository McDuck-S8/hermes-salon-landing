# EverOS Anti-Rot + Test Harness Integration (2026-07-02/03)

## Summary
Applied EverOS ROT.md layered rot model to Hermes + implemented AI-First Business Playbook Test Harness.

## EverOS Anti-Rot Model Applied to Hermes

| Layer | Rot Speed | Action |
|-------|-----------|--------|
| Identity (SOUL.md, AGENTS.md) | Months | Quarterly review |
| Rules & Hooks (PROCEDURAL_SKILLS.md) | Weeks | Monthly scan |
| Skills (crystal/, scripts/*.py) | Days-weeks | Fix on contact |
| Agents (autonomous_agent, goal_executor) | Days | Weekly assessment |
| Tools/MCPs (hermes_config, providers) | Hours | Auto-fix + alert |
| Substrate (KC, session_recall, MEMORY.md) | Grows, doesn't rot | Enrich on contact |

## Maintenance Cadence
- **Monthly (auto)**: maintain-os scans Revisit dates, interviews for refresh
- **Weekly (light)**: cron/proxy/disk/health check
- **On contact**: edit file → update its Revisit line

## Test Harness Implementation
Created `skills/devops/test-harness/` with full SPEC → TESTS → GENERATE → VALIDATE → LOOP → DELIVER cycle:
- `harness.py` — orchestrator
- `verify_trigger.py` — standalone module for procedural_executor integration
- Templates for SPEC, TESTS, VALIDATION
- Example: proxy fix (keepalive_expiry=0) verified in 2 loops

## Integration Points
1. **Revisit lines** added to 50+ core files (SOUL.md, AGENTS.md, all scripts/*.py)
2. **expiry.md registry** created at `scripts/cache/expiry.md`
3. **Test Harness** integrated into `procedural_executor` via `verify_trigger.py`
4. **Kill Switches** design ready for implementation
5. **Structured logging** (structlog) design ready

## Key Lessons
1. **Separate modules for integration** — procedural_executor had syntax issues (non-ASCII), so verify_trigger.py was created as clean standalone module
2. **Accelerated testing works** — 1h real = 24h simulated with time compression
3. **Two loops is typical** — first catches syntax/logic, second catches integration
4. **Harness enforces discipline** — no DELIVER without all tests passing
5. **Revisit + expiry.md = single source of truth** for rot management

## Next Integrations (Priority)
1. War Room (/standup, /discuss)
2. Three-Layer Memory (FTS5 + embeddings + salience)
3. Kill Switches (6 env vars)
4. Exfiltration Guard
5. Auto-Assign (Gemini Flash classifier)
6. Suggestions Engine
7. Content Pipeline for Arbitrage