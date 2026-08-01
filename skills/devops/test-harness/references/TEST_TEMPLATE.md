# TESTS Template

Define what "done" looks like. Every test must be:
- **Automated** (runnable without human intervention)
- **Deterministic** (same input = same result)
- **Measurable** (pass/fail with clear threshold)

```markdown
# TESTS: <Title matching SPEC>

## Test Suite
tests:
  - name: "<descriptive name>"
    type: <code_pattern | py_compile | pytest | integration | behavioral | performance>
    file: "<path to file being tested>"  # optional
    pattern: "<regex or string to search>"  # for code_pattern
    script: "<path to test script>"  # for integration
    threshold: "<measurable threshold>"  # e.g. ">99%", "<500ms", "0 errors"
    condition: "<natural language condition>"  # for behavioral
    timeout: <seconds>  # optional, default 30
    depends_on: ["<other test name>"]  # optional, for ordering
```

## Test Types

| Type | When to Use | Example |
|------|-------------|---------|
| `code_pattern` | Verify specific code exists | `keepalive_expiry=0` in adapter.py |
| `py_compile` | Python syntax validation | Any .py file |
| `pytest` | Unit/integration tests | `tests/unit/test_adapter.py` |
| `integration` | End-to-end flow | `scripts/simulate_24h_uptime.py` |
| `behavioral` | Observable behavior | "auto-recovery within 30s" |
| `performance` | Latency/throughput | "<500ms p99 latency" |

## Example (Filled)

```markdown
# TESTS: Fix proxy intermittent failures

## Test Suite
tests:
  - name: "keepalive_expiry set to 0"
    type: code_pattern
    file: hermes-agent/plugins/platforms/telegram/adapter.py
    pattern: "keepalive_expiry=0"
    timeout: 5

  - name: "syntax valid"
    type: py_compile
    file: hermes-agent/plugins/platforms/telegram/adapter.py
    timeout: 10

  - name: "24h uptime simulation"
    type: integration
    script: tests/simulate_24h_uptime.py
    threshold: ">99% success rate"
    timeout: 300

  - name: "no manual restart needed"
    type: behavioral
    condition: "auto-recovery within 30s of proxy drop"
    timeout: 60

  - name: "message burst delivery"
    type: integration
    script: tests/message_burst_test.py
    threshold: "100% delivery, <2s latency p99"
    timeout: 120
    depends_on: ["keepalive_expiry set to 0"]
```

## Test Design Principles

1. **One test, one assertion** — each test validates one thing
2. **Fast feedback** — unit tests <10s, integration <5min
3. **Independent** — tests don't depend on each other's state
4. **Readable names** — name describes what is being verified
4. **Thresholds are measurable** — ">99%", "<500ms", "0 errors"
5. **Dependencies explicit** — `depends_on` for ordering