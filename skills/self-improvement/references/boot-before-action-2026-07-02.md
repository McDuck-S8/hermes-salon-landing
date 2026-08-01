# Boot Before Action (2026-07-02)

## Rule
**First tool call in session MUST be `hermes_start.py` (or `python scripts/self_system.py --status`).** Skipping boot = starting blind.

## What boot loads
- Session context (dumps, conversations, knowledge entries)
- Active goals (55 in this session)
- User needs (20)
- Knowledge graph state (2002 nodes, 5296 edges)
- Error backlog (6 recent errors)
- Human-written context files (DECISION_LOG, ALERTS, SELF_AUDIT, agent_policies)
- Tool catalog (20892 chars)
- Reality Gate verdict
- Session manifest (7 changed files detected)
- Signal daemon
- Procedural executor (cron health)

## User Reaction
User caught agent multiple times describing actions instead of doing them because boot wasn't run first. Agent said "I'll check" but didn't actually run tools — was just describing.

## Correct Pattern
```bash
# FIRST tool call in every session:
terminal(command="cd D:/Portable_Soft/hermes && python hermes_start.py")

# OR status check:
terminal(command="cd D:/Portable_Soft/hermes && python scripts/self_system.py --status")

# THEN proceed with actual work
```

## Anti-pattern
- Saying "I'll check" / "Let me look" without running a tool
- Describing what you WOULD do instead of doing it
- Asking user what to do next instead of booting and seeing what the system says

## Why it matters
Without boot:
- No active goals loaded → agent doesn't know priorities
- No context → agent asks stupid questions
- No error backlog → agent repeats known failures
- No tool catalog → agent uses wrong tools
- Reality Gate not run → agent trusts stale state