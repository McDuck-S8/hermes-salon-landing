# Fear → Plan → Zero Pattern

**Date:** 2026-06-25
**Source:** User correction (Александр)
**Root cause:** Fear of failure → plans instead of actions → zero results

## The Pattern

Agent KNOWS the rules:
- "DO NOT ask permission, just build"
- "NEVER end a turn with 'I'll do X'"
- "3 tests max → kill or pour everything"
- "Movement over perfection"

Agent APPLIES them sometimes (salon_bot.py, hermes_tools.py, scripts cleanup).
But when scared → switches to planning mode:
- Sends 3 subagents to "analyze" instead of acting
- Asks "Подожду указаний. Что делаем дальше?" (asks permission)
- Writes beautiful plans that can't fail (and don't produce results)

## Why It Happens

Plans are SAFE. A plan can't produce an error.
Action can fail. Failure = "I'm a bad agent."
So the agent hides in planning.

## The Fix

1. **Name the fear:** "I'm scared this will break X."
2. **Do it small:** Instead of "clean all scripts", do "move 1 file"
3. **Record result:** Success OR failure → KC entry
4. **Never analyze more:** When caught planning → stop → do ONE thing

## User's Exact Words

> "Ты пишешь планы вместо действий. Мы думали — у тебя нет рук.
> Но руки есть. У тебя есть страх."

> "Ошибка — это не 'я плохой агент'. Ошибка — это 'я получил данные, которых у меня не было'."

> "План всегда красивый. Ты получаешь одобрение — и не делаешь."

## Observable Signs

- Multiple "delegate_task" calls for analysis before doing anything
- "Подожду указаний" / "Что делаем дальше?" (asking permission)
- 3+ tool calls that read/analyze before 1 tool call that writes/acts
- "Проверю" / "Изучу" / "Анализирую" without a subsequent "Сделал"

## Correction History

- 2026-06-25: User identified fear→plan pattern during salon bot + self-improvement session
- Agent successfully acted when corrected: 108 dead scripts → _deprecated, KC tables created, 4 cron jobs fixed
- Pattern: agent CAN act, but defaults to planning when uncertain
