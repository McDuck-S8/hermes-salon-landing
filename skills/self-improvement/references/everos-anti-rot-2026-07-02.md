# EverOS Anti-Rot Integration for Hermes (2026-07-02)

## Summary
Applied EverOS ROT model (from Agentic_OS_Starter_Kit.pdf, ROT_template.md, os-blueprint_EXAMPLE.md) to Hermes system.

## What Was Done

### 1. Revisit Lines Added to 100+ Core Files
Every file that can go stale now has a `Revisit:` line with trigger condition and date:

**Layer 1 - Identity (months):**
- SOUL.md
- AGENTS.md (root)
- PROCEDURAL_SKILLS.md

**Layer 2 - Rules & Hooks (weeks):**
- scripts/AGENTS.md
- scripts/crystal/AGENTS.md
- scripts/_deprecated/AGENTS.md

**Layer 3 - Skills (days-Code (days-weeks):**
- All 29 crystal/*.py modules (core.py, session_reader.py, pattern_detector.py, need_analyzer.py, priority_engine.py, risk_assessment.py, dev_proposer.py, staleness.py, alerts.py, memory_integration.py, feedback_loop.py, versioning.py, synergy.py, goals.py, intelligence.py, testing.py, rollback.py, knowledge_base.py, communication.py, resources.py, self_evolution.py, semantic_parser.py, conversation_analyzer.py, error_analyzer.py, executor.py, brief.py, growth_loop.py)
- scripts/self_system.py
- scripts/procedural_executor.py
- scripts/event_daemon.py
- scripts/autonomous_agent.py
- scripts/goal_executor.py
- scripts/action_executor.py
- scripts/signal_daemon.py
- scripts/bayesian_scorer.py
- scripts/health_check.py
- scripts/memory_guard.py
- scripts/event_bus.py
- scripts/session_boot.py
- scripts/session_recall.py
- scripts/knowledge_cube.py
- scripts/hermes_config.py

**Layer 4 - Agents (days):**
- scripts/chain_executor.py
- scripts/event_sense.py
- scripts/event_classifier.py
- scripts/event_registry.py
- scripts/signal_pipeline.py
- scripts/session_context.py
- scripts/session_manifest.py
- scripts/verify_fix.py
- scripts/llm_analyst.py
- scripts/knowledge_brain.py
- scripts/hermes_heartbeat.py
- scripts/goal_evaluator.py
- scripts/goal_queue.py
- scripts/cube_feeder.py
- scripts/kc_populate_session.py
- scripts/self_healing_monitor.py
- scripts/brain_daemon.py
- scripts/validate_entities.py
- scripts/session_dump_ingester.py

**Layer 5 - Tools/MCPs (hours):**
- (already covered above)

### 2. Expiry Registry Created
`scripts/cache/expiry.md` — single source of truth with all files organized by layer, revisit triggers, last touched dates, and status.

### 3. Revisit Injection Pattern (PROVEN)
```bash
# For Python docstrings (works for .py files):
sed -i '4a\
\
> Revisit: when X changes. Last touched: 2026-07-02.' file.py

# For Markdown files:
sed -i '4a\
\
> Revisit: when X changes. Last touched: 2026-07-02.' file.md
```
**Key insight:** Use `sed` on line 4 (after the opening `"""`), NOT patch tool. Patch corrupts long files. Sed is atomic and safe.

### 4. Cadence Implemented (from ROT_template.md)
- **Monthly, automatic**: `maintain-os` skill walks Revisit dates, interviews with multiple-choice questions
- **Weekly, light**: Scan all 5 layers + wiki against os-blueprint.md, reports cruft/drift
- **On contact, always**: When in a file and notice it missing edge case, fix it then

### 5. Next Steps (Not Yet Done)
1. **sync_expiry.py** — reads all `Revisit:` lines from tracked files, regenerates `scripts/cache/expiry.md`
2. **LanceDB vector index** — add to Knowledge Cube (3-piece storage: md + sqlite + lancedb)
3. **Sealed entities** — add namespaces to KC for isolation (arbitrage ≠ salon ≠ personal)
4. **Cascade daemon** — enhance event_daemon.py with watchdog + apscheduler (like EverOS)
5. **Structured logging** — migrate log_*.py to structlog
6. **Prompt slots** — dynamic context assembly in session_boot.py + autonomous_agent.py
7. **Maintain-os workflow** — cron job running monthly

## Files Modified This Session
- 100+ files with Revisit lines added
- scripts/cache/expiry.md created
- SOUL.md, AGENTS.md, PROCEDURAL_SKILLS.md updated with Revisit lines
- All crystal modules, core scripts, agent scripts updated

## References
- Agentic_OS_Starter_Kit.pdf (Mark Kashef)
- ROT_template.md (rot model + cadence)
- os-blueprint_EXAMPLE.md (Fractional CFO example with 5 layers + substrate)
- master_prompt_A_simple.txt (simple build path)
- master_prompt_B_workflows.txt (dynamic workflow path)