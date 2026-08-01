# Truncated Responses — 2026-06-29

## Problem
Agent cuts off responses mid-sentence / mid-thought. User sees incomplete analysis (e.g., self-audit stopped at Policy 18 of 20).

## Root Cause
- Token budget anxiety: agent tries to be "concise" and stops streaming
- No forced completion mechanism for long analytical outputs

## Fix
1. **Write long analyses to file first** via `execute_code` → `write_file`
2. **Then summarize** in response
3. **Always complete the current thought block** before ending turn
4. Use `todo` to track multi-part responses: each section = one todo item

## Example
```python
# Instead of streaming self-audit:
write_file("cache/self_audit_full.md", full_audit_text)
# Then in response: "Full audit saved. Summary: ..."
```

## Signal to Watch
If response ends without closing `---` or `###` block → FAILURE. Must complete structure.