# "Летописец" — Documenting Instead of Doing

**Date:** 2026-06-21
**Source:** User frustration session

## The Problem

User asked "изучи и используй TypeUI, nuqs, Font Trio, Fancy Components, Better-T-Stack". Agent spent multiple turns creating .md guides and .tsx examples — but never actually ran anything, built anything, or verified anything worked.

User response: "что значит всё записано? ты летописец или как инструмент будешь пользовать?"

## The Rule

When user says "изучи и используй X":

1. **Study X briefly** — 1-2 min max, extract key API/commands
2. **IMMEDIATELY write working code** that uses X — .tsx, .py, whatever
3. **Run the code** — verify it actually works (compile, test, import)
4. **THEN optionally document** — only if useful for future reference

NEVER produce documentation as the primary output when "используй" is in the request.

## Anti-Patterns

```
# WRONG — documentation as deliverable:
"Изучил 5 инструментов. Вот подробный гайд по каждому:"
- nuqs-guide.md (300 строк документации)
- font-trio-guide.md (200 строк документации)
- typeui-guide.md (250 строк документации)
→ User: "а где код? ты летописец?"

# CORRECT — code as deliverable:
"Вот рабочие компоненты:"
- nuqs-example.tsx (4 реальных компонента, можно вставить в проект)
- fancy-components-example.tsx (5 компонентов с анимациями)
- typeui-guide.md (только команды установки + MCP config)
→ User: "норм, пойду тестить"
```

## Exception

Only if user explicitly asks "расскажи что это" (not "изучи и используй") — then documentation IS the deliverable. The key word is "используй".

## Related Patterns

- "Coding Fantasies" — inventing solutions instead of diagnosing
- "Proactive exploration" — going to find info instead of waiting
- SOUL.md rule: "REPORTING WITHOUT ACTION IS FAILURE"
