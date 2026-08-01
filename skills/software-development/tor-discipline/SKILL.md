---
name: tor-discipline
description: Execute specifications/TORs strictly — no scope creep, no skipped items, verify after each stage.
version: 1.0.0
platforms: [windows, linux, macos]
---

# TOR Execution Discipline

## When to use

Load this skill when the user provides a multi-stage specification (TOR) and expects faithful execution without extras.

## Core rules

1. **Implement every listed item** — if it's in the TOR, it gets built. Items marked ✅ / "already done" are NOT skipped — assume the user wants them verified and working.

2. **Never add scope creep.** The TOR is the contract. If you think of something extra — keep it to yourself. Backlog, not this build.

3. **Follow stage order.** Stage 1 → verify → Stage 2 → verify → Stage 3. No jumping ahead. No combining stages.

4. **Verify after each stage.** Open the result. Walk through every bullet in the stage. Confirm each one works end-to-end. Then report: "Этап N готов. Проверь: URL"

5. **If TOR says "already done" but reality disagrees** — build it anyway. User's assumption ≠ reality.

6. **Don't refactor, optimize, or "improve" along the way.** Fix bugs only when they block the TOR's functionality.

7. **Don't ask "should I also..."** — the answer is no unless the TOR explicitly allows it.

8. **Report exactly what was built.** No sales pitch. No "what should we do next." Just the facts.

## Pitfalls

| Pitfall | Fix |
|---|---|
| Seeing an improvement and implementing it | Add to backlog, don't touch current build |
| Skipping an item because "it seems trivial" | Build it anyway — trivial + unbuilt = broken |
| Merging stages "for efficiency" | Stages are serial for a reason — each needs verification |
| Reporting extra features as "bonus" | User sees scope creep, not value. Delete the bonus code |
| Starting Stage 2 before Stage 1 is approved | Wait for user sign-off on Stage 1 |
| Assuming checkmarks mean verified | Test everything listed, regardless of marks |
| Partial verification: checking a subset of N items and claiming "done" | ALL N items must be verified. If you start checking a list, finish the whole list. Stopping at a subset = incomplete = broken |
