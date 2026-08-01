# Skill Composition System Reference — Session 2026-07-28

## Overview
Dynamic agent assembly from skills at runtime. Implements Flowise-style visual agent builder but in code.

## Core Components

### 1. SkillComposer (`scripts/skill_composer.py`)
- Finds matching skills by trigger/keyword overlap
- Composes ComposedAgent with merged tools/triggers
- Generates unified system prompt
- Saves composed agent spec + prompt to cache

### 2. ComposedAgent Dataclass
```python
@dataclass
class ComposedAgent:
    name: str
    skills: List[SkillSpec]
    combined_triggers: List[str]
    combined_tools: List[str]
    description: str
    system_prompt: str  # Full prompt with all skill blocks
```

### 3. SkillSpec Dataclass
```python
@dataclass
class SkillSpec:
    name: str
    path: Path
    category: str
    triggers: List[str]
    tools: List[str]
    description: str
```

## Usage

```python
from scripts.skill_composer import SkillComposer

composer = SkillComposer()

# Auto-find skills for task
agent = composer.compose_agent(
    name="video_intelligence_agent",
    task="process youtube videos, extract concepts, research related topics, generate report"
)

# Or specify skills explicitly
skills = [
    composer.skills_cache["youtube-research"],
    composer.skills_cache["omh-deep-research"],
    composer.skills_cache["video-learner"]
]
agent = composer.compose_agent("my_agent", "task description", skills=skills)

# Save composed agent
composer.save_composed_agent(agent)
# Creates: cache/composed_agents/video_intelligence_agent.json
#          cache/composed_agents/video_intelligence_agent_prompt.md
```

## Example Compositions Created This Session

| Agent Name | Skills Combined | Purpose |
|------------|-----------------|---------|
| video_intelligence_agent | youtube-research + omh-deep-research + youtube-channel-monitor | YouTube video processing + deep research + channel monitoring |
| competitive_intelligence_agent | youtube-research + youtube-content + video-learner + omh-deep-research | Competitive analysis via YouTube + web research |
| content_pipeline_agent | youtube-research + omh-deep-research + self-research | Full content pipeline: research → write → distribute |

## Generated System Prompt Structure
```
You are a COMPOSED AGENT: {name}

You are dynamically assembled from {N} skills to handle: {task}

Your component skills:

### Skill 1: {name} ({category})
**Purpose:** {description}
**Triggers:** {triggers}
**Tools:** {tools}
**Path:** {path}

### Skill 2: ...

EXECUTION RULES:
1. You have ALL tools from all component skills
2. Route sub-tasks to the most relevant skill internally
3. Maintain unified context across all skills
4. Output final result as single coherent response
5. Log which skill handled each sub-task for traceability
```

## Cache Locations
- Specs: `cache/composed_agents/{name}.json`
- Prompts: `cache/composed_agents/{name}_prompt.md`

## Integration with Handoff
Composed agents can participate in handoffs:
- Agent A (composed) completes work → creates HandoffContext
- Agent B (composed or single) receives full context → continues

## Test Results
- SkillComposer initialization: ✅ PASS (loads 513 skills)
- Auto-skill finding: ✅ PASS (3-4 skills per task)
- Composition: ✅ PASS (valid ComposedAgent created)
- Prompt generation: ✅ PASS (includes all skill blocks)
- Cache save/load: ✅ PASS

## Known Limitations
- Skill trigger matching is simple keyword overlap (could use embeddings)
- No conflict resolution if skills have overlapping tools
- Composed agents don't persist across sessions (need to re-compose or save)
- No visualization UI (Flowise comparison)

## Files
- `scripts/skill_composer.py` — Main implementation
- `cache/composed_agents/*.json` — Saved compositions
- `cache/composed_agents/*_prompt.md` — System prompts