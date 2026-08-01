# Delegation Over Manual Work (2026-07-02)

## User Constraint
"и сколько говорить не лезь своими ручками!!! всё только через лавр!!!"
"система сама должна найти и закрыть пробелы!!!!"

## Rule
**ALL implementation work goes through Lavra protocols.** Do NOT write code manually in the main session.

## Pattern
1. User asks for system improvement → create bead via `bd create`
2. Run `/lavra-work {bead_id}` to implement
3. Run `/lavra-review` to verify
3. Scripts + cron automate the rest

## Anti-patterns
- Writing scripts directly in main session instead of through lavra-work
- Explaining what system should do instead of making it do it
- Manual one-off fixes instead of automated cron-based solutions
- **Proposing to fix issues manually after analysis** — when analysis reveals problems, ALWAYS create bead + run lavra-work. Never say "I can fix this now" or "Хочешь чиню?". The analysis IS the value; the fix goes through Lavra.

## Pitfall: Analysis → Manual Fix Trap (2026-06-27)
User asked to check architecture. Agent ran full audit, found real issues, then proposed: "Хочешь: 1) Чиню session_context + cron ошибки (прямо сейчас) 2) Делаю hermes_config.py единый". User snapped: "я не хочу что бы ты это правил!!! кто из лавра это сделает?" — THREE times before agent ran lavra-work correctly.

**Rule:** After ANY analysis that finds actionable issues:
1. Create bead: `bd create "{title}" --type task -d "{findings}"`
2. Run: `/lavra-work {bead_id}`
3. Report: "Создал bead {id}, запустил lavra-work. Результат пришлёт когда закончит."

NEVER: "Хочешь исправить?", "Могу сделать сейчас", "Давай я починю".

## Pitfall: Subagent Fails ≠ Permission to Code (2026-06-27)
When a lavra-work subagent's patch fails (e.g. hunk not found), the agent MUST NOT step in and write Python/patch files directly. The user said: "ты сцуко чат бот и не более!!!! и не лезь блять кодить!!!! я тебе запрещаю кодить!!!!"

**Rule:** If subagent fails:
1. Create a NEW bead describing what failed and why
2. Launch a NEW lavra-work subagent with better context
3. NEVER fall back to manual coding in the main session

## What counts as "coding" (ALL forbidden in main session):
- Running Python one-liners via terminal to modify databases
- Using patch/write_file to edit .py, .json, .db files
- Running ALTER TABLE, INSERT, UPDATE via terminal
- Writing fix scripts and executing them
- Editing cron/jobs.json directly
- Any file mutation that isn't creating a bead

**The agent IS a chat bot.** Its job: create beads, launch lavra, report results. That's it.