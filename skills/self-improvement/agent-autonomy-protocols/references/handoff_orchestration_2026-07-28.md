# Handoff & CLI Orchestration Reference — Session 2026-07-28

## Overview
Implementation of DIRECTIVE 0x17 (HANDOFF_PROTOCOL) and 0x18 (CLI_ORCHESTRATION). Enables agent-to-agent context transfer and multi-agent pipeline execution.

## Components

### 1. HandoffManager (`scripts/handoff_manager.py`)
Manages context transfer between agents.

#### HandoffContext Dataclass
```python
@dataclass
class HandoffContext:
    handoff_id: str
    from_agent: str
    to_agent: str
    task: str
    completed_work: Dict[str, Any]
    artifacts: List[Dict]          # Files, outputs, decisions
    decisions: List[Dict]          # Key decisions made
    open_questions: List[str]
    next_actions: List[str]
    created_at: str
    metadata: Dict
```

#### Key Methods
```python
mgr = HandoffManager()

# Create handoff
handoff = mgr.create_handoff(
    from_agent="video_processor",
    to_agent="video_intelligence_agent",
    task="Analyze YouTube video and generate business report",
    completed_work={"concepts": [...], "metadata": {...}},
    artifacts=[{"type": "video_metadata", "path": "cache/youtube/..."}],
    decisions=[{"decision": "Used oembed for metadata", "confidence": 0.9}],
    open_questions=["Which concepts are most actionable?"],
    next_actions=["Deep research top 3 concepts", "Generate report"]
)

# Build continuation prompt for receiving agent
prompt = mgr.build_continuation_prompt(handoff)
# Returns formatted prompt with full context

# Execute handoff with custom executor
result = mgr.execute_handoff(handoff, executor_fn=subagent_executor)
```

### 2. CLIOrchestrator (`scripts/cli_orchestrator.py`)
Multi-agent pipeline execution with dependency management.

#### AgentTask Dataclass
```python
@dataclass
class AgentTask:
    task_id: str
    agent_name: str
    prompt: str
    dependencies: List[str]  # Task IDs that must complete first
    timeout: int = 300
    priority: int = 0
```

#### AgentResult Dataclass
```python
@dataclass
class AgentResult:
    task_id: str
    agent_name: str
    success: bool
    output: str
    error: str = ""
    elapsed: float = 0.0
    artifacts: List[Dict] = None
```

#### Pipeline Building
```python
orch = CLIOrchestrator(max_workers=3)

# Sequential chain
orch.add_task("research", "competitive_intelligence_agent", "Analyze competitors")
orch.add_task("scripts", "content_pipeline_agent", "Write video scripts", deps=["research"])
orch.add_task("video", "video_learner_agent", "Generate videos", deps=["scripts"])
orch.add_task("publish", "social_poster_agent", "Post to channels", deps=["video"])

# Parallel tasks
orch.add_task("monitor", "channel_monitor_agent", "Check for new videos", deps=[])
orch.add_task("report", "analyst_agent", "Generate weekly report", deps=["research", "monitor"])

# Set executor
orch.set_executor(subagent_executor)

# Execute
results = orch.execute()
summary = orch.get_summary()
# {"total_tasks": 5, "successful": 4, "failed": 1, "total_time": 45.2}
```

#### Dependency Resolution
- Topological sort on DAG
- Parallel execution of independent tasks
- ThreadPoolExecutor with configurable workers
- Real-time progress logging

### 3. Integration Pattern

```
VideoProcessor (skill) 
    → creates HandoffContext 
    → HandoffManager.build_continuation_prompt()
    → passes to next agent (composed or single)
    
CLIOrchestrator defines pipeline
    → each step can be composed agent
    → respects dependencies
    → parallel where possible
```

## Usage Example

```python
# 1. Process video
pipeline = YouTubePipeline()
video_data = pipeline.process_video(url)

# 2. Extract concepts → tactical buffer
for concept in extract_concepts(video_data):
    tactical_buffer.add(concept.title, concept.description, "video", {"video_id": vid})

# 3. Handoff to intelligence agent
handoff = handoff_mgr.create_handoff(
    from_agent="video_processor",
    to_agent="competitive_intelligence_agent",
    task="Generate competitor intelligence report from video concepts",
    completed_work={"video_data": video_data, "concepts": concepts},
    artifacts=[{"type": "video_metadata", "data": video_data}],
    next_actions=["Deep research each concept", "Cross-reference with web data", "Generate report"]
)

# 4. Build prompt for receiving agent
prompt = handoff_mgr.build_continuation_prompt(handoff)

# 5. Execute (or let orchestrator run it)
orch = CLIOrchestrator()
orch.add_task("intel", "competitive_intelligence_agent", prompt)
orch.add_task("report", "content_pipeline_agent", "Write report from intelligence", deps=["intel"])
orch.set_executor(my_subagent_executor)
orch.execute()
```

## Test Results
- HandoffManager.create_handoff: ✅ PASS
- HandoffManager.build_continuation_prompt: ✅ PASS (structured output)
- CLIOrchestrator.add_task: ✅ PASS
- CLIOrchestrator.add_chain: ✅ PASS
- CLIOrchestrator.add_parallel: ✅ PASS
- CLIOrchestrator.execute: ✅ PASS (with mock executor)
- Dependency resolution: ✅ PASS (topological sort)

## Cache Storage
- Handoffs: `cache/handoffs/handoff_{id}.json`
- Index: `cache/handoffs/index.jsonl`
- Orchestration results: `cache/orchestration_results.json`

## Known Issues
1. Subagent executor not fully integrated (uses `python -m hermes_cli delegate` which requires hermes_cli module)
2. No persistence of handoffs across sessions (TODO: register with StatePersistenceManager)
3. No timeout handling in orchestrator for hung tasks
4. No retry logic for failed tasks

## Files
- `scripts/handoff_manager.py` — HandoffContext + HandoffManager
- `scripts/cli_orchestrator.py` — AgentTask + CLIOrchestrator
- `cache/handoffs/*.json` — Stored handoffs
- `cache/orchestration_results.json` — Pipeline results