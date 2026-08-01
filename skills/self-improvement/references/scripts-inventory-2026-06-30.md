# Scripts Inventory — 100+ Active Scripts

## Problem
Agent writes new code instead of using 100+ ready scripts in scripts/. User caught this 4+ times.

## Key Scripts to ALWAYS Consider Before Writing New Code

### System
- `hermes_config.py` — unified config, single source of truth
- `hermes_heartbeat.py` — health check + events
- `health_check.py` — verify critical files
- `memory_guard.py` — check/fix MEMORY.md
- `self_system.py` — unified entry point for self-analysis
- `session_boot.py` — event-driven session startup
- `session_manifest.py` — change tracker

### Events
- `event_bus.py` — event-driven architecture
- `event_bridge.py` — sensors → actions
- `event_daemon.py` — heartbeat every N seconds
- `event_classifier.py` — classify events
- `event_registry.py` — config from JSON
- `event_sense.py` — living nervous system
- `emit_event.py` — send events from any script

### Knowledge
- `knowledge_cube.py` — RAG storage
- `knowledge_brain.py` — active brain (consult BEFORE acting)
- `kc_rag.py` — FTS5 + tags
- `cube_feeder.py` — populate from files
- `kc_feeder.py` — populate from sessions
- `auto_tagger.py` — classify by domain
- `auto_recall.py` — search by keywords

### Agent
- `autonomous_agent.py` — autonomous agent
- `action_executor.py` — execute actions (HANDS)
- `action_feedback.py` — learning loop
- `goal_queue.py` — goal management
- `goal_evaluator.py` — evaluate goals
- `goal_executor.py` — execute goals
- `output_validator.py` — verify results BEFORE showing

### Proactive
- `proactive_engine.py` — proactive analysis
- `proactive_executor.py` — proactive actions
- `procedural_executor.py` — reflexes without LLM
- `curiosity_engine.py` — discover new things
- `dev_processor.py` — R&D processing

### Learning
- `crystal.py` — 30 modules self-learning
- `bayesian_scorer.py` — probabilistic scoring
- `feedback_store.py` — store action outcomes
- `self_improvement_loop.py` — self-improvement cycle
- `self_healing_monitor.py` — self-healing

### Monitoring
- `signal_daemon.py` — external signals (HN, GitHub)
- `signal_scanner.py` — scan signals
- `sensor_array.py` — sensors on everything
- `bot_monitor.py` — Telegram monitor
- `result_producer.py` — fix instead of alert

## Rule
BEFORE writing any new script, check if an existing one does the job.
User's 100+ scripts = ready infrastructure. Use it.