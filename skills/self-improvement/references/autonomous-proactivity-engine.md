# Autonomous Proactivity Engine — Reference Implementation

## Overview
This document captures the implementation patterns for a fully autonomous proactivity engine in Hermes, built during the June 2026 session. The engine transforms Hermes from an "information collector" into a "knowledge generator" by closing the feedback loop: detect issues → LLM analysis → apply fixes → verify → write verified knowledge to Knowledge Cube.

## Architecture

```
┌─────────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│ proactive_executor  │────▶│ pending_analysis │────▶│ LLM Analyst Service │
│ (cron, every 15m)   │     │ .json            │     │ (cron, every 30s)  │
└─────────────────────┘     └──────────────────┘     └─────────┬──────────┘
                                                               │
                                                               ▼
┌─────────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│ Knowledge Cube      │◀────│ hermes_hooks     │◀────│ suggested_fixes    │
│ (verified=true)     │     │ on_task_complete │     │ .json              │
└─────────────────────┘     └──────────────────┘     └────────────────────┘
```

## Key Components

### 1. Proactive Executor (`scripts/proactive_executor.py`)
- **Phase 2.5 LLM Analysis**: Integrated between cron error scan and fix application
- **`analyze_with_llm()`**: Reads `suggested_fixes.json` (priority) → `llm_analysis_cache.json` (legacy) → writes `pending_analysis.json`
- **`apply_llm_suggested_fixes()`**: Returns detailed structure `{applied, verified, failed, skipped, total}`
- **`verify_fix_result()`**: Runs syntax checks + pytest for verification
- **Patch Generator**: Converts LLM descriptions to unified diffs for known patterns (indentation fixes)

### 2. LLM Analyst Service (`scripts/llm_analyst.py`)
- Polls `pending_analysis.json` every 30 seconds
- Calls **free models only** via opencode-zen with auto-rotation:
  1. nemotron-3-ultra-free
  2. deepseek-v4-flash-free
  3. mimo-v2.5-free
  4. qwen3.6-plus
  5. qwen3.5-plus
- Auto-rotates on: timeout, error, rate_limit, empty_response
- Outputs `suggested_fixes.json` with schema:
  ```json
  {
    "fix_type": "patch|command|investigation",
    "description": "What this fix does",
    "patch_or_action": "Unified diff or shell command",
    "confidence": 0.0-1.0,
    "target_file": "path/to/file.py"
  }
  ```

### 3. Configuration (`config.yaml`)
```yaml
llm_analyst:
  free_models:
    - provider: opencode
      model: nemotron-3-ultra-free
      priority: 1
    - provider: opencode
      model: deepseek-v4-flash-free
      priority: 2
    # ... etc
  auto_rotate: true
  rotate_on: ["timeout", "error", "rate_limit", "empty_response"]
  poll_interval_seconds: 30
  max_issues_per_batch: 10
```

### 4. Cron Job (`cron/llm_analyst.yaml`)
```yaml
name: llm-analyst
schedule: "30s"
script: "scripts/llm_analyst.py"
no_agent: true
model:
  provider: opencode_zen
  model: nemotron-3-ultra-free
```

## Critical Design Decisions

### Free Models Only
**User requirement**: "мы используем в системе только фри модели провайдеров!!!!"
- No OpenRouter, no paid APIs
- opencode-zen provides free tier models
- Auto-rotation essential due to rate limits on free tiers

### Information vs Knowledge
**User insight**: "инфа становится знанием когда её применяют и используют для пользы дела... без использования инфы-оно остается просто инфой"
- Knowledge Cube entries must have `verified=true` and `evidence="tests pass / deploy succeeded"`
- The loop is not closed until `on_task_complete` writes verified results back to KC

### Autonomous Operation
**User preference**: "запусти что там нужно и проверь систему на проактивность... начинай работать, запускай агентов и по плану поехали"
- No manual copy-paste commands
- Agent should execute, not just describe
- Cron jobs run autonomously

## Pitfalls & Lessons Learned

### 1. Exit Code Design
Proactive executor returns 1 when "issues found but no auto-fix possible" — this causes cron to mark job as error, creating a self-referential error loop.
**Fix**: Return 0 on successful execution (even with issues), 1 only on exceptions. Or configure cron to not treat exit 1 as error for this job.

### 2. Patch Generator Limitations
LLM often returns descriptive text instead of valid unified diffs.
**Fix**: Enhanced prompt with strict format requirements + description-to-patch generator for common patterns (indentation, missing imports, etc.)

### 3. Indentation Error Location Mismatch
LLM reported error at line 1154, actual error at line 1024.
**Fix**: Pattern matching in generator should search for the actual pattern, not trust line numbers from LLM.

### 4. Self-Healing State Persistence
Cron error scan reads `cron/jobs.json` and `cron/output/` — errors persist until manually cleared.
**Fix**: Clear `cron/self_healing_state.json` and relevant output dirs after verified fix.

### 5. opencode-zen CLI Path
`opencode` command not in PATH after npm global install.
**Fix**: Use full path `D:/npm-global/node_modules/opencode-ai/bin/opencode.exe` or add npm global bin to PATH.

## Verification Checklist
- [ ] `python -m py_compile scripts/proactive_executor.py` passes
- [ ] `python scripts/test_llm_analyst.py` generates fixes via free model
- [ ] `python scripts/proactive_executor.py` runs end-to-end, detects issues, applies/verifies fixes
- [ ] `hermes cron start llm-analyst` starts background service
- [ ] Verified fixes written to KC with `verified=true`, `evidence="..."`
- [ ] Auto-rotation works when model fails (test by temporarily blocking a model)

## Related Beads
- Epic: `hermes-xjo` — Close LLM Analysis Feedback Loop
- `hermes-xjo.1` — LLM Analyst Service
- `hermes-xjo.2` — Fix apply_llm_suggested_fixes return structure
- `hermes-xjo.3` — Post-fix verification mechanism
- `hermes-xjo.4` — Update hermes_hooks for verified knowledge capture
- `hermes-xjo.5` — Cron job for LLM Analyst

## Files Created/Modified
- `scripts/llm_analyst.py` (new)
- `scripts/test_llm_analyst.py` (test script)
- `scripts/proactive_executor.py` (enhanced: Phase 2.5, apply/verify functions)
- `config.yaml` (added llm_analyst section)
- `cron/llm_analyst.yaml` (new cron job)
- `cron/jobs.json` (updated proactive-executor status)