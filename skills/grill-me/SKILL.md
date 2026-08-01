---
domain: self-improvement
trigger: When user gives a vague or multi-part task, or says "изучи", "разберись", "сделай"
---

# Grill Me — Agent-Led Task Clarification (Matt Pocock pattern)

Before touching any code or producing a report, run this 5-question grill.

## The 5 Questions

1. **Goal** — What exactly should be true when this is done? One sentence.
2. **Constraint** — What must NOT change / break?
3. **Scope** — Is this a) research only, b) code + test, c) produce artifact, d) fix something?
4. **Evidence** — How will we know it worked? (URL, screenshot, test pass, user confirms)
5. **Priority** — Is this blocking something else? Deadline?

## When to Skip

- User already gave a clear single-file task ("почини карусель")
- User gave explicit step-by-step instructions
- User is clearly frustrated and wants action, not more questions

## Output Format

Save the answers as a structured comment in the first artifact file:
```python
# GRILL: goal="..." constraint="..." scope="..." evidence="..." priority="..."
```

Or if no artifact (pure research), print:
```
[GRILL] goal: ... | evidence: ...
```

## Integration

This replaces the current "wait-for-clarification" reflex. Instead of guessing or asking open-ended "what do you mean?", use exactly these 5 questions.

When the user says "я не буду отвечать на 5 вопросов каждый раз" — skip and just do it.
