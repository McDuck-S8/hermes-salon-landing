# Multi-LLM Audit Pattern

**Source:** Session 2026-06-29
**Pattern:** When debugging complex event-driven systems, get a second opinion from another LLM before fixing.

## Why

Single-LLM audit has blind spots:
- Agent built the system → blind to its own assumptions
- Agent sees code daily → stops noticing broken connections
- Fresh perspective catches structural issues the builder missed

## How

1. Run your own audit (read files, check connections, map pipeline)
2. Present findings to user
3. User brings in another LLM (DeepSeek, Claude, etc.) for second opinion
4. Cross-reference both analyses
5. Fix only issues confirmed by BOTH

## Example (2026-06-29)

Agent audit found:
- event-heartbeat wrong script ✅
- event_bus.process() hangs ✅
- signal_daemon dead ✅
- goal_executor kills goals ✅

DeepSeek audit found SAME issues +:
- Root cause: manual processes without autostart (deeper insight)
- "Why it worked yesterday" explanation (narrative clarity)

Result: 100% overlap, DeepSeek added WHY not WHAT.

## When to Use

- "Вчера работало, сегодня не работает" → multi-LLM audit
- Complex pipeline with 5+ components → multi-LLM audit
- User is frustrated → fresh perspective helps emotionally too

## Anti-patterns

- Don't ask DeepSeek to FIX — only to ANALYZE
- Don't blindly trust one LLM — always verify against actual code
- Don't run audit if you already know the exact fix — just fix it

## Files

- `references/integration-audit-methodology-2026-06-29.md` — the 10-point checklist
