# Report Without Saving — 2026-06-25

## Problem
## Problem
Agent discovers useful information (new CPA offer, traffic source, tool) and reports it to user but does NOT save it to persistent storage (ARBITRAGE_WORKSHOP.md, Knowledge Cube, memory).

## Violations
- **Policy 16**: Workshop must be replenished CONSTANTLY, not on command
- **Pre-Report Checklist**: "Did I do Action A? → Did I do Action B (save)? → If NO: STOP. Save first."

## Fix
**Before ANY report to user:**
1. If discovered new brick/scheme/tool → `patch` ARBITRAGE_WORKSHOP.md
2. If learned new pattern → `memory` add or skill update
3. If found arbitrage opportunity → add to ARBITRAGE_WORKSHOP.md with math
4. Only THEN report to user

## Signal to Watch
Response contains "I found X" or "Discovered Y" but no file write tool call → VIOLATION. Save first, report second.

## Example
```python
# BAD: Report without saving
print("Found new CPA offer: Leadgid pays 30K per mortgage")

# GOOD: Save then report
patch("ARBITRAGE_WORKSHOP.md", ..., new_leadgid_entry)
print("Added Leadgid 30K offer to workshop. Details in file.")
```