# Execution + Feedback Loop Pattern

## Core Rule
A self-improving system that only observes and proposes is useless.
The full cycle is mandatory:
```
Observe → Analyze → Propose → Execute → Evaluate → Learn
```

## Why
Crystal v3 was broken because it had steps 1-3 but not 4-6.
It observed sessions, found patterns, proposed actions — but never applied them
or measured results. The user called this out: "где реальные ценности?"

## Implementation Pattern

### Snapshot-Before / Snapshot-After
```python
def execute_and_evaluate(proposal, executor, engine):
    before = snapshot_state(engine)    # count signals, errors, alerts
    result = executor.execute(proposal) # actually do the thing
    after = snapshot_state(engine)      # count again
    assessment = assess(before, after, result)
    save_history(proposal, result, assessment)
    return assessment
```

### Assessment Score
- Command executed successfully: +0.4
- Errors decreased: +0.3
- Dry run worked: +0.2
- Base attempt credit: +0.1
- Success threshold: >= 0.3

### History
- Keep last 100 entries
- Track: proposal_id, action, department, success, delta
- Stats: total cycles, success rate, average delta

## User Preference: Don't Ask, Just Do
User repeatedly said "МОЖЕТ УЖЕ НАЧНЕШЬ РАБОТАТЬ!!!!"
When given a clear task, execute immediately.
Never ask "do you want me to?" — resolve ambiguity with reasonable defaults.
