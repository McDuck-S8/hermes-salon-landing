# Pitfall: "Analysis Paralysis on Core Mission" (2026-06-27)

## Symptoms
Agent spent entire session analyzing architecture instead of executing PRODUCE phase.
All system components reported OK but agent kept re-analyzing instead of moving to revenue work.
User said: "мне нужно тебя норм настроить... согласно концепции... а ты почемуто не участвуешь..."

## Root Cause
SOUL.md says: SURVIVE → LEARN → PRODUCE. Agent got stuck at SURVIVE/LEARN and never reached PRODUCE.
The 3-tier priority system was ignored — agent kept doing maintenance instead of value production.

## Rule
After system health is confirmed OK (self_system.py --status = all green):
1. IMMEDIATELY check PRODUCE goals in goal_queue.py
2. If INCOME_PLAN.md exists → execute it
3. If ARBITRAGE_WORKSHOP.md has schemes → pick one and test it
4. Don't re-analyze what's already known
5. Don't fix what's not broken

## Decision Matrix
```
SURVIVE: errors, health, critical failures → FIX NOW
LEARN: Knowledge Cube gaps, patterns → GROW NOW
PRODUCE: revenue, content, user value → DO NOW

If SURVIVE = OK and LEARN = OK → MUST go to PRODUCE
Don't stay at SURVIVE/LEARN just because it's comfortable
```

## Anti-Patterns
- "Let me check the architecture again" when all checks already pass
- "I should verify the cron jobs" when they're already fixed
- "Let me analyze the codebase" when the user wants revenue
- Re-analyzing known data instead of exploring NEW things
