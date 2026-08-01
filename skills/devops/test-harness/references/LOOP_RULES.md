# Loop Rules

Rules governing the LOOP phase of the Test Harness cycle.

## Loop Limits

| Parameter | Default | Env Override | Description |
|-----------|---------|--------------|-------------|
| Max loops | 3 | `HERMES_TEST_HARNESS_MAX_LOOPS` | Hard limit on GENERATE → VALIDATE cycles |
| Timeout per loop | 300s | `HERMES_TEST_HARNESS_TIMEOUT` | Max seconds per validation run |
| Escalation after | Max loops reached | — | Alert human, record in ALERTS.md |

## Loop Trigger Conditions

A loop iteration occurs when **validation fails** (any test fails).

## Loop Behavior

### On Each Loop Iteration:
1. **Record failure** — capture which tests failed, error messages, stack traces
2. **Analyze failure** — categorize: syntax, logic, integration, performance, flaky
3. **Feed back to agent** — provide structured failure context:
   ```json
   {
     "failed_tests": ["test_name1", "test_name2"],
     "errors": ["error message 1", "error message 2"],
     "stack_traces": ["...", "..."],
     "loop": 2,
     "previous_attempts": [
       {"loop": 1, "fix": "added keepalive_expiry=0", "result": "timeout test still fails"}
     ]
   }
   ```
4. **Agent regenerates** — agent produces new fix/patch
5. **Re-validate** — run full test suite again

### Loop Categorization (for analytics):

| Category | Typical Fix | Max Loops |
|----------|-------------|-----------|
| `syntax` | Indentation, missing import, typo | 1 |
| `logic` | Wrong condition, off-by-one, edge case | 2-3 |
| `integration` | Missing dependency, wrong API call, config | 2-3 |
| `performance` | Timeout, memory, latency | 3 |
| `flaky` | Race condition, timing, external service | 3 (then escalate) |

## Escalation Rules

After `MAX_LOOPS` reached without verification:

1. **Alert human** — Telegram message with:
   - SPEC title
   - Target file
   - Loop history (what was tried each loop)
   - Final failure details
   - Suggested next steps

2. **Record in ALERTS.md** — structured entry:
   ```markdown
   ## ALERT: Test Harness Max Loops Exceeded
   - Spec: Fix proxy intermittent failures
   - Target: adapter.py
   - Loops: 3
   - Final failure: 24h uptime test still fails
   - Suggested: investigate network-level proxy issues
   - Timestamp: 2026-07-02 14:30
   ```

3. **Rollback if deployed** — execute rollback plan from SPEC

4. **Schedule root cause analysis** — create goal for deep investigation

## Anti-Patterns (Prevent These)

| Anti-Pattern | Prevention |
|--------------|------------|
| Same fix retried 3x | Track attempted fixes in loop history; agent must propose DIFFERENT approach each loop |
| Agent ignores test feedback | Failure context MUST include exact test failure details |
| Infinite loop on flaky test | After 3 flaky failures → mark test as flaky, escalate |
| Loop without progress | Require DIFFERENT approach each loop; same approach = escalate |

## Human Intervention Points

| Point | Action |
|-------|--------|
| Before loop 1 | Human reviews SPEC/TESTS (optional) |
| After loop 1 failure | Human can adjust TESTS if too strict |
| After loop 2 failure | Human can adjust SPEC if requirements unclear |
| After max loops | Human MUST intervene (escalation) |

## Kill Switch for Loops

```env
HERMES_TEST_HARNESS_ENABLED=true
HERMES_TEST_HARNESS_MAX_LOOPS=3
HERMES_TEST_HARNESS_TIMEOUT=300
HERMES_TEST_HARNESS_ESCALATE_ON_MAX=true  # default true
```

If `HERMES_TEST_HARNESS_ENABLED=false`:
- Harness returns immediately with `verified: true` (bypass)
- Logs warning to ALERTS.md

## Integration with Verify Fix

`verify_fix.py` is called by harness on each loop iteration.
- Returns structured result with `verified`, `checks_passed`, `checks_failed`
- Harness uses this to decide: verify → DELIVER, or fail → LOOP