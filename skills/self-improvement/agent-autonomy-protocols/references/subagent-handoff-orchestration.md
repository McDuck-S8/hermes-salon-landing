# Subagent Context & Handoff Patterns — 2026-07-28

## Full Context Injection (DIRECTIVE 0x0F)

Every subagent MUST inherit the Principal's complete execution context:

```python
SUBAGENT_ENV = {
    **os.environ,                              # ALL environment variables
    "HERMES_HOME": str(HERMES_HOME),           # Canonical path
    "ALL_PROXY": "socks5://127.0.0.1:10806",   # v2rayN SOCKS5
    "HTTPS_PROXY": "socks5://127.0.0.1:10806",
    "HTTP_PROXY": "socks5://127.0.0.1:10806",
    "PYTHONPATH": f"{HERMES_HOME}/scripts;{os.environ.get('PYTHONPATH', '')}",
    "PATH": f"{HERMES_HOME}/hermes-agent/.venv/Scripts;{os.environ.get('PATH', '')}",
    "WORKDIR": str(HERMES_HOME),
}
```

### Implementation
- `scripts/hermes_subagent.py` — unified launcher with full context
- `scripts/subagent_context_manager.py` — context building + delegation
- `scripts/delegation_manager.py` — MUST inject context before spawning

### Checklist for Every Delegation
- [ ] ALL_PROXY / HTTPS_PROXY / HTTP_PROXY set to v2rayN
- [ ] HERMES_HOME resolved to canonical path
- [ ] Python venv path in PATH
- [ ] PYTHONPATH includes scripts/
- [ ] Working directory = HERMES_HOME
- [ ] API keys/credentials available

---

## Handoff Protocol (DIRECTIVE 0x10)

Agent A completes work → packages context → Agent B continues seamlessly.

### Handoff Context Structure
```python
@dataclass
class HandoffContext:
    handoff_id: str              # UUID for tracking
    from_agent: str              # Source agent name
    to_agent: str                # Target agent name
    task: str                    # Original task description
    completed_work: Dict         # What was done
    artifacts: List[Dict]        # Files, outputs, cache entries
    decisions: List[Dict]        # Key decisions with confidence
    open_questions: List[str]    # What remains unclear
    next_actions: List[str]      # Concrete next steps
    metadata: Dict               # Extra context
```

### Usage
```python
from scripts.handoff_manager import HandoffManager

mgr = HandoffManager()

handoff = mgr.create_handoff(
    from_agent="competitive_intelligence_agent",
    to_agent="content_pipeline_agent",
    task="Build competitor content strategy",
    completed_work={"competitors": [...], "maps_data": {...}},
    artifacts=[{"type": "cache", "path": "cache/youtube/*.json"}],
    decisions=[{"decision": "Focus on top 3 competitors", "confidence": 0.9}],
    open_questions=["Which platform to prioritize?"],
    next_actions=["Write video scripts", "Generate thumbnails", "Schedule posts"]
)

# Agent B receives full context
prompt = mgr.build_continuation_prompt(handoff)
# → "Continue from where competitive_intelligence_agent left off..."
```

### Handoff Storage
- `cache/handoffs/handoff_<id>.json` — individual handoff
- `cache/handoffs/index.jsonl` — chronological index

---

## CLI Orchestration (DIRECTIVE 0x11)

Multi-agent pipelines with dependencies, parallel execution, result aggregation.

### Pipeline Definition
```python
from scripts.cli_orchestrator import CLIOrchestrator

orch = CLIOrchestrator(max_workers=3)

# Sequential chain
orch.add_task("research", "competitive_intelligence_agent", "Analyze competitors")
orch.add_task("scripts", "content_pipeline_agent", "Write video scripts", deps=["research"])
orch.add_task("video", "video_learner_agent", "Generate videos", deps=["scripts"])

# Parallel task (runs alongside chain)
orch.add_task("monitor", "youtube_channel_monitor", "Set up channel alerts", deps=[])

# Execute
orch.set_executor(subagent_executor)
results = orch.execute()

# Results aggregated
summary = orch.get_summary()
# {"total": 4, "successful": 4, "failed": 0, "total_time": 45.2}
```

### Dependency Resolution
- Topological sort of task graph
- Parallel execution where deps allow
- Max workers respected
- Results passed to dependent tasks

### Output Aggregation
- Individual results in `orch.results`
- Summary in `orch.get_summary()`
- Full trace saved to `cache/orchestration_results.json`

---

## Subagent Batching (DIRECTIVE 0x0B)

For long-running external operations (YouTube, web scraping):

### Rules
- Max 5 items per subagent
- 60s timeout per item
- If timeout → retry with fallback (curl + proxy, oembed)
- Monitor heartbeat: silent > 2 cycles → restart with fallback

### Batch Processing Pattern
```python
def process_youtube_batch(urls: List[str], batch_size: int = 5):
    batches = [urls[i:i+batch_size] for i in range(0, len(urls), batch_size)]
    
    for batch in batches:
        # Launch parallel subagents
        for url in batch:
            deleg_task(
                goal=f"Process {url}",
                context="Full Hermes context injected",
                role="leaf"
            )
        # Wait for completion (with heartbeat monitoring)
        # Retry failures with faster fallback
```