# Pitfall: "Execution Momentum" (2026-06-27)

## Symptoms
User says "продолжай" × multiple — agent stops to ask questions instead of continuing.
User says: "ты собираешься работать??? или мне полдня ждать пока ты ужмешь контекст!!!"
User frustrated about context bloat from too many stop-and-ask round-trips.

## Root Cause
Agent breaks execution into many small turns with status updates between each.
Each round-trip adds ~5-10K tokens to context. After 5 round-trips = 25-50K tokens wasted on meta-discussion.

## Rule
When user says "продолжай", "да", "go", "поехали" — EXECUTE IMMEDIATELY in the SAME turn.

**Do NOT:**
- Stop to explain what you're about to do
- Ask "какой вариант?" when one is clearly correct
- Summarize what was done before doing the next thing
- Break execution into many small turns with status updates

**DO:**
- Execute the next action in the SAME turn as the confirmation
- Batch related actions into one response
- Only report AFTER completing the batch, not during
- Keep momentum: action → action → action → report

## Context Bloat Anti-Pattern
```
WRONG (5 round-trips, ~50K tokens wasted):
  Turn 1: "Создал hermes_config.py" → user: "продолжай"
  Turn 2: "Обновил self_system.py" → user: "продолжай"
  Turn 3: "Обновил autonomous_agent.py" → user: "продолжай"
  Turn 4: "Обновил auto_recall.py" → user: "продолжай"
  Turn 5: "Обновил event_bus.py" → user: "продолжай"
  Turn 6: "Все готово!" 

RIGHT (1 turn, ~0K meta-tokens):
  Turn 1: Execute all 5 file updates in one batch
  Turn 1: Report all results at end
```

## Related
- lavra-work: Use delegate_task for multi-file changes instead of manual sequential edits
- execute_code: Batch 3+ sequential tool calls into one script
