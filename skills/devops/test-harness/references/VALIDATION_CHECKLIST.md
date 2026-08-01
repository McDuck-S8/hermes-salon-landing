# Validation Checklist

Every fix/feature must pass ALL applicable gates before DELIVER.

## Universal Gates (Every Fix)

- [ ] **SPEC exists** — SPEC.md written before any code
- [ ] **TESTS defined** — TESTS.md written before GENERATE
- [ ] **Syntax valid** — `py_compile` passes for Python files
- [ ] **No hardcoded secrets** — Exfiltration guard passes
- [ ] **KC entry ready** — Structured data for Knowledge Cube

## Code Quality Gates

- [ ] **Type hints** — Functions have type hints (if Python)
- [ ] **Docstrings** — Public functions have docstrings
- [ ] **Error handling** — Try/except with specific exceptions
- [ ] **Logging** — Structured logs with timestamps
- [ ] **Config via env** — No hardcoded paths/tokens

## Test Gates

- [ ] **Unit tests pass** — `pytest` on relevant test files
- [ ] **Integration tests pass** — End-to-end flow verified
- [ ] **Edge cases covered** — Empty input, timeout, network failure
- [ ] **Performance threshold** — Latency/memory within limits

## Integration Gates

- [ ] **DB connectivity** — If touches database, quick_check passes
- [ ] **Health endpoints** — If service, /health returns 200
- [ ] **Event emission** — If event-driven, emits correct events
- [ ] **Skill registration** — If new skill, auto-discovered at boot

## Documentation Gates

- [ ] **Revisit line updated** — File has `> Revisit: ... Last touched: YYYY-MM-DD.`
- [ ] **DECISION_LOG.md** — Entry added with rationale
- [ ] **Skill updated** — If pattern discovered, skill patched
- [ ] **expiry.md synced** — Run `sync_expiry.py` after changes

## DELIVER Gate (All Above Must Pass)

Only when ALL applicable gates pass:
1. Write KC entry with verification proof
2. Update DECISION_LOG.md
3. Update skill if pattern discovered
4. Sync expiry.md
5. Tag in git (optional)

## Escalation Gates

If ANY gate fails after MAX_LOOPS:
- [ ] Alert sent to human (Telegram)
- [ ] Failure recorded in ALERTS.md
- [ ] Rollback plan executed if deployed
- [ ] Root cause analysis scheduled