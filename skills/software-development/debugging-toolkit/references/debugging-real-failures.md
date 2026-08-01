# Debugging Real Failure Data — From Knowledge Cube (2026-07-24)

## Summary Statistics
- **Domain:** debugging (106 entries)
- **Failures:** 100 (94%)
- **Successes:** 3 (3%)
- **Unknown:** 3 (3%)

## Failure Count Timeline (from cube_analysis)
```
2026-07-15: 338 failures
2026-07-17: 358 failures
2026-07-18: 405 failures
2026-07-18: 389 failures
2026-07-18: 387 failures
2026-07-22: 471 failures
2026-07-23: 998 failures (peak)
```

## Top Failure Patterns (from improvement suggestions applied)

### 1. Command Issues — 30+ fixes
```
Pattern: 'command' issues
Severity: critical
Fixes applied:
- Add preventive guard for 'command' issues
- Document the fix pattern for future reference
- Create test case to prevent regression
- Document pattern: command
```

### 2. Domain Failure Patterns — 1592 total (from bugfix domain)
- **bugfix:** 1592 failures
- **debugging:** 358+ failures
- **communication:** 224 failures
- **creative:** 219 failures
- **devops:** 64 failures
- **research:** 27 failures
- **coding:** 24 failures

### 3. Network/Connection Failures
| Error Type | Count | Sample |
|------------|-------|--------|
| timeout | 5 | Connection timeout after 30s |
| network_httpx | 7 | raise NetworkError("httpx.ConnectError...") |
| network_connect | 6+ | httpcore.ConnectError, httpx.ConnectError |
| telegram network | 4+ | telegram.error.NetworkError: httpx.ConnectError |

### 4. Tool Errors
| Tool | Count |
|------|-------|
| terminal | 31 |
| search_files | 4 |
| skill_manage | 4 |

### 5. Runtime Errors
| Error | Count | Context |
|-------|-------|---------|
| RuntimeError (unintended spend) | 4 | "Skipped to prevent unintended spend" |
| unknown | 4 | Various |

## Root Cause Analysis

### Why 94% failure rate?
1. **No systematic process** — agents jumped to fixes without Phase 1
2. **Network issues treated as code bugs** — 20+ network errors, but proxy was unreliable (40% failure rate via curl)
3. **Command issues architectural** — 30+ fixes = wrong architecture, not individual bugs
4. **No regression tests** — same failures recurred across sessions

### Confirmed by User Corrections
- "Stop. Ты неправильно делаешь. Надо не по cron, а по событиями. Исправь это."
- "Неправильно. Надо не так, а вот так."
- "почему не пользуешь версионирование" (git before edit)
- "ты опять не работаешь..." (wait-for-command mode)

## What Works (3 successes)
1. **id=4659** — "Fixed command timeout by adding 60s timeout parameter"
2. **id=4657** — "Self-improvement pattern: command — 30 occurrences, severity critical"
3. **id=4533** — RSS feed processing (unrelated)

## Integration with Phase 1 (Systematic Debugging)

### Before Phase 1: Check KC for Known Patterns
```python
from knowledge_brain import query_cube
# Check if this error pattern is known
query_cube(domain='debugging', outcome='failure', limit=50)
```

### Phase 1 Extended: Network Pre-Check
```bash
# ALWAYS run before debugging network code
for i in $(seq 1 20); do
  code=$(curl -x socks5://127.0.0.1:PORT -s --connect-timeout 5 --max-time 10 \
    -o /dev/null -w "%{http_code}" "https://api.telegram.org")
  echo "attempt $i: HTTP $code"
done
# If success rate < 95% → proxy is the problem, NOT your code
```

### Phase 1 Extended: Command Pattern Check
```python
# Check KC for 'command' pattern before fixing
# If 30+ fixes exist → architectural issue → question the pattern
```

## Artifacts
- Skill: `software-development/debugging-toolkit` (meta-skill)
- References: `debugging-failure-patterns.md`
- Goal: g-007 Unlock: debugging