# Skill Composition Patterns — 2026-07-28

## Dynamic Agent Assembly from Skills

### Core Concept
Instead of writing monolithic agents, compose agents dynamically from existing skills at runtime.

### Architecture
```
Skill A (youtube-research)     Skill B (youtube-content)     Skill C (video-learner)
        ↓                              ↓                              ↓
    ┌──────────────────────────────────────────────────────────────────────┐
    │                    COMPOSED AGENT: video_intelligence_agent          │
    │  - Routes sub-tasks to relevant skill internally                    │
    │  - Maintains unified context across all skills                      │
    │  - Outputs single coherent response                                  │
    └──────────────────────────────────────────────────────────────────────┘
```

### Usage
```python
from scripts.skill_composer import SkillComposer

composer = SkillComposer()

# Option 1: Auto-find skills for task
skills = composer.find_skills_for_task("process youtube videos and extract concepts")

# Option 2: Explicit skill selection
skills = [
    composer.skills_cache['youtube-research'],
    composer.skills_cache['youtube-content'], 
    composer.skills_cache['video-learner'],
    composer.skills_cache['omh-deep-research']
]

agent = composer.compose_agent('video_intelligence_agent', 'process videos + research', skills)
composer.save_composed_agent(agent)
```

### Available Skill Categories (Key)
| Category | Skills | Use For |
|----------|--------|---------|
| media | youtube-research, youtube-content, youtube-transcript, video-learner, youtube-channel-monitor | Video processing, YouTube research |
| omh-deep-research | omh-deep-research, lavra-research, self-research | Multi-phase web research |
| automation | content-pipeline, cpa-video-pipeline, rss-monitoring-cron | Content automation |
| research | research-toolkit, trend-scout, llm-wiki, blogwatcher | General research |
| self-improvement | agent-autonomy-protocols, self-improving-skills, skill-evolution | Agent evolution |

### Composition Rules
1. Max 5 skills per composed agent (cognitive load)
2. Skills must have compatible triggers (auto or matching)
3. Unified context passed to all skills
4. Skill with highest trigger match handles sub-task
5. Results aggregated by composer

### Composed Agents Created
| Agent | Skills | Purpose |
|-------|--------|---------|
| video_intelligence_agent | youtube-research, omh-deep-research, youtube-channel-monitor | Full video pipeline |
| competitive_intelligence_agent | youtube-research, youtube-content, video-learner, omh-deep-research | Competitor analysis |
| content_pipeline | youtube-research, omh-deep-research, self-research | Content creation pipeline |

### PatternMerger Integration
When tactical patterns win 5 consecutive conflicts for same parameter:
1. PatternMerger merges tactical exception into global strategic pattern
2. Creates new version of global pattern with merged context
3. Old global → archive (SUPERSEDED_BY_EXCEPTION)
4. Can trigger new skill generation if pattern is novel enough