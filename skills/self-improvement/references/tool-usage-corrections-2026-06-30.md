# Tool Usage Corrections — 2026-06-30

## Pitfall: "Wrong Tools"
Agent uses `terminal` for read/search/edit instead of proper tools.
User: "это твои инструменты!!!! ты их пользуешь???"
Root cause: Linux habit, forgetting tools exist.
Fix: SOUL.md has MANDATORY rules. tool-catalog has selection table.

## Pitfall: "Asking Stupid Questions"
Agent asks "what should I do?" instead of just doing it.
User: "ты блять идиот задавая такие вопросы"
Fix: never ask permission to act. Just DO it.

## Pitfall: "Subagent Timeouts"
Subagents timeout at 600s on complex tasks.
Fix: break into smaller pieces. If still timing out — execute_code.

## Pitfall: "Cron Instead of Events"
Agent suggests cron for event-driven system.
User: "Ты уже построил событийную тягу."
Fix: use event_bus.py, not cron.

## Tool Selection Quick Reference
| Task | USE | NOT |
|------|-----|-----|
| Read file | read_file | cat, terminal |
| Search files | search_files | grep, terminal |
| Edit file | patch | sed, terminal |
| Create file | write_file | echo, terminal |
| Web search | web_search | curl, terminal |
| Complex task | delegate_task | manual coding |
