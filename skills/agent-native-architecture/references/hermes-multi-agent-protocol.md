# Hermes Multi-Agent Collaboration Protocol

Implementation of agent-native architecture principles in Hermes using a Manager-Worker pattern inspired by FirstMate's fleet management.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  AGENT MANAGER (Orchestrator / "First Mate")                │
│  - Task queue management                                     │
│  - Worker registration & dispatch                            │
│  - Workflow execution (dependencies, parallel, sequential)  │
│  - Shared state: cache/task_queue.json, cache/worker_registry.json │
└──────────────────────────┬──────────────────────────────────┘
                           │ dispatch
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ CODE WORKER   │  │ REVIEW WORKER │  │ GENERAL WORKER│
│ (code_worker) │  │ (review_...)  │  │ (general_...) │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
              ┌────────────────────────┐
              │ KNOWLEDGE CUBE / CACHE │
              │ - Landing pages        │
              │ - Review results       │
              │ - Team log             │
              └────────────────────────┘
```

## Key Implementation Details

### 1. Agent Manager (`scripts/agent_manager.py`)
- **Task Queue**: JSON-based with statuses (PENDING → ASSIGNED → IN_PROGRESS → COMPLETED/FAILED)
- **Worker Registry**: Tracks worker status, capabilities, completed/failed counts
- **Dependency Resolution**: Tasks wait for dependencies before dispatch
- **Workflow Engine**: Pre-defined workflows (landing_review, arbitrage_pipeline)
- **Subprocess Execution**: Workers run as isolated subprocesses with JSON stdin/stdout

### 2. Worker Base Class (`scripts/worker_base.py`)
- **Shared Logging**: All workers write to `cache/agent_team.log` (append-only JSONL)
- **LLM Integration**: Built-in `call_llm()` method for local DeepSeek
- **Checklist System**: Load/save checklists from Knowledge Cube
- **File Operations**: Standardized read_file, save_checklist methods

### 3. Specialized Workers
| Worker | Purpose | Key Capabilities |
|--------|---------|------------------|
| `code_worker.py` | Create tools, landings, scripts | HTML landing generation, Python tool scaffolding |
| `review_worker.py` | Quality review | Landing checklist (12 items), code quality, content structure |
| `general_worker.py` | Fallback/basic tasks | Landing creation, research stubs, content stubs |

### 4. Communication Protocol
- **Task Data**: JSON passed via stdin to worker subprocess
- **Result**: JSON via stdout (last line)
- **Team Log**: Append-only JSONL for debugging/observability
- **Checkpoint Files**: `cache/{checklist}_results_{task_id}.json` for review artifacts

## Parity & Granularity Compliance

✅ **Parity**: Workers use same primitives (file I/O, LLM, subprocess) as the main agent
✅ **Granularity**: Each worker is a focused tool; complex workflows = task composition
✅ **Composability**: New workflows = new step sequences in agent_manager
✅ **Emergent**: Agent can handle open-ended "create and review landing" by composing workers

## Anti-Patterns Addressed

| Anti-Pattern | How We Avoid It |
|--------------|-----------------|
| Agent as router | Manager delegates OUTCOMES not function calls |
| Workflow-shaped tools | Workers have primitives; workflow = task sequence |
| Context starvation | Context passed explicitly in task_data |
| Heuristic completion | Workers explicitly return success/error JSON |
| Incomplete CRUD | Workers can create, read, update, delete files |
| Sandbox isolation | Shared cache/ directory = shared workspace |

## Usage Examples

### Register Workers
```bash
python scripts/agent_manager.py --register-worker code_001 --worker-type code_worker
python scripts/agent_manager.py --register-worker review_001 --worker-type review_worker
```

### Run Workflow
```bash
python scripts/agent_manager.py --workflow landing_review
```

### Create Ad-hoc Task
```bash
python scripts/agent_manager.py --create-task "Create landing for crypto offer" --worker-type code_worker --priority 3
```

## Files Created This Session

| File | Purpose |
|------|---------|
| `scripts/agent_manager.py` | Orchestrator with task queue, worker registry, workflow engine |
| `scripts/worker_base.py` | Base class with logging, LLM, checklist, file ops |
| `scripts/workers/review_worker.py` | Landing/code/content reviewer with 12-point checklist |
| `scripts/workers/code_worker.py` | Landing generator, tool creator |
| `scripts/workers/general_worker.py` | Fallback worker for basic tasks |

## Integration Points

1. **Knowledge Cube**: Workers save review results → KC for future learning
2. **ARBITRAGE_WORKSHOP.md**: Review findings can append to workshop
3. **email_intake.py**: New offers → tasks → workers → deployments
4. **Forge**: Workers can invoke Forge for dynamic tool creation
5. **Content Pipeline**: Review worker validates content before publish

## Next Steps

- [ ] Add `arbitrage_worker.py` for CPA offer research/deployment
- [ ] Add `content_worker.py` for video script generation
- [ ] Add `research_worker.py` for niche/trend analysis
- [ ] Implement async worker pool (currently sequential subprocess)
- [ ] Add worker health monitoring & auto-restart
- [ ] Integrate with Bayesian scorer for task prioritization
- [ ] Add git worktree isolation (FirstMate-style) for parallel safety