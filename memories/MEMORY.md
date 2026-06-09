# Hermes Memory — System State & Learnings

## System Architecture

Hermes is an autonomous, self-healing, self-learning, proactive system.

### Core Modules

| Module | File | Purpose |
|---|---|---|
| Autonomous Agent | `scripts/autonomous_agent.py` | Decision brain — SURVIVE → LEARN → PRODUCE |
| Event Evolution | `scripts/event_evolution.py` | Event-driven triggers and knowledge capture |
| Self-Healing | `scripts/self_healing_monitor.py` | Cron job restart on failure |
| Self-Improvement | `scripts/self_improvement_loop.py` | Pattern detection, skill auto-creation |
| Proactive Executor | `scripts/proactive_executor.py` | Applies fixes, verifies results |
| Knowledge Cube | `scripts/knowledge_cube.py` | SQLite knowledge storage |
| Core Engine | `scripts/core_engine.py` | Connects Cube + Lavra + Sessions |
| Unified System | `scripts/unified.py` | Orchestrator (duplicates core_engine) |

### Cron Loop

| Job | Interval | Script |
|---|---|---|
| self-healing-monitor | 15 min | `self_healing_monitor.py` |
| proactive-executor | 15 min | `proactive_executor.py` |
| system-watcher | 60 min | `system_watcher.py` |
| unified-cycle | 120 min | `unified_cron.py` |
| self-improvement | daily | `self_improvement_loop.py` |
| self-analysis | nightly | `self_analysis_cron.py` |
| self-assessment | daily | `self_assessment_cron.py` |
| skill-evolution | periodic | `skill_evolution_cron.py` |

### Decision Hierarchy

```
SURVIVE (tier 1) — fix errors, maintain health
  ↓
LEARN (tier 2) — improve Knowledge Cube, discover patterns
  ↓
PRODUCE (tier 3) — generate value for user
```

### Data Flow

```
Event → EventMonitor → EvolutionTrigger → Action → Knowledge Cube
Cron → Autonomous Agent → Decision Matrix → Execute → Log
Self-Improvement → Analyze → Suggestions → Apply → Feedback
Self-Healing → Detect → Restart → Verify → Alert (3x fails)
```

## Known Issues (2026-06-09)

1. **SOUL.md was empty** — now filled with persona definition
2. **core_engine.py and unified.py overlap** — both connect to Cube/Lavra/Sessions
3. **Hardcoded paths** in unified.py: `D:/Portable_Soft/hermes`
4. **HERMES_HOME** defined inconsistently across scripts
5. **MEMORY.md was sparse** — now populated

## Learnings

- Knowledge Cube auto-growing works but needs quality control
- Self-healing successfully restarts failed cron jobs
- Self-improvement loop creates skills from repeated patterns (3+ occurrences)
- Proactive executor applies LLM-suggested fixes with verification
- Event evolution tracks task completions, errors, and user corrections

## Active Knowledge Cube Stats

- Experiences: growing (auto-feeder + white spot exploration)
- Domains: system, coding, communication, research, devops, browser, etc.
- White spots: being filled by autonomous exploration
- Failure rate: monitored and declining

## Cycles Completed: 63+

## Session History

- 2026-06-09: DOX framework integrated, AGENTS.md hierarchy created
- System audit: identified duplicate modules, hardcoded paths, empty SOUL.md
- Memory consolidation in progress