---
name: test-harness
description: Test Harness pattern from AI-First Business Playbook — SPEC → TESTS → GENERATE → VALIDATE → LOOP → DELIVER. Every fix/feature passes through this cycle.
---

# Test Harness — Closed-Loop Quality Enforcement

Implements the AI-First Business Playbook test harness pattern:
Every fix/feature MUST pass: SPEC → TESTS → GENERATE → VALIDATE → LOOP (max 3) → DELIVER

---

## Key Implementation Lessons (2026-07-03)

### Integration with Procedural Executor
- Created `scripts/verify_trigger.py` as separate module to avoid syntax issues in `procedural_executor.py`
- Each trigger action runs verification via `verify_trigger.py` with trigger-specific health checks
- Verification results recorded to Knowledge Cube + ALERTS.md

### Syntax Hygiene for Generated Code
- When patching Python files: remove non-ASCII (Cyrillic, arrows, em-dashes) first
- Fix unterminated triple-quoted strings (must be even count)
- Use sed for surgical fixes, not write_file for full rewrites
- Test import after every patch: `python -c "import scripts.module"`

### Test Harness as Separate Module
- `verify_trigger.py` imports `TestHarness` from `skills/devops/test-harness/scripts/harness.py`
- Fixed harness.py import: `from scripts.verify_fix` → `from verify_fix` (run from project root)
- This avoids coupling test harness into main procedural executor syntax

Every fix/feature goes through this cycle. No exceptions.

## Architecture (Implemented)

```
test-harness/
├── SKILL.md                    # This file
├── references/
│   ├── SPEC_TEMPLATE.md        # Human writes SPEC
│   ├── TEST_TEMPLATE.md        # Human defines TESTS (what "done" looks like)
│   ├── VALIDATION_CHECKLIST.md # Validation criteria
│   ├── LOOP_RULES.md           # When to loop back
│   └── example_fix_cycle.md    # Worked example
├── scripts/
│   └── harness.py              # Main orchestrator (TestHarness class)
├── templates/
│   └── TEMPLATES.md            # SPEC/TESTS/VALIDATION templates
```

## The Cycle (Mandatory for Every Fix/Feature)

### 1. SPEC (Human writes)
```markdown
# SPEC: Fix proxy intermittent failures
## Goal
Proxy must maintain >99% uptime over 24h window without manual restarts.
## Acceptance Criteria
- [ ] keepalive_expiry=0 in adapter.py
- [ ] 24h uptime test passes (>99% success rate)
- [ ] No manual restarts needed
```

### 2. TESTS (Human defines what "done" looks like)
```markdown
# TESTS: Fix proxy intermittent failures
tests:
  - name: "keepalive_expiry set to 0"
    type: code_pattern
    file: hermes-agent/plugins/platforms/telegram/adapter.py
    pattern: "keepalive_expiry=0"
  - name: "24h uptime simulation"
    type: integration
    script: tests/simulate_24h_uptime.py
    threshold: ">99% success rate"
```

### 3. GENERATE (Agent writes code)
- Agent reads SPEC + TESTS
- Produces patch/command
- Output recorded

### 4. VALIDATE (Harness runs TESTS)
- Runs all tests via `verify_fix.py`
- Records pass/fail
- If FAIL → LOOP

### 5. LOOP (Max 3 iterations)
- On failure: agent gets test failure details
- Agent fixes, re-generates
- Re-validate
- After 3 failures → escalate to human

### 6. DELIVER (Only when all tests pass)
- Write KC entry with verification proof
- Update skill if pattern discovered
- Record in DECISION_LOG.md

## Usage

```bash
# Start a new fix cycle
python skills/devops/test-harness/scripts/harness.py start --spec SPEC.md --tests TESTS.md

# Run validation on existing fix
python skills/devops/test-harness/scripts/harness.py validate --target scripts/procedural_executor.py --tests TESTS.md

# Full cycle with auto-loop
python skills/devops/test-harness/scripts/harness.py cycle --spec SPEC.md --tests TESTS.md --max-loops 3
```

## Integration Points (Implemented)

- **verify_fix.py** → calls `harness.validate()` (updated 2026-07-02)
- **procedural_executor** → triggers harness on fix attempts (trigger_gateway_dead updated 2026-07-03)
- **TestHarness class** → available at `skills/devops/test-harness/scripts/harness.py`

## Kill Switch
```env
HERMES_TEST_HARNESS_ENABLED=true  # default true
HERMES_TEST_HARNESS_MAX_LOOPS=3
HERMES_TEST_HARNESS_TIMEOUT=300
```

## Verification Gates (Non-Negotiable)
1. **SPEC exists** before any code written
2. **TESTS defined** before GENERATE
3. **All tests pass** before DELIVER
4. **KC entry written** with proof
5. **Loop counter** prevents infinite cycles

## Lessons Learned (2026-07-03)
- **Accelerated testing works** — 1h real = 24h simulated with time compression (example: proxy uptime)
- **Keepalive is critical** — `keepalive_expiry=0` prevents silent connection drops (proxy fix)
- **Two loops is typical** — first loop catches syntax/logic, second catches integration
- **Test scripts must be created** — behavioral tests need executable scripts
- **Harness enforces discipline** — no DELIVER without all tests passing
- **Integration with procedural_executor** — `verify_with_test_harness()` called after gateway restart