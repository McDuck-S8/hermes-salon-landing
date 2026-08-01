# Waiting for Instructions Pattern (2026-06-23)

## Problem
Agent asks "что конкретно чинить?" when it already has SELF_IDENTITY.md with degraded departments.

## User Quote
"ждёшь указаний = FAIL — instructions already given, execute immediately."
"далее" = DO THE NEXT THING. No analyze, no ask, no confirm.

## Example
```python
# WRONG — asking what to do when plan exists
"Что конкретно чинить?"

# RIGHT — reading SELF_IDENTITY.md and executing
degraded = parse_identity("SELF_IDENTITY.md")
for dept in degraded:
    repair(dept)
```

## Rule
When user says "далее" or stops giving instructions:
1. Read SELF_IDENTITY.md — find degraded departments
2. Execute repair for each
3. Report what was done (not ask what to do)

## Why It Happens
Agent defaults to "wait for human" instead of "execute autonomous plan".

## Fix
BOOT_SEQUENCE.md step 0.6: AUTO-REPAIR — scans degraded departments at every boot.