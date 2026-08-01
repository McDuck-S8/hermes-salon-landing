# Session Analysis Report Template

Use this template when generating consultation reports from session data.

## Full Report Format

```markdown
## Session Analysis Report
*{date} — {N} sessions analyzed*

### Session 1: {title}
**Source:** {cli|gateway|cron} | **Messages:** {count} | **Duration:** {start} → {end}
**Task:** {one-line description of what the user was doing}
**Status:** {complete|in-progress|blocked|abandoned}
**Artifacts:** {files created, databases, configs}
**Blockers:** {what prevented completion, if any}

→ **Recommendation:** {specific actionable next step}

### Session 2: ...

### Patterns
1. **{pattern name}** — {description of what repeats across sessions}
2. ...

### Systemic Issues
| # | Issue | Severity | First Seen | Times Repeated | Description |
|---|-------|----------|------------|----------------|-------------|
| 1 | {issue} | 🔴 Critical | {date} | {N}x | {what and why} |
| 2 | {issue} | 🟡 Medium | ... | ... | ... |

### Trend (if multiple report runs exist)
| Metric | Run 1 | Run 2 | Run 3 | Δ |
|--------|-------|-------|-------|---|
| Experiences | ... | ... | ... | ... |
| Active sessions | ... | ... | ... | ... |
| Completion rate | ... | ... | ... | ... |
```

## Minimal Report (when nothing new)

If no new sessions or no actionable findings:
```
[SILENT]
```

Do NOT produce a report saying "nothing to report." Just suppress delivery.

## Language

Match the user's language. If user writes in Russian, report in Russian.
If user writes in English, report in English.
