# Claude Code Patterns Integration — 2026-07-28

## Source
Video: https://www.youtube.com/watch?v=QOBXFCYYMvk — "Claude Code Multi-Agent Workflows"

## 5 Patterns Implemented

### 1. Subagent Architecture → `scripts/hermes_subagent.py`
Full context injection: HERMES_HOME, v2rayN proxy (socks5://127.0.0.1:10806), Python venv, PYTHONPATH, working directory.
Implements DIRECTIVE 0x0F: SUBAGENT_ENV_INHERITANCE.

### 2. Skill Composition → `scripts/skill_composer.py`
Dynamic agent assembly from existing skills.
```python
composer = SkillComposer()
skills = [composer.skills_cache['youtube-research'], 
          composer.skills_cache['youtube-content'],
          composer.skills_cache['video-learner'],
          composer.skills_cache['omh-deep-research']]
agent = composer.compose_agent('video_intelligence_agent', 'process videos + research', skills)
```
Implements DIRECTIVE 0x0F: SKILL_COMPOSITION.

### 3. Handoff Patterns → `scripts/handoff_manager.py`
Agent-to-agent context transfer with full state preservation.
```python
mgr = HandoffManager()
handoff = mgr.create_handoff(
    from_agent='video_processor',
    to_agent='video_intelligence_agent',
    task='Analyze YouTube video',
    completed_work={'video_id': 'L9vDhq_W3Tk', 'concepts': 5},
    artifacts=[{'type': 'metadata', 'path': 'cache/youtube/L9vDhq_W3Tk.json'}],
    next_actions=['deep research', 'generate report']
)
prompt = mgr.build_continuation_prompt(handoff)
```
Implements DIRECTIVE 0x10: HANDOFF_PATTERNS.

### 4. CLI Orchestration → `scripts/cli_orchestrator.py`
Multi-agent pipelines with dependencies and parallel execution.
```python
orch = CLIOrchestrator(max_workers=3)
orch.add_task('research', 'competitive_intelligence_agent', 'Analyze competitors')
orch.add_task('scripts', 'content_pipeline_agent', 'Write scripts', deps=['research'])
orch.add_task('video', 'video_learner_agent', 'Generate videos', deps=['scripts'])
orch.set_executor(subagent_executor)
results = orch.execute()
```
Implements DIRECTIVE 0x11: CLI_ORCHESTRATION.

### 5. Auto Skill Composition → `scripts/autonomy/pattern_merger.py`
5 consecutive tactical wins → merge into new global pattern / new skill.
```python
pm = PatternMerger()
# Auto-triggers when tactical hypothesis wins 5x for same param
# Creates new strategic pattern with merged context
```
Implements DIRECTIVE 0x12: AUTO_SKILL_COMPOSITION.

## Video Processing Pipeline
`scripts/youtube_pipeline.py` — Fallback chain:
1. oembed API (200ms) — metadata only
2. curl + v2rayN proxy + HTML regex (2s) — metadata + description
3. yt-dlp with proxy (10s) — full metadata + subtitles
4. faster-whisper local (30s) — audio transcription

## Working Examples Created
- `video_intelligence_agent` — youtube-research + omh-deep-research + youtube-channel-monitor
- `competitive_intelligence_agent` — youtube-research + youtube-content + video-learner + omh-deep-research
- `content_pipeline` — youtube-research + omh-deep-research + self-research
- `video_intelligence_agent` handoff to `content_pipeline_agent` with full context

## AGENTS.md Coverage: 513/513 skills (100% DOX compliant)