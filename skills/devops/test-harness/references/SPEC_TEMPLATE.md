# SPEC Template

Use this template when starting a new fix or feature. Fill in all sections.

```markdown
# SPEC: <Title of Fix/Feature>

## Goal
<One sentence: what is the desired outcome?>

## Context
<Why is this needed? What's the current problem? Root cause if known.>

## Acceptance Criteria
- [ ] Criterion 1 (measurable)
- [ ] Criterion 2 (measurable)
- [ ] Criterion 3 (measurable)

## Scope
**In scope:**
- File(s) to modify:
- Systems affected:

**Out of scope:**
- What we're NOT changing:

## Risks
- Risk 1: mitigation
- Risk 2: mitigation

## Rollback Plan
If verification fails after deploy:
1. Step 1
2. Step 2
```

---

## Example (Filled)

```markdown
# SPEC: Fix proxy intermittent failures

## Goal
Proxy must maintain >99% uptime over 24h window without manual restarts.

## Context
Current: proxy_intermittent skill only increases timeout.
Root cause: keepalive_expiry=0 not set in adapter.py.

## Acceptance Criteria
- [ ] keepalive_expiry=0 in adapter.py
- [ ] 24h uptime simulation passes (>99% success rate)
- [ ] Auto-recovery within 30s of proxy drop
- [ ] No manual restarts needed

## Scope
**In scope:**
- hermes-agent/plugins/platforms/telegram/adapter.py
- proxy_intermittent skill in PROCEDURAL_SKILLS.md

**Out of scope:**
- Gateway restart logic (separate skill)
- Network-level proxy issues

## Risks
- Risk: adapter change breaks message delivery → mitigation: test with message burst
- Risk: keepalive_expiry=0 causes connection leaks → mitigation: monitor connection count

## Rollback Plan
1. Revert adapter.py to previous version
2. Restart gateway
3. Run 1h uptime test
```