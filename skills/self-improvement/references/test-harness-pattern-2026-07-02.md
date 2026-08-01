# Test Harness Pattern (from AI-First Business Playbook, 2026-07-02)

## Core Principle
Human writes SPEC + TESTS → Agent generates → Validates against tests → FAIL = loop back → PASS = deliver

## Applied to Hermes
Every fix/feature must follow:
1. **SPEC** - What needs to be built (clear, testable requirements)
2. **TESTS** - What "success" looks like (automated verification criteria)
3. **GENERATE** - Agent builds the deliverable
4. **VALIDATE** - Automated checks against tests
5. **LOOP** - If FAIL, iterate with error context. If PASS, deliver.

## Implementation in verify_fix.py
```python
# Every fix must have:
spec = "Fix proxy connection timeout"
tests = [
    "curl -x socks5://127.0.0.1:10806 -s --connect-timeout 5 https://api.telegram.org returns 200",
    "hermes gateway list shows PID",
    "netstat shows proxy on 10806"
]
# Agent generates fix → runs tests → loops until all pass
```

## Pitfall: "Works on my machine"
Tests must be runnable in clean environment. Document exact commands, expected outputs, timeout values.

## Integration with Hermes Workflow
- Before any code change: write SPEC + TESTS in cache/fix_spec.json
- After implementation: run verify_fix.py with those tests
- Only mark complete when ALL tests pass
- Archive spec + test results in DECISION_LOG.md