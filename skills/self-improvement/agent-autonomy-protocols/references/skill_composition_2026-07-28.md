# Skill Composition Patterns Reference — Session 2026-07-28

## Overview
Implementation of DIRECTIVE 0x0F (SKILL_COMPOSITION) and 0x12 (AUTO_SKILL_COMPOSITION). Dynamically assembles agents from multiple skills at runtime.

## Architecture

### SkillComposer (`scripts/skill_composer.py`)
Discovers skills, matches them to tasks, and composes unified agents.

#### SkillSpec Dataclass
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

#### ComposedAgent Dataclass
```python
@dataclass
class ComposedAgent:
    name: str
    skills: List[SkillSpec]
    combined_triggers: List[str]
    combined_tools: List[str]
    description: str
    system_prompt: str
```

#### Key Methods
```python
composer = SkillComposer()

# Auto-discover skills from skills/ directory
skills = composer.find_skills_for_task("analyze youtube videos and write reports")
# Returns top 3 matching skills by trigger/keyword overlap

# Compose agent from specific skills
agent = composer.compose_agent(
    name="video_intelligence_agent",
    task="process youtube videos, extract concepts, research related topics, generate report",
    skills=[youtube_research, omh_deep_research, youtube_channel_monitor]
)

# Save agent spec + system prompt
agent_file = composer.save_composed_agent(agent)
# Creates: cache/composed_agents/video_intelligence_agent.json
# Creates: cache/composed_agents/video_intelligence_agent_prompt.md
```

### Skill Matching Algorithm
1. **Trigger matching** (weight: 2) — exact trigger phrase in task
2. **Keyword overlap** (weight: 1) — description words in task (len > 3)
3. **Sort by score desc**, return top N (default 3)

### Composed Agent System Prompt Structure
```
You are a COMPOSED AGENT: {name}
Task: {task}

Your component skills:
### Skill 1: {name} ({category})
Purpose: {description}
Triggers: {triggers}
Tools: {tools}
Path: {path}

### Skill 2: {name} ({category})
...

EXECUTION RULES:
1. You have ALL tools from all component skills
2. Route sub-tasks to the most relevant skill internally
3. Maintain unified context across all skills
4. Output final result as single coherent response
5. Log which skill handled each sub-task for traceability
```

## Test Results

| Composed Agent | Skills Combined | Purpose |
|---|---|---|
| video_intelligence_agent | youtube-research, omh-deep-research, youtube-channel-monitor | Video → concepts → research → monitor |
| content_pipeline | youtube-research, youtube-content, video-learner, omh-deep-research | Research → content → video → publish |
| competitive_intelligence_agent | youtube-research, youtube-content, video-learner, omh-deep-research | Video analysis + deep research |

## Auto-Composition via PatternMerger (DIRECTIVE 0x12)

### PatternMerger (`scripts/autonomy/pattern_merger.py`)
Merges winning tactical exceptions into new global patterns, then auto-generates composed skills.

```python
pm = PatternMerger(tactical_buffer, strategic_db)

# Check if tactical has won 5x consecutively for a param
result = pm.check_and_merge("param_name")
# If merged: returns new strategic pattern with superseded_by link
```

### Auto-Skill Generation Flow
```
Tactical Buffer (hypotheses)
    → 5 consecutive wins for same param
    → PatternMerger merges → new StrategicPattern (vN+1)
    → SkillComposer creates composed agent from related skills
    → New skill saved to skills/auto-generated/
    → Registered in skill index
```

### Skill Composition Triggers
- **Manual**: User requests composed agent for task
- **Automatic**: PatternMerger detects 5+ exception wins
- **Scheduled**: Cron job scans tactical buffer for promotion candidates

## Cache Storage
- Composed agents: `cache/composed_agents/{name}.json`
- System prompts: `cache/composed_agents/{name}_prompt.md`
- Skill index: rebuilt by `skill_indexer.py`

## Known Issues
1. Tools list empty in SkillSpec (frontmatter parsing needs improvement)
2. No validation of composed agent system prompt length (can exceed context)
3. No automatic conflict resolution between skill tool requirements
4. Auto-generated skills not yet persisted to skills/ directory

## Files
- `scripts/skill_composer.py` — SkillComposer class
- `cache/composed_agents/*.json` — Composed agent specs
- `cache/composed_agents/*_prompt.md` — System prompts

## Integration Points
- **Tactical Buffer**: Source of promotion candidates
- **Strategic DB**: Target for merged patterns
- **PatternMerger**: Trigger for auto-composition
- **CLIOrchestrator**: Runs composed agents in pipelines