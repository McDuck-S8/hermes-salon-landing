# Memory Architecture Research — 2026-06-22

## Sources

### Kjetil Furås — "Give Your AI Agent Persistent Memory in 2026"
URL: https://kjetilfuras.com/ai-agent-persistent-memory

Key points:
- Runs autonomous AI agent as 24/7 daemon (content pipeline, social media, analytics)
- File-based memory: learnings.md, observations.md, goals.md, daily-logs/
- learnings.md < 100 lines, curated aggressively
- Agent reads on boot, writes on tool execution
- No vector DB, no embeddings, no retrieval pipeline — just markdown files
- "The thing that makes it actually useful isn't the LLM — it's the memory system"

Boot pattern:
```python
def start_session(agent):
    learnings = read_file("~/.agent/learnings.md")
    goals = read_file("~/.agent/goals.md")
    agent.system_prompt += f"## What you've learned:\n{learnings}\n## Current goals:\n{goals}"
```

Observation pattern:
```python
def observe(observation: str, category: str = "pattern"):
    timestamp = datetime.now().isoformat()
    entry = f"- [{timestamp}] ({category}) {observation}\n"
    with open("~/.agent/observations.md", "a") as f:
        f.write(entry)
```

### Reddit r/AI_Agents — "Stop putting your AI agent's memory inside the LLM context window"
URL: https://www.reddit.com/r/AI_Agents/comments/1u1hmjq/

Key points:
- Durable state MUST live outside agent in transactional DB (Postgres, files)
- Agent reads on boot, writes on tool execution — NOT the database
- Use deterministic control flow for safety (Python/state graph), not prompts
- Treat LLM as judgement layer only (processing unstructured inputs)
- Moving state to dedicated DB enables pause/replay/unit-test of agent execution

### TDS — "A Practical Guide to Memory for Autonomous LLM Agents"
URL: https://towardsdatascience.com/a-practical-guide-to-memory-for-autonomous-llm-agents

Key findings from arxiv 2603.07670:
- "Gap between has memory and does not have memory > gap between different LLM backbones"
- Write-Manage-Read loop — most agents neglect MANAGE
- Four temporal scopes:
  1. Working memory = context window (ephemeral, high-bandwidth, limited)
  2. Episodic = concrete experiences, what happened when (daily logs)
  3. Semantic = distilled facts and relationships (learnings.md)
  4. Procedural = how to do things (skills/)

### Anthropic — Effective Context Engineering
URL: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

- Memory tool in public beta on Claude Developer Platform
- File-based system for storing outside context window
- Context management = tool result clearing

### Mem0 — State of AI Agent Memory 2026
URL: https://mem0.ai/blog/state-of-ai-agent-memory-2026

- Six open problems: temporal abstraction, cross-session structure, application-level evaluation, privacy/consent, cross-session identity resolution, memory staleness
- Has Hermes agent tutorial for adding session-persistent memory
