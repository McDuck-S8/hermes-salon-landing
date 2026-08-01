# Debugging Failure Patterns — Real Data from KC (2026-07-24)

## Domain Statistics
- **Total debugging entries:** 106
- **Failures:** 100 (94%)
- **Successes:** 3 (3%)
- **Unknown:** 3 (3%)

## Failure Timeline
| Date | Failure Count | Notes |
|------|---------------|-------|
| 2026-07-23 | 998 | Peak — cube_analysis recurring_failure |
| 2026-07-22 | 471 | cube_analysis recurring_failure |
| 2026-07-18 | 405 | cube_analysis recurring_failure |
| 2026-07-18 | 389 | cube_analysis recurring_failure |
| 2026-07-18 | 387 | cube_analysis recurring_failure |
| 2026-07-17 | 358 | cube_analysis recurring_failure |
| 2026-07-15 | 338 | cube_analysis recurring_failure |

## Root Causes Identified (from improvement suggestions)

### 1. Command Issues (most frequent)
- **Pattern:** `command` issues — 30+ fixes applied
- **Fixes:** Preventive guards, test cases, pattern documentation
- **Skill:** `systematic-debugging` → Phase 1 check

### 2. Network/Connection Errors
- **timeout:** 5 occurrences, 30s timeout
- **network_httpx:** 7 occurrences, httpx exceptions
- **network_connect:** 6+ occurrences, httpcore/httpx ConnectError
- **telegram network:** 4+ occurrences, httpx.ConnectError
- **Fix:** proxy reliability check BEFORE code changes (see systematic-debugging pitfall)

### 3. Tool Errors
- **tool_error (terminal):** 31 occurrences
- **tool_error (search_files):** 4 occurrences
- **tool_error (skill_manage):** 4 occurrences

### 4. Runtime Errors
- **unknown (RuntimeError):** 4 occurrences — "Skipped to prevent unintended spend"
- **log_analysis auto-detected** patterns

## Anti-Patterns Confirmed by Data

| Anti-Pattern | Evidence | Countermeasure in debugging-toolkit |
|--------------|----------|-------------------------------------|
| Fix without Phase 1 | 998 failures accumulated | Phase 1 mandatory in workflow |
| Multiple fixes at once | 30+ fixes for 'command' | ONE change, test, repeat |
| Skip regression test | Recurring failures | TDD: RED first |
| Guess at async bugs | Network hangs, timeouts | python-debugpy / node-inspect with breakpoints |
| "Works in CLI not TUI" | Slash command sync issues | debugging-hermes-tui-commands registry sync |

## Session Artifacts

### Debugging Skills Available
| Skill | Version | Purpose |
|-------|---------|---------|
| systematic-debugging | 1.3.0 | 4-phase methodology (patched 2026-07-24) |
| python-debugpy | 1.1.0 | pdb + debugpy/DAP |
| node-inspect-debugger | 1.1.0 | CDP for Node.js |
| debugging-hermes-tui-commands | 1.1.0 | Slash command sync |
| debugging-toolkit | 1.0.0 | Meta-skill (created 2026-07-24) |

### KC Query Used
```python
from knowledge_brain import query_cube
query_cube(domain='debugging', outcome='failure', limit=100)
```

## Lessons for Future Sessions

1. **Debugging domain = 94% failure rate** — always load debugging-toolkit FIRST for any debugging task
2. **Network issues are proxy problems, not code problems** — run curl loop (20 reqs) before touching adapter code
3. **Command issues need guards, not more fixes** — 30+ fixes = architectural pattern issue
4. **Log analysis auto-detected patterns** are already in KC — query before manual analysis
5. **Phase 1 is non-negotiable** — 998 failures prove skipping it fails