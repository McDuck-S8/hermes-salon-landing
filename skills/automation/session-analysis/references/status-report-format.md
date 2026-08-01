# Structured Status Report Format

User preference: concise, structured, actionable. No fluff. No markdown tables
in terminal (use ASCII box drawing). Russian language.

## Template

```
═══════════════════════════════════════════════
СОСТОЯНИЕ СИСТЕМЫ — [дата]
═══════════════════════════════════════════════

  [Component]:  [STATUS] ([detail])

═══════════════════════════════════════════════
CRON JOBS: [N] всего
═══════════════════════════════════════════════

  Активные и рабочие:
    ✓ [name]  — [schedule], OK

  Активные но с ошибками:
    ✗ [name]  — [error summary]

  Мёртвые/отключённые: [N] штук

═══════════════════════════════════════════════
ОШИБКИ (топ по количеству)
═══════════════════════════════════════════════

  [logfile]:  [N] ошибок
  Корневая проблема: [root cause if known]

═══════════════════════════════════════════════
ЧТО РАБОТАЕТ
═══════════════════════════════════════════════

  ✓ [working thing]

═══════════════════════════════════════════════
ЧТО ДЕЛАТЬ (приоритеты)
═══════════════════════════════════════════════

Приоритет 1: [most urgent]
Приоритет 2: [second]
Приоритет 3: [third]
```

## Data Sources

1. **System health**: `python scripts/self_system.py --status`
2. **Cron jobs**: `cronjob(action='list')` — count enabled, check last_status
3. **Processes**: `tasklist | grep python` (Windows) or `ps aux | grep python`
4. **Goals**: Read from `cache/crystal/goals.json` or boot dump
5. **Errors**: `grep -ci "error" logs/*.log` — rank by count
6. **Boot status**: Check `logs/session_boot.log` tail

## User Preferences

- **Concise**: No paragraphs. Bullet points. ASCII art headers.
- **Honest**: If something is broken, say so. Don't round up "warn" to "ok".
- **Actionable**: End with prioritized next steps, not just diagnosis.
- **Russian**: User communicates in Russian, report in Russian.
- **No manual testing**: Never say "write /ping to check". Verify programmatically.
