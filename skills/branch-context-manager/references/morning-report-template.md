# Morning Report Template

Use this template when generating morning/evening status reports from branch context files.

## Data Sources

1. `$HERMES_HOME/branches.yaml` — active branches with status
2. `$HERMES_HOME/breadcrumbs.log` — chronological activity log
3. `session_search(sort="newest", limit=5)` — recent sessions for deeper context

## Windows Path Note

On Windows hosts, `~` expansion works in Python (`os.path.expanduser`) but terminal bash may fail with `cd: C:\Users\Asus: No such file or directory`. Use `execute_code` with Python's `open()` or `read_file` tool instead of terminal `cat`.

## Report Format (4 sections)

```markdown
# ☀️ Утренний отчёт — [дата]

## 1. Активные ветки
| Ветка | Статус | Следующий шаг |
|-------|--------|---------------|
| branch-name | status from yaml | next_step from yaml |

## 2. Что было сделано вчера
- [timestamp] — [branch] — [action from breadcrumbs]
- Pull additional context from session_search if breadcrumbs are sparse

## 3. Приоритеты на сегодня
1. [Most urgent — based on next_step fields + unresolved problems]
2. [Second priority]
3. [etc.]

## 4. Проблемы
| Проблема | Серьёзность | Детали |
|----------|-------------|--------|
| issue | 🔴/🟡/🟢 | context |
```

## Rules

- Always read BOTH files before generating report
- Cross-reference breadcrumbs with session_search for richer context
- If breadcrumbs.log has only 1-2 entries, check sessions for more detail
- Sort priorities by urgency: blockers > in-progress > research
- Be concise — no fluff, no explanations of obvious things
- Write in the user's language (match breadcrumbs language)
- If branches.yaml is empty or all branches are closed, report "Нет активных веток"
- If breadcrumbs.log is empty, report "Нет активности вчера" and check sessions anyway
