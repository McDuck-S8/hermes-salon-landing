# Crystal / Self-Improvement Loop — 2026-07-04

## Session Findings

### Crystal State
- **65,651 patterns** in `patterns.json` (37 MB) — major growth
- **8,869 signals** in `signals.json`
- **208 needs** in `needs.json`
- **200 proposals** in `proposals.json` (top: patch_skill for ai-core/telegram-bots, priority 1.0)
- **19 evolution entries** — learning from feedback
- **100 feedback history** entries

### Self-Improvement Loop (scripts/self_improvement_loop.py)
- **386 suggestions** this run (4 critical, 4 high, 377 medium, 1 low)
- **79.2% overall failure rate** — high, driven by `tool_error`, `unknown`, `scheduler` log patterns
- **0 skills auto-created**, **0 knowledge entries written** — loop is detecting but not executing
- **Top critical patterns:**
  - `tool_error` × 26: `terminal` tool issues
  - `unknown` × 12: ">>> selected: [survive] fix cron jobs with errors"
  - `scheduler` × 12: cron job processing errors
  - `cronjob_tools` × 11: failed to execute cron job 2f8449cdfeef

### Proactive Executor (scripts/proactive_executor.py)
- **9 issues detected**, 3 cron jobs errored:
  - `event-heartbeat`: usage error (fixed via jobs.json patch)
  - `procedural-executor`: timeout 120s (tasklist hangs)
  - `health-check`: exfiltration false positive (fixed regex)
- **17 KC gaps** (white spots): coding, research, devops, architecture, testing, security, etc. — all 0 entries
- **3 gap-filling tasks generated** for coding/research/devops
- **2 skills auto-evolved**: `automation-auto-patterns` (+7x, +5x occurrences)

## Key Insight: The Loop Is Detecting But Not Executing

The self-improvement system generates excellent diagnostics (386 suggestions) but:
- `run_proactive()` calls LLM Analyst which times out
- `run_healing()` only cleans cache, doesn't fix root causes
- `run_learning()` only searches session recall, doesn't write to KC
- No automated "apply top N fixes" phase

## Recommended Enhancement

Add an **execution phase** to `self_improvement_loop.py`:
```python
def apply_top_fixes(suggestions, max_fixes=5):
    """Auto-apply top N critical/high fixes with verification."""
    critical = [s for s in suggestions if s.severity in ('critical', 'high')][:max_fixes]
    for fix in critical:
        result = execute_fix(fix)
        verify_fix(fix, result)
        log_fix_result(fix, result)
```

## Debugging Path Used

1. `self_system.py --status` → verify system health
2. `self_system.py --analyze` → gaps/trends
3. `self_system.py --heal` → cron/cache
4. `self_improvement_loop.py --status` → full report
5. `proactive_executor.py` → cron errors + KC gaps
6. Fix root causes in `cron/jobs.json` and skills

## Files Modified This Session
- `scripts/self_system.py` — restored from git
- `cron/jobs.json` — `event-heartbeat` script fixed
- `skills/devops/exfiltration-guard/scripts/exfil_guard.py` — phone regex fixed