---
name: compliance_checker
description: "Daily verification of three core autonomy rules: Zero Trust, Passive Income, Iterative Attack. Runs as cron, logs to feedback_store, auto-corrects violations."
trigger: "On schedule (daily 06:00), or when compliance check requested"
usage: compliance_checker
category: self-improvement
---

# Compliance Checker

Verifies three core autonomy rules daily. No reports — only compliance or auto-correction.

## Three Rules

| Rule | Principle | Check |
|------|-----------|-------|
| **Zero Trust** | Все изменения верифицируются субагентом | subagent_verifier runs logged in feedback_store (24h) |
| **Passive Income** | Кроны работают без участия пользователя | Cron runs in 48h + maintenance_scanner recent |
| **Iterative Attack** | Ежедневно ≥1 автономная задача | proactive_doer/skill_usage_analyzer/suggestion_applier tasks today |

## Data Sources

- `feedback_store.db` — verification logs, cron runs, task executions
- `maintenance_reports/` — maintenance_scanner output
- `cache/proactive_doer_tasks.json` — autonomous task queue
- `cron/jobs.json` — enabled job count

## Thresholds

| Rule | Compliant If | Non-Compliant Action |
|------|--------------|----------------------|
| Zero Trust | ≥1 subagent_verifier run in 24h | Queue subagent_verifier task |
| Passive Income | ≥1 cron run in 48h + maintenance_scanner recent | Queue cron restart task |
| Iterative Attack | ≥1 autonomous task today | Queue generated task from suggestions/gaps |

## Auto-Correction

| Rule | Correction | Queue |
|------|------------|-------|
| Zero Trust | `verify_recent_changes` task | `cache/subagent_verifier_tasks.json` |
| Passive Income | `restart_failed_crons` task | `cache/proactive_doer_tasks.json` |
| Iterative Attack | `execute_generated_task` | `cache/proactive_doer_tasks.json` |

## Logging

All checks logged to `feedback_store.db` as `compliance_checker_<rule>` with:
- `compliant: boolean`
- `details: object`
- `action_taken: string|null`

## Cron

```json
{
  "name": "compliance-checker",
  "script": "compliance_checker.py",
  "schedule": "0 6 * * *",  // Daily 06:00
  "enabled": true
}
```

## Verification

```bash
# Syntax
python -m py_compile scripts/compliance_checker.py

# Check only
python scripts/compliance_checker.py --check --json

# Check + auto-correct
python scripts/compliance_checker.py --check --auto-correct --json
```

## Example Output (All Compliant)

```json
{
  "zero_trust": {
    "compliant": true,
    "details": {"verification_logs_24h": 2, "message": "All changes must pass subagent_verifier before survival"},
    "action": null
  },
  "passive_income": {
    "compliant": true,
    "details": {"cron_runs_48h": 1, "maintenance_scanner_recent": true, "message": "Background cron jobs executing autonomously"},
    "action": null
  },
  "iterative_attack": {
    "compliant": true,
    "details": {"new_tasks_today": 0, "proactive_tasks_today": 3, "message": "3 autonomous tasks executed today"},
    "action": null
  }
}
```