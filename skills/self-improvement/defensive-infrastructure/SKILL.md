---
name: defensive-infrastructure
description: "Cross-platform defensive infrastructure modules — eliminates filesystem bugs, tool missing errors, subprocess hangs, and Windows blindness. Provides: atomic I/O, tool registry with fallback chains, process management with heartbeat/timeouts, platform abstractions."
version: "1.0.0"
author: "Hermes Agent"
tags:
  - defensive-programming
  - cross-platform
  - reliability
  - atomic-io
  - tool-registry
  - process-management
  - platform-abstraction
action_type: assist
output_type: skill
triggers:
  - defensive infrastructure
  - atomic file operations
  - tool registry
  - process manager
  - platform utils
  - cross-platform reliability
  - windows path bugs
  - subprocess timeout
related_skills:
  - agent-autonomy-protocols
  - self-improving-skills
  - system-remediation-protocol
---

# Defensive Infrastructure — Class-Level Reliability Patterns

## Overview

This skill captures the **defensive infrastructure modules** created to eliminate recurring classes of bugs:
- Filesystem/path management failures
- External tool dependency failures
- Subprocess timeout/hang/cleanup failures
- Windows-specific path/shell/process blindness

These are **class-level** patterns — not one-off fixes. Every Hermes agent session should have these available.

## Modules (in `scripts/`)

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `fs_utils.py` | Atomic, safe, cross-platform file I/O | `ensure_dir`, `safe_write_text`, `safe_read_text`, `atomic_write`, `atomic_json_update`, `file_lock`, `resolve_path`, `safe_write_json`, `safe_read_json` |
| `tool_registry.py` | Tool discovery, validation, fallback chains | `ToolRegistry`, `ToolSpec`, `ToolInfo`, `check_tool`, `require_tool`, `run_tool`, `run_with_fallback`, `get_tool_registry` |
| `process_manager.py` | Managed subprocesses with heartbeat/timeout | `ProcessManager`, `ProcessConfig`, `ProcessInfo`, `ProcessState`, `run_command`, `get_process_manager` |
| `platform_utils.py` | Cross-platform abstractions | `get_platform`, `is_windows`, `run_command`, `kill_process`, `get_memory_info`, `get_disk_usage`, `get_config_dir`, `get_cache_dir`, `which`, `find_executable` |
| `design_reference_collector.py` | External design source scanning | `DesignReferenceCollector`, source configs |
| `design_analyzer.py` | Pattern/component extraction from references | `DesignAnalyzer`, pattern extraction |
| `design_skill_generator.py` | Dynamic skill composition from patterns | `DesignSkillGenerator`, pattern→skill pipeline |
| `design_evaluator.py` | Automated quality gates (Lighthouse, axe, ESLint, W3C) | `DesignEvaluator`, quality thresholds |
| `design_critic.py` | LLM-based deep critique | `DesignCritic`, visual quality, trend alignment |
| `design_feedback.py` | Feedback loop: auto scores → pattern promotion | `DesignFeedback`, A/B, user ratings |
| `design_redesign.py` | Full pipeline: analysis → research → adaptation → generation → QC → handoff | `DesignRedesignPipeline` |

## Design Learning Infrastructure (added 2026-07-28)

**Design Skills Created (6):**
- `design-research` — external source scanning via external_import
- `design-adaptation` — PatternAdapter for brand tokens
- `design-code-generator` — HTML/CSS/JS from patterns + tokens
- `design-quality-check` — Lighthouse ≥80, axe ≥90, W3C=0, custom ≥70
- `design-feedback` — auto scores, user ratings, A/B → pattern promotion
- `design-redesign` — full pipeline: analysis → research → adaptation → generation → QC → critique → handoff

**Quality Thresholds:**
| Metric | Threshold |
|--------|-----------|
| Lighthouse Performance | ≥80 |
| Lighthouse Accessibility | ≥90 |
| Lighthouse Best Practices | ≥85 |
| Lighthouse SEO | ≥80 |
| axe-core Score | ≥90 |
| W3C Errors | 0 |
| ESLint Errors | 0 |
| Custom Design Checks | ≥70 |

**Promotion Pipeline:** Tactical Buffer (TTL 14d) → 3 successful uses + 80% score → Strategic DB (versioned)

## Usage Patterns

### Atomic File Operations (eliminates partial writes, corruption)
```python
from scripts.fs_utils import atomic_write, atomic_json_update, file_lock, ensure_dir

ensure_dir(Path("output"))
atomic_write(Path("output/data.txt"), lambda p: p.write_text("content"))
atomic_json_update(Path("config.json"), lambda d: {**d, "new_key": "value"})

with file_lock(Path("config.json")) as f:
    json.dump(data, f)
```

### Tool Registry (eliminates "command not found", version mismatches)
```python
from scripts.tool_registry import get_tool_registry, require_tool, run_tool

registry = get_tool_registry()
registry.check_all(force=True)  # Pre-flight check

info = require_tool("yt-dlp")  # Raises if missing
code, out, err = run_tool("yt-dlp", ["--dump-json", url])

# Fallback chain
code, out, err = registry.run_with_fallback("yt-dlp", "curl", args)
```

### Process Manager (eliminates hangs, zombies, cleanup failures)
```python
from scripts.process_manager import get_process_manager, ProcessConfig

mgr = get_process_manager()
config = ProcessConfig(command=["python", "script.py"], timeout=30, restart_on_failure=True)
pid = mgr.start_process(config)
info = mgr.wait_for_process(pid, timeout=60)

# Or simple one-shot
code, out, err = run_command(["python", "script.py"], timeout=30)
```

### Platform Utils (eliminates Windows blindness)
```python
from scripts.platform_utils import get_platform, is_windows, run_command, get_config_dir, get_cache_dir, which, find_executable

if is_windows():
    # Use platform-appropriate paths
    config = get_config_dir("myapp")
    cache = get_cache_dir("myapp")

code, out, err = run_command(["python", "-c", "print('hello')"])
```

## Integration with Autonomy Protocols

These modules implement **DIRECTIVE 0x16 (PERSISTENT_STATE_CHECKPOINTING)** and support:
- `state_persistence.py` — checkpointing uses `fs_utils.atomic_write`
- `youtube_pipeline.py` — uses `tool_registry` for yt-dlp, `process_manager` for subprocesses
- `design_evaluator.py` — uses `tool_registry` for lighthouse/axe/eslint, `platform_utils` for paths

## Quality Gates

| Module | Test Coverage | Known Limitations |
|--------|---------------|-------------------|
| `fs_utils.py` | Basic ops tested | Windows file locking uses exclusive-create (no fcntl) |
| `tool_registry.py` | Tool check tests | Cache TTL 1hr; manual `force=True` for fresh check |
| `process_manager.py` | Timeout/restart tests | No direct Popen access for kill; marks state only |
| `platform_utils.py` | Cross-platform tests | `psutil` optional for memory/disk; falls back gracefully |

## When to Use

**Always** — these are infrastructure. Load at session start or when:
- Writing any file → `fs_utils`
- Calling external tool → `tool_registry.check_tool` first
- Running subprocess → `process_manager` or `platform_utils.run_command`
- Handling paths → `platform_utils` or `fs_utils.resolve_path`

## Pitfalls Avoided

| Pitfall | Before | After |
|---------|--------|-------|
| Partial JSON write corrupts config | `json.dump()` directly | `atomic_json_update()` |
| `yt-dlp` not found → crash | Direct `subprocess.run()` | `require_tool("yt-dlp")` + fallback |
| Subprocess hangs forever | `subprocess.run(timeout=...)` | `ProcessManager` with heartbeat + kill |
| `os.chdir()` breaks other threads | Manual `os.chdir()` | `platform_utils.run_command(cwd=...)` |
| Windows `taskkill` fails silently | Raw `taskkill` call | `platform_utils.kill_process_tree()` |
| Temp files left behind | Manual `tempfile` | `fs_utils` atomic writes auto-clean |

## Extension Points

To add a new defensive module:
1. Create `scripts/<module>.py` with clear exports
2. Add to this skill's `references/` as `<module>.md`
3. Update `tool_registry.py` if it wraps external tools
4. Update `process_manager.py` if it manages new process types
5. Document in this skill's SKILL.md